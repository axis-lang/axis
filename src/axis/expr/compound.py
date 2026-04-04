from __future__ import annotations

from typing import Any, Self

import protomorph as pm

from axis import log, syn

from .lowering import build_compound_bound


class Compound(syn.Expr):
    components: tuple[syn.Expr, ...]

    @classmethod
    def build(cls, *components: syn.Expr) -> syn.Expr:
        if len(components) == 1:
            return components[0]
        return cls(components=components)

    def __str__(self):
        return " ".join(str(c) for c in self.components)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        return build_compound_bound(self.components, scope)
