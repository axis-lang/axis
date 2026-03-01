from decimal import Decimal
from types import EllipsisType
from typing import ClassVar, Self

from axis.literals import Wildcard, WILDCARD
from axis import syn

class Lit(syn.Expr):
    type Value = Decimal | int | str | bool | EllipsisType | None | Wildcard
    value: Value

    _: ClassVar[Wildcard] = WILDCARD

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)
