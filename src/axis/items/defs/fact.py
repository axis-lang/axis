from __future__ import annotations

from typing import ClassVar

from protobase import flux, _

from axis import expr, log, sem, syn

from .base import SymDef, build_extends_fact_contribution, build_spec_bindings


class FactDef(SymDef):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym[..$spec]"),
    )

    sym: expr.Sym = _
    spec: expr.Tuple = _

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        if self.takes:
            log.error("FactDef does not support takes blocks").label(self.takes[0]).throw()
        if self.returns:
            log.error("FactDef does not support returns blocks").label(self.returns[0]).throw()

        contributions: set[sem.Context.Contribution] = set()
        for where in self.where or (None,):
            spec_bindings = build_spec_bindings(self.spec, where)
            contributions.add(
                sem.Entity.PredicateFacet(
                    anchor=self.anchor,
                    spec_bindings=spec_bindings,
                    origin=self.origin,
                    ctx=self,
                )
            )
            fact_contrib = build_extends_fact_contribution(
                self,
                scope_name=self.anchor.name,
                bindings=spec_bindings,
                extends=self.extends,
                origin=self.origin,
            )
            if fact_contrib is not None:
                contributions.add(fact_contrib)

        return frozenset(contributions)
