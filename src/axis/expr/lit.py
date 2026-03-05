from decimal import Decimal
from types import EllipsisType
from typing import ClassVar, Self

from axis.literals import WildcardType, Wildcard
from axis import syn, dom

class Lit(syn.Expr):
    type Value = dom.Literal | EllipsisType | WildcardType
    value: Value

    _: ClassVar[WildcardType] = Wildcard

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)
