from typing import Self

import protomorph as pm

from axis import syn

from .bound_support import build_spec_args, unsupported_bound, val_type_name

class Index(syn.Expr):
    origin: syn.Expr
    indices: syn.Expr # generalmente sera un Tuple (o shape)

    @classmethod
    def build(cls, origin: syn.Expr, indices: syn.Expr) -> Self:
        return cls(origin=origin, indices=indices)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Val:
        origin_val = self.origin.to_bound(scope)
        if isinstance(origin_val, pm.Err):
            return origin_val
        args = build_spec_args(self.indices, scope)
        if isinstance(args, pm.Err):
            return args
        if isinstance(origin_val, pm.Anchor):
            return origin_val.specialize(args)
        return unsupported_bound(
            self,
            f"specialization requires an Anchor base, got {val_type_name(origin_val)}",
        )
