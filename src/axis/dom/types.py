from __future__ import annotations

from typing import ClassVar, cast

from protobase import Missing, MissingType

from axis import dom
from .base import Builtin, Data


class Type(Builtin, abstract=True):
    val_cls: ClassVar[type[dom.Val] | None] = None
    ANCHOR: ClassVar[str]

    @classmethod
    def _type(cls, *args: type | dom.Type) -> dom.Type:
        if args:
            raise TypeError(
                f"{cls.__name__}._type does not accept type arguments when used as a metatype"
            )
        return dom.nominal_type(cls._anchor_path())

    def _metatype(self) -> dom.Type:
        return dom.nominal_type(self._anchor_path(), self._metaspec())

    def wrap(self, data: Data) -> dom.Val:
        val_cls = type(self).val_cls or dom.Const
        return val_cls(type=self, data=data)

    def _metaspec(self) -> dom.Const | None:
        return None

    def _encode(self, data: Data) -> Data:
        return data

    def _decode(self, raw_data: Data) -> Data:
        return raw_data

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
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
            return fields[offset].wrap(data[offset])
        elif isinstance(data, Builtin):
            k = fields.index.keys[offset]
            if k is None:
                raise KeyError(f"Struct has no positional field at offset {offset}")
            return fields[offset].wrap(getattr(data, k))
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")


class StructType(Type):
    "def dom.Struct.Type[..Index] Type : ( attrs: (..Index: Type) )"

    ANCHOR: ClassVar[str] = "dom.Struct.Type"

    meta_attrs: dom.Struct[str, Type]

    def _metaspec(self):
        return dom.struct(
            *self.meta_attrs.map(
                lambda meta_attr: dom.type_of(dom.val(meta_attr)),
            )
        )

    def _decode(self, raw_data: Data) -> Data:
        match raw_data:
            case tuple() as raw_fields:
                if len(raw_fields) != len(self.meta_attrs):
                    raise ValueError(
                        f"Expected {len(self.meta_attrs)} fields, got {len(raw_fields)}"
                    )
                return tuple(
                    field_type._decode(field_raw)
                    for field_type, field_raw in zip(
                        self.meta_attrs.values, raw_fields
                    )
                )
            case _:
                raise TypeError(
                    f"Expected tuple data for StructType, got {type(raw_data)}"
                )

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        return self.meta_attrs


class NominalType(Type):
    """
    def dom.Nominal.Type[..S](spec_ref: Ref.Spec[..S])
    """

    ANCHOR: ClassVar[str] = "dom.Nominal.Type"

    spec_ref: dom.Spec

    def _metaspec(self):
        return self.spec_ref._args_const()

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        introspector = dom.INTROSPECTOR.get(dom.DEFAULT_INTROSPECTOR)
        if introspector is not None:
            return introspector.fields(self)
        return None

    def _fields(self) -> dom.Struct[str, Type] | None:
        return dom.INTROSPECTOR.get().fields(self)

    def _encode(self, data: Data) -> Data:
        fields = self._fields()

        if fields is None:
            return data

        if isinstance(data, Builtin):
            data = tuple(
                getattr(data, k) for k in cast(tuple[str, ...], fields.index.keys)
            )

        elif not isinstance(data, tuple):
            raise ValueError(
                f"Expected tuple data for NominalType with fields, got {type(data)}"
            )

        if len(data) != len(fields):
            raise ValueError(f"Expected {len(fields)} fields, got {len(data)}")

        from .api import _encode

        return cast(
            Data,
            tuple(
                _encode(field_type, field_value)
                for field_type, field_value in zip(fields, data)
            ),
        )

    def _decode(self, raw_data: Data) -> Data:
        fields = self._fields()
        introspector = dom.INTROSPECTOR.get(dom.DEFAULT_INTROSPECTOR)
        if introspector is None:
            raise ValueError(f"Cannot decode {self!r}: no active introspector")

        if self.spec_ref.path == "std.Any":
            return raw_data

        if fields is None:
            if isinstance(raw_data, tuple):
                return introspector.construct(self, raw_data)
            return raw_data

        if not isinstance(raw_data, tuple):
            raise ValueError(
                f"Expected tuple data for NominalType with fields, got {type(raw_data)}"
            )
        if len(raw_data) != len(fields):
            raise ValueError(f"Expected {len(fields)} fields, got {len(raw_data)}")

        from .api import _decode

        decoded_args = tuple(
            _decode(field_type, field_value)
            for field_type, field_value in zip(fields, raw_data)
        )
        return introspector.construct(self, decoded_args)


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

    def _metaspec(self):
        s = self.spec_ref._args_const()
        return dom.struct(
            S=cast(dom.Const, s if s else dom.val(None)),
            U=cast(dom.Const, dom.val(self.underlying._metatype())),
        )

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        raise NotImplementedError("NominalQualifier._dir is not implemented yet")

    def _get(self, data: Data, key: str | int) -> dom.Val:
        raise NotImplementedError("NominalQualifier._get is not implemented yet")

    def _encode(self, data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._encode is not implemented yet")

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._decode is not implemented yet")


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
                    f"use dom.union_type() for automatic flattening"
                )

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("decode for UnionType is not yet supported")
