from __future__ import annotations

from typing import ClassVar

from axis import syn
from protobase import Inmutable


class Mod(syn.SegregatedItem, Inmutable):
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

    path: syn.Expr | None = None

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

    def contribute(self, collector) -> None:
        if self.path is None:
            return
        collector.namespace(self.path, origin=self.path, ctx=self)
        collector.member(self.path, origin=self, ctx=self)

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)
