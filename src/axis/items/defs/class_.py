from __future__ import annotations

from typing import ClassVar, Optional, cast

from itertools import product
from protobase import flux, slot_cached_property, _

from axis import expr, log, syn, sem

from .base import SymDef, build_param_bindings, build_spec_bindings


class ClassDef(SymDef):
    """
    Class-like definitions. Always emits OverloadContribution.
    """

    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
        syn.Expr.from_str("$sym[..$spec]"),
        syn.Expr.from_str("$sym(..$args)"),
        syn.Expr.from_str("$sym[..$spec](..$args)"),
    )

    sym: expr.Sym = _
    spec: expr.Tuple | None = None
    args: expr.Tuple | None = None

    def __invariant__(self):
        if len(self.returns) > 0:
            log.warn("ClassDef should not have returns").label(self.origin).emit()

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        return frozenset(
            sem.Entity.OverloadContribution(
                anchor=self.anchor,
                spec_bindings=expr.build_binding_struct(self.spec, where),
                param_bindings=expr.build_binding_struct(self.args, takes),
                origin=self.origin,
                ctx=self,
            )
            for where, takes in product(
                self.where or (None,),
                self.takes or (None,),
            )
        )
