from decimal import Decimal
from typing import Any, Self
from axis import syn

class Lit(syn.Expr, frozen=True):
    type Value = Decimal | int | str | bool
    value: Value

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)
