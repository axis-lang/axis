from __future__ import annotations

from typing import ClassVar

from axis import syn, sem, val, items
from protobase import cached_property


class Mod(syn.Item, frozen=True):
    """
    Cometido: agrupar semanticamente un conjunto de sub-items.

    el modulo representa un espacio de nombres

    Example:
        mod axis.items:
            ...
    """

    outline_keyword: ClassVar[str] = "mod"
    # grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    pkg: items.Package

    path: syn.Expr
    # uses: tuple[blocks.Use, ...]

    # @property
    # def name(self) -> str:
    #     if isinstance(self.path, expr.Member):
    #         return self.path.as_sym()
    #     elif isinstance(self.path, expr.Sym):
    #         return self.path

    #     raise TypeError(f"Unexpected path type: {type(self.path)}")

    @classmethod
    def build(
        cls,
        kw,
        path: syn.Expr,
        *,
        pkg: items.Package,
        children: tuple[syn.Block, ...],
        parent: syn.SegregatedOutlineNode,
    ):
        # children=children,
        return cls(path=path, parent=parent, pkg=pkg)

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)
