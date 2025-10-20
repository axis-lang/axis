from __future__ import annotations

from typing import ClassVar

from axis import syn, items


class Mod(syn.SegregatedItem, frozen=True):
    """
    Cometido: agrupar semanticamente un conjunto de sub-items.

    el modulo representa un espacio de nombres

    Example:
        mod axis.items:
            ...
    """

    outline_keyword: ClassVar[str] = "mod"
    # grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    #pkg: items.Package

    path: syn.Expr

    @classmethod
    def build(
        cls,
        kw,
        path: syn.Expr,
        *,
        #pkg: items.Package,
        children: syn.OutlineNode.Children,
        #parent: syn.SegregatedOutlineNode,
        **kwargs
    ):
        # procesa imports desde children
        return cls(path=path, **kwargs)

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)
