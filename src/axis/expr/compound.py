from typing import Self

import protomorph as pm

from axis import syn

from .bound_support import build_compound_bound


class Compound(syn.Expr):
    components: tuple[syn.Expr, ...]

    @classmethod
    def build(cls, *components: syn.Expr) -> syn.Expr:
        if len(components) == 1:
            return components[0]
        return cls(components=components)

    def __str__(self):
        return " ".join(str(c) for c in self.components)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Val:
        return build_compound_bound(self.components, scope)
