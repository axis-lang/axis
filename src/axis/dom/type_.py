from __future__ import annotations

from typing import Any, Self

from axis import dom
from .core import Builtin, Literal, Decimal


class Type(Builtin, abstract=True):
    @property
    def type(self) -> Type:
        raise NotImplementedError(
            f"Type.type is not implemented in {self.__class__.__name__}"
        )

    @property
    def as_val(self) -> dom.Const:
        return dom.Const(type=self.type, data=self)

    @staticmethod
    def of_native(native: type | None) -> dom.Type:
        return dom.type_of_native(native)

    @staticmethod
    def of_struct(*positional: Type, **nominal: Type) -> dom.StructType:
        return StructType(fields=dom.Struct.new(*positional, **nominal))

    @staticmethod
    def of_union(*members: Type) -> dom.UnionType:
        return dom.UnionType(members=frozenset(members))


class UnionType(Type):
    members: frozenset[Type]


class StructType(Type):
    """
    (a: Ta, b: Tb, c: Tc)
    """

    fields: dom.Struct[str, Type]



class NominalType(Type):
    ref: dom.Spec

    @property
    def type(self) -> Type:
        return dom.NOMINAL_TYPE

    @classmethod
    def new(cls, ref: dom.Ref | str, **spec) -> Self:
        return cls(ref=dom.Spec.new(ref, **spec))

    # @classmethod
    # def from_anchor_spec(cls, anchor: str, **spec) -> Self:
    #     return cls(ref=dom.Spec.from_anchor_spec)

    @classmethod
    def from_ref(cls, ref: dom.Ref) -> Self:
        return cls(ref=ref.spec)

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls.from_ref(dom.Anchor.from_str(value))


class Qualifier(Type, abstract=True):
    underlying: Type


class NominalQualifier(Qualifier):
    ref: dom.Spec

    @classmethod
    def from_ref(cls, ref: dom.Ref, underlying: Type) -> Self:
        return cls(ref=ref.spec, underlying=underlying)

    @classmethod
    def from_str(cls, value: str, underlying: Type) -> Self:
        return cls.from_ref(dom.Anchor.from_str(value), underlying)
