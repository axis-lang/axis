from __future__ import annotations

from typing import Any, Self

from axis import dom
from .core import Builtin, Literal, Decimal


class Type(Builtin, abstract=True):
    # @staticmethod
    # def of_native(t: type) -> Type:
    #     return dom.type_of_native(t)

    @staticmethod
    def of_literal(value: Literal):
        return dom.type_of_literal(value)


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


class NominalType(Type):
    ref: dom.Spec

    @classmethod
    def new(cls, ref: dom.Ref|str, **spec) -> Self:
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


class StructType(Type):
    """
    (a: Whole, b: Whole, c: Whole)
    """

    fields: dom.Struct[str, Type]

    @staticmethod
    def new(*positional: Type, **nominal: Type) -> StructType:
        return StructType(fields=dom.Struct.new(*positional, **nominal))


class UnionType(Type):
    members: tuple[Type, ...]

