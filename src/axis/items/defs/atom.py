from __future__ import annotations

from typing import ClassVar

from protobase import flux, _

from axis import expr, sem, syn

from .base import SymDef, build_extends_fact_contribution


class AtomDef(SymDef):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
    )

    sym: expr.Sym = _

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        contributions: set[sem.Context.Contribution] = {
            sem.Entity.SpecContribution(
                anchor=self.anchor,
                spec_bindings=sem.BindingStruct(),
                origin=self.origin,
                ctx=self,
            )
        }

        fact_contrib = build_extends_fact_contribution(
            self,
            scope_name=self.anchor.name,
            bindings=sem.BindingStruct(),
            extends=self.extends,
            origin=self.origin,
        )
        if fact_contrib is not None:
            contributions.add(fact_contrib)

        return frozenset(contributions)
