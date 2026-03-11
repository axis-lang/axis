from __future__ import annotations

from typing import ClassVar, Self, TYPE_CHECKING, cast

from protobase import Missing, MissingType

from axis import dom
from .core import Builtin, Data

if TYPE_CHECKING:
    from .struct import Struct


class Type(Builtin, abstract=True):
    ANCHOR: ClassVar[str]

    def __repr__(self):
        anchor = getattr(self, "ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return self.__class__.__name__

    @property
    def as_val(self) -> dom.Const:
        return dom.Const(type=self.__type__, data=self.__data__)

    def _axis_dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        """Return the field map for this type, or None if opaque.

        Subclasses override to expose their internal structure.
        The base implementation returns None (opaque).
        """
        return None

    def _axis_get(self, data: Data, key: str | int) -> dom.Val:
        """Access a sub-value by key using cremallera decomposition.

        The type side (self) tells us how to split the data side.
        Requires _axis_dir() to return a Struct (not None).
        """
        fields = self._axis_dir(data)
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
    "dom.Type.Union[..T]"
    ANCHOR: ClassVar[str] = "dom.Type.Union"

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

    @property
    def __type__(self) -> Type:
        return dom._nominal_type("dom.Type.Union")


class StructType(Type):
    "def dom.Type.Struct[..Index] Type : ( fields: (..Index: Type) )"
    ANCHOR: ClassVar[str] = "dom.Type.Struct"

    fields: dom.Struct[str, Type]

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Type.Struct", dom._literal_struct(*self.fields.index.keys)
        )

    def _axis_dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        return self.fields


class NominalType(Type):
    """
    def dom.Type.Nominal[..S](spec_ref: Ref.Spec[..S])
    """
    ANCHOR: ClassVar[str] = "dom.Type.Nominal"

    spec_ref: dom.Spec

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Type.Nominal",
            self.spec_ref.specialization
            # dom._struct(
            #     spec_ref=self.spec_ref.type.as_val,
            # ),
        )
    
    def __repr__(self):
        return repr(self.spec_ref)

    @property
    def __rich__(self):
        return self.spec_ref.__rich__


    def _axis_dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        introspector = dom.INTROSPECTOR.get(None)
        if introspector is not None:
            return introspector.fields(self)
        return None

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

    def __repr__(self):
        return f"{self.spec_ref!r} {self.underlying!r}"
    
    # def __rich__(self):
    #     raise NotImplementedError("NominalQualifier does not support __rich__; Use repl() instead")

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Qual.Nominal",
            dom._struct(
                S=cast(dom.Pure | dom.Var, dom.val(self.spec_ref.type)),
                U=cast(dom.Pure | dom.Var, dom.val(self.underlying)),
            ),
        )
