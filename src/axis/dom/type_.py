from __future__ import annotations

from typing import ClassVar, cast

from protobase import Missing, MissingType

from axis import dom
from .core import Builtin, Data


class Type(Builtin, abstract=True):
    ANCHOR: ClassVar[str]

    @classmethod
    def _type(cls, *args: type | dom.Type) -> dom.Type:
        if args:
            raise TypeError(
                f"{cls.__name__}._type does not accept type arguments when used as a metatype"
            )
        return dom._nominal_type(cls._anchor_path())

    def _metaspec(self) -> dom.Const | None:
        return None

    def _metatype(self) -> dom.Type:
        return dom._nominal_type(type(self)._anchor_path(), self._metaspec())

    @property
    def __type__(self) -> dom.Type:
        return self._metatype()

    def __repr__(self):
        anchor = getattr(self, "ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return self.__class__.__name__

    @property
    def as_val(self) -> dom.Const:
        return dom.Const(type=self._metatype(), data=self)

    def _decode(self, raw_data: Data) -> Data:
        return raw_data

    def _dir(
        self, data: Data | MissingType = Missing
    ) -> dom.Struct[str, Type] | None:
        """Return the field map for this type, or None if opaque.

        Subclasses override to expose their internal structure.
        The base implementation returns None (opaque).
        """
        return None

    def _get(self, data: Data, key: str | int) -> dom.Val:
        """Access a sub-value by key using cremallera decomposition.

        The type side (self) tells us how to split the data side.
        Requires _dir() to return a Struct (not None).
        """
        fields = self._dir(data)
        if fields is None:
            raise KeyError(f"No member {key!r} on opaque type {type(self).__name__}")

        if isinstance(key, str):
            offset = fields.index.get(key)
        elif isinstance(key, int):
            offset = key
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

        if isinstance(data, tuple):
            return dom.Const(type=fields[offset], data=data[offset])
        elif isinstance(data, Builtin):
            k = fields.index.keys[offset]
            if k is None:
                raise KeyError(f"Struct has no positional field at offset {offset}")
            return dom.Const(type=fields[offset], data=getattr(data, k))
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")


class UnionType(Type):
    "dom.Union[..T].Type"

    ANCHOR: ClassVar[str] = "dom.Union.Type"

    types: frozenset[Type]

    def __invariants__(self) -> None:
        if not self.types:
            raise TypeError("UnionType.types must not be empty")
        for t in self.types:
            if isinstance(t, UnionType):
                raise TypeError(
                    f"UnionType.types must not contain nested UnionTypes; "
                    f"use dom._union_type() for automatic flattening"
                )

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("decode for UnionType is not yet supported")


class StructType(Type):
    "def dom.Struct.Type[..Index] Type : ( fields: (..Index: Type) )"

    ANCHOR: ClassVar[str] = "dom.Struct.Type"

    fields: dom.Struct[str, Type]

    def _metaspec(self) -> dom.Const | None:
        mapped = self.fields.map(
            lambda field_type: cast(dom.Pure | dom.Var, dom.type_of(dom.val(field_type)))
        )
        positional = [
            value
            for key, value in zip(mapped.index.keys, mapped.values)
            if key is None
        ]
        nominal = {
            key: value
            for key, value in zip(mapped.index.keys, mapped.values)
            if key is not None
        }
        return dom._struct(*positional, **nominal)

    def _dir(
        self, data: Data | MissingType = Missing
    ) -> dom.Struct[str, Type] | None:
        return self.fields

    def _decode(self, raw_data: Data) -> Data:
        if not isinstance(raw_data, tuple):
            return raw_data
        return tuple(
            field_type._decode(field_raw)
            for field_type, field_raw in zip(self.fields.values, raw_data)
        )


class NominalType(Type):
    """
    def dom.Nominal.Type[..S](spec_ref: Ref.Spec[..S])
    """

    ANCHOR: ClassVar[str] = "dom.Nominal.Type"

    spec_ref: dom.Spec

    def _metaspec(self) -> dom.Const | None:
        return self.spec_ref._metaspec()

    def __repr__(self):
        return repr(self.spec_ref)

    @property
    def __rich__(self):
        return self.spec_ref.__rich__

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        introspector = dom.INTROSPECTOR.get(dom.DEFAULT_INTROSPECTOR)
        if introspector is not None:
            return introspector.fields(self)
        return None

    def _decode(self, raw_data: Data) -> Data:
        if not isinstance(raw_data, tuple):
            return raw_data

        anchor_path = ".".join(self.spec_ref.anchor.data)
        if anchor_path == "dom.Nominal.Type":
            if len(raw_data) != 1:
                return raw_data

            specialization = self.spec_ref.specialization
            spec_type = dom.SpecType(
                anchor=dom.AnchorType(),
                spec=specialization.type if specialization is not None else None,
            )
            spec_ref = spec_type._decode(raw_data[0])
            if isinstance(spec_ref, dom.Spec):
                return cast(Data, dom.NominalType(spec_ref=spec_ref))
            return raw_data

        introspector = dom.INTROSPECTOR.get(dom.DEFAULT_INTROSPECTOR)
        if introspector is None:
            return raw_data

        fields = introspector.fields(self)
        builtin_cls = introspector.class_for(self)
        if fields is None or builtin_cls is None:
            return raw_data

        attrs: dict[str, Data] = {}
        for key, field_type, field_raw in zip(fields.index.keys, fields.values, raw_data):
            if key is None:
                continue
            attrs[key] = field_type._decode(field_raw)
        return cast(Data, builtin_cls(**attrs))


class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "dom.Qual"

    underlying: Type


class NominalQualifier(Qualifier):
    """
    def dom.Qual.Nominal[..S, U](..super, spec_ref: Ref.Spec[..S])
    extends dom.Qual[U]
    """

    ANCHOR: ClassVar[str] = "dom.Qual.Nominal"

    spec_ref: dom.Spec

    def _metaspec(self) -> dom.Const | None:
        spec = self.spec_ref._metaspec() or dom._literal(None)
        underlying = dom.type_of(dom.val(self.underlying))
        return dom._struct(
            S=cast(dom.Pure | dom.Var, spec),
            U=cast(dom.Pure | dom.Var, underlying),
        )

    def __repr__(self):
        return f"{self.spec_ref!r} {self.underlying!r}"

    # def __rich__(self):
    #     raise NotImplementedError("NominalQualifier does not support __rich__; Use repl() instead")

    def _decode(self, raw_data: Data) -> Data:
        return self.underlying._decode(raw_data)
