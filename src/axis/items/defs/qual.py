from __future__ import annotations

from typing import ClassVar, Optional

from protobase import flux, _

from axis import expr, log, syn, sem

from .base import (
    SymDef,
    build_param_bindings,
    build_spec_bindings,
)


class QualDef(SymDef):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym $under"),
        syn.Expr.from_str("$sym[..$spec] $under"),
    )

    spec: Optional[expr.Tuple] = None
    under: syn.Expr = _

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        try:
            contributions: set[sem.Context.Contribution] = set()
            for where in self.where or (None,):
                spec_bindings = build_spec_bindings(self.spec, where)
                for takes in self.takes or (None,):
                    contributions.add(
                        sem.EntityView.QualifierContribution(
                            anchor=self.anchor,
                            spec_bindings=spec_bindings,
                            param_bindings=build_param_bindings(None, takes),
                            underlying_bound_expr=self.under,
                            origin=self.origin,
                            ctx=self,
                        )
                    )

            return frozenset(contributions)
        except Exception:
            log.fatal("Failed to build QualifierContribution").label(self.origin).show()
            raise
