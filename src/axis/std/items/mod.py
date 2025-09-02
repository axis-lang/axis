from __future__ import annotations

from typing import ClassVar, Optional

from axis.core import src, syn, log, sem, val


class Mod(syn.Item):
    """
    Cometido: agrupar semanticamente un conjunto de sub-items.

    el modulo representa un espacio de nombres

    Example:
        mod axis.items:
            ...
    """

    keyword: ClassVar[str] = "mod"
    grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    path: syn.Expr

    @classmethod
    def build(cls, kw, path: syn.Expr, *, children=tuple[syn.Block]):
        return cls(path=path, children=children)

    def bind(self, parent: sem.Binding) -> sem.Binding:
        ref = val.Ref.from_expr(self.path, base_ref=parent.ref)
        return sem.Binding(
            parent=parent,
            ref=ref,
            item=self,
        )

