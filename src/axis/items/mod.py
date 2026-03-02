from __future__ import annotations

from typing import ClassVar, cast

from protobase import flux

from axis import dom, expr, syn
from axis.sem import Entity, Scope

from .blocks import Use
from .item import Item
from .ref import name_from_expr, ref_from_expr, scope_ref_from_item
from .scopes import parent_scope


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
    uses: tuple[Use, ...] = ()

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
        uses = tuple(child for child in children if isinstance(child, Use))
        return cls(path=path, uses=uses, **kwargs)

    @flux.property
    def ref(self) -> dom.Anchor:
        if self.path is None:
            raise ValueError("Mod requires a path to build its ref")
        scope_ref = scope_ref_from_item(self)
        ref = ref_from_expr(self.path, scope_ref)
        if isinstance(ref, dom.Spec):
            raise ValueError("Module ref cannot be specialized")
        return cast(dom.Anchor, ref)

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        if self.path is None:
            return frozenset()
        scope_ref = scope_ref_from_item(self)
        contributions: list[Entity.Contribution] = []
        if scope_ref is not None:
            contributions.append(
                Entity.Member(
                    anchor=scope_ref,
                    name=name_from_expr(self.path),
                    target=self.ref,
                    origin=self.path,
                    ctx=self,
                )
            )
        return frozenset(contributions)

    @flux.property
    def scope(self) -> Scope:
        scope_name = name_from_expr(self.path) if self.path is not None else None
        builder = Scope.Builder(name=scope_name, parent=parent_scope(self))
        realm = self.realm
        if realm is None:
            return builder.build()

        db = realm.database
        for use in self.uses:
            for name, ref in use.entries:
                if isinstance(name, expr.Lit) and name.value is Ellipsis:
                    for member_name, member_ref in _namespace_members(
                        db, ref.anchor
                    ).items():
                        sym = expr.Sym(name=member_name).with_span_of(name)
                        builder.define(sym, member_ref)
                    continue
                builder.define(cast(expr.Sym, name), ref)

        if self.path is not None:
            for name, ref in _namespace_members(db, self.ref).items():
                builder.define(expr.Sym(name=name), ref)

        return builder.build()

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)


def _namespace_members(db, scope_ref: dom.Anchor) -> dict[str, dom.Ref]:
    members: dict[str, dom.Ref] = dict(db.members_by_scope.get(scope_ref, {}))
    for ref in db.entities_by_ref:
        parent = ref.parent
        if parent is not None and parent == scope_ref:
            data = cast(dom.Anchor.Data, ref.data)
            name = data.member
            members.setdefault(name, ref)
    return members
