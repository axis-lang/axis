from __future__ import annotations

from typing import ClassVar, Self, TYPE_CHECKING

from protobase import Missing, MissingType

from axis import dom
from .core import Builtin, Data

if TYPE_CHECKING:
    from .struct import Struct


class Type(Builtin, abstract=True):
    ANCHOR: ClassVar[str]

    @property
    def __type__(self) -> Type:
        raise NotImplementedError(
            f"{self.__class__.__name__}.__type__ is not implemented"
        )

    @property
    def __data__(self) -> Data:
        return self

    @property
    def as_val(self) -> dom.Const:
        return dom.Const(type=self.__type__, data=self.__data__)

    def dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        """Return the field map for this type, or None if opaque.

        Subclasses override to expose their internal structure.
        The base implementation returns None (opaque).
        """
        return None

    def get(self, data: Data, key: str | int) -> dom.Val:
        """Access a sub-value by key using cremallera decomposition.

        The type side (self) tells us how to split the data side.
        Requires dir() to return a Struct (not None).
        """
        fields = self.dir(data)
        if fields is None:
            raise KeyError(f"No member {key!r} on {type(self).__name__} (opaque)")
        if isinstance(key, str):
            offset = fields.index.get(key)
        elif isinstance(key, int):
            offset = key
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")
        if not isinstance(data, tuple):
            raise TypeError(f"Expected tuple data for dir/get, got {type(data).__name__}")
        return dom.Const(type=fields[offset], data=data[offset])


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
    "dom.Type.Struct[..Index] Type -> ( fields: (..I: Type) )"
    ANCHOR: ClassVar[str] = "dom.Type.Struct"

    fields: dom.Struct[str, Type]

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Type.Struct", dom._literal_struct(*self.fields.index.keys)
        )

    def dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        return self.fields


class NominalType(Type):
    """
    val nominal_type: dom.Type.Nominal[SpecType] = (spec_ref: SpecData)
    """
    ANCHOR: ClassVar[str] = "dom.Type.Nominal"

    spec_ref: dom.Spec

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Type.Nominal",
            dom._struct(
                spec_ref=self.spec_ref.type.as_val,
            ),
        )

    def dir(self, data: Data | MissingType = Missing) -> Struct[str, Type] | None:
        introspector = dom.INTROSPECTOR.get(None)
        if introspector is not None:
            return introspector.fields(self)
        return None

class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "dom.Qual"

    underlying: Type


class NominalQualifier(Qualifier):
    ANCHOR: ClassVar[str] = "dom.Qual.Nominal"

    spec_ref: dom.Spec

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Qual.Nominal",
            dom._struct(
                spec_ref=self.spec_ref.type.as_val,
                underlying=self.underlying.as_val,
            ),
        )

