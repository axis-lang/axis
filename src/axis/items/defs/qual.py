from __future__ import annotations

from typing import ClassVar, Optional

from protobase import flux

from axis import expr, syn
from axis.sem import Context

from .base import Def


class QualDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym $target"),
        syn.Expr.from_str("$sym[..$spec] $target"),
    )

    sym: expr.Sym | None = None
    spec: Optional[expr.Tuple] = None
    target: syn.Expr | None = None

    @flux.property
    def contributions(self) -> frozenset[Context.Contribution]:
        return frozenset()
