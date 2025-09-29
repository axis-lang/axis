from typing import Self
from axis import syn

class Trail(syn.Expr, frozen=True):
    'base {suite}'

    base: syn.Expr
    suite: syn.Expr # lambda

    @classmethod
    def build(cls, base: syn.Expr, suite: syn.Expr) -> Self:
        return cls(base=base, suite=suite)
