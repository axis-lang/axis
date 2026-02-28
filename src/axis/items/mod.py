from __future__ import annotations

from typing import ClassVar

from protobase import flux

from axis import dom, syn
from axis.sem import Database

from .item import Item
from .ref import name_from_expr, ref_from_expr, scope_ref_from_item


class Mod(Item):
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

    @flux.property
    def ref(self) -> dom.Ref:
        if self.path is None:
            raise ValueError("Mod requires a path to build its ref")
        scope_ref = scope_ref_from_item(self)
        return ref_from_expr(self.path, scope_ref)

    @flux.property
    def contributions(self) -> frozenset[Database.Contribution]:
        if self.path is None:
            return frozenset()
        scope_ref = scope_ref_from_item(self)
        contributions: list[Database.Contribution] = [
            Database.Namespace(anchor=self.ref, origin=self.path, ctx=self)
        ]
        if scope_ref is not None:
            contributions.append(
                Database.Member(
                    anchor=scope_ref,
                    name=name_from_expr(self.path),
                    target=self.ref,
                    origin=self,
                    ctx=self,
                )
            )
        return frozenset(contributions)

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)
