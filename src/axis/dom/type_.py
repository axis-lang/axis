from __future__ import annotations

from typing import ClassVar, Self

from axis import dom
from .core import Builtin, Data


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
                spec_ref=dom.type_of(self.spec_ref),
            ),
        )

    @classmethod
    def from_ref(cls, ref: dom.Ref) -> Self:
        return cls(spec_ref=ref.spec)

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(spec_ref=dom._spec_ref(value))


class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "dom.Type.Qual"

    underlying: Type


class NominalQualifier(Qualifier):
    ANCHOR: ClassVar[str] = "dom.Type.Qual.Nominal"

    ref_spec: dom.SpecType

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Type.Qual.Nominal",
            dom._struct(
                ref_spec=self.ref_spec.as_val,
                underlying=self.underlying.as_val,
            ),
        )

    @classmethod
    def from_ref(cls, ref: dom.Ref, underlying: Type) -> Self:
        return cls(ref_spec=ref.spec.type, underlying=underlying)

    @classmethod
    def from_str(cls, value: str, underlying: Type) -> Self:
        return cls.from_ref(dom.Anchor.from_str(value), underlying)
