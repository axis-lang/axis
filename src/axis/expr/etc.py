from decimal import Decimal
from typing import Any, Literal, Self
from axis import syn

class Etc(syn.Expr, frozen=True):
    '..expr'
    expr: syn.Expr

    @classmethod
    def build(cls, op: Literal['..'], expr: syn.Expr) -> Self:
        return cls(expr=expr)
