from typing import Self

from axis import syn

class Index(syn.Expr):
    origin: syn.Expr
    indices: syn.Expr # generalmente sera un Tuple (o shape)

    @classmethod
    def build(cls, origin: syn.Expr, indices: syn.Expr) -> Self:
        return cls(origin=origin, indices=indices)
