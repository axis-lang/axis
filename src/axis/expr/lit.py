from decimal import Decimal
from types import EllipsisType
from typing import ClassVar, Self

from axis.literals import WildcardType, Wildcard
from axis import syn, dom


class Lit(syn.Expr):
    type Value = dom.Literal | EllipsisType | WildcardType

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)

    value: Value

    @property
    def is_wildcard(self) -> bool:
        return self.value is Wildcard

    @property
    def is_ellipsis(self) -> bool:
        return self.value is Ellipsis


#Special -> Wildcard, Ellipsis