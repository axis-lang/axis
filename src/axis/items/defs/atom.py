from __future__ import annotations

from typing import ClassVar

from protobase import flux, _

from axis import expr, sem, syn

from .base import SymDef


class AtomDef(SymDef):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
    )

    sym: expr.Sym = _

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        return frozenset({
            sem.Entity.SpecContribution(
                anchor=self.anchor,
                spec_bindings=sem.BindingStruct(),
                origin=self.origin,
                ctx=self,
            )
        })
