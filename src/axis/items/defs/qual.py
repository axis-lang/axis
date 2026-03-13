from __future__ import annotations

from typing import ClassVar, Optional

from protobase import flux, _

from axis import expr, log, syn, sem

from .base import SymDef, build_spec_bindings


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
            return frozenset(
                sem.Entity.QualContribution(
                    anchor=self.anchor,
                    spec_bindings=build_spec_bindings(self.spec, where),
                    underlying_expr=self.under,
                    origin=self.origin, #takes or where or returns,
                    ctx=self,
                )
                for where in self.where or (None,)
            )
        except Exception:
            log.fatal("Failed to build QualContribution").label(self.origin).show()
            raise

