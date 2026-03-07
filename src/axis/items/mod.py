from __future__ import annotations

from typing import ClassVar, cast, Literal, Self

from protobase import flux, _, slot_cached_property, frozendict

from axis import dom, expr, syn, sem, log

# from axis.sem import Entity, Scope

from .blocks import Use
from .item import Item
#from .scopes import parent_scope


class Mod(Item):
    outline_keyword: ClassVar[str] = "mod"


    path: syn.Expr = _
    uses: tuple[Use, ...] = ()

    @classmethod
    def build(
        cls: type[Self],
        kw: Literal["mod", "unit"],
        path: syn.Expr,
        *,
        children: syn.OutlineNode.Children,
        **kwargs,
    ):
        uses = tuple(child for child in children if isinstance(child, Use))
        return cls(path=path, uses=uses, **kwargs)

    @slot_cached_property
    def anchor(self):
        anchor = self.parent.anchor if self.parent is not None else None
        return expr.as_anchor(self.path, anchor)

    @flux.property
    def ref(self) -> dom.Anchor:
        if self.path is None:
            raise ValueError("Mod requires a path to build its ref")
        scope_ref = self.anchor
        ref = expr.to_spec_ref(self.path, scope_ref)
        if ref is None:
            raise ValueError("Mod requires a path to build its ref")
        if isinstance(ref, dom.Spec):
            raise ValueError("Module ref cannot be specialized")
        return cast(dom.Anchor, ref)

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        # contributions: list[sem.Entity.Contribution] = []
        # contributions.append(
        #     sem.Entity.Member(
        #         anchor=self.anchor,
        #         name=expr.to_name(self.path),
        #         target=self.ref,
        #         origin=self.path,
        #         ctx=self,
        #     )
        # )
        return frozenset()

    @slot_cached_property
    def name(self) -> str | None:
        return expr.name_of(self.path) if self.path is not None else None

    def _build_scope(self, scope_builder: sem.Scope.Builder) -> None:
        namespaces = self.realm.namespaces_by_anchor
        for resolved_target in namespaces.get(self.anchor, ()):
            scope_builder.define(resolved_target.name, resolved_target, origin=self)
        for use in self.uses:
            use._contribute_to_scope(scope_builder, namespaces)

    # @flux.property
    # def scope(self) -> sem.Scope:
    #     scope_name = expr.name_of(self.path) if self.path is not None else None
    #     builder = sem.Scope.Builder(name=scope_name, parent=parent_scope(self))
    #     realm = self.realm
    #     if realm is None:
    #         return builder.build()

    #     members_by_anchor = realm.namespaces_by_anchor
    #     for use in self.uses:
    #         for name, ref in use.entries:
    #             if isinstance(name, expr.Lit) and name.value is Ellipsis:
    #                 if ref is None:
    #                     continue
    #                 for member_name, member_ref in _namespace_members(
    #                     members_by_anchor, ref.anchor
    #                 ).items():
    #                     sym = expr.Sym(name=member_name).with_span_of(name)
    #                     builder.define(sym, cast(dom.Val, member_ref))
    #                 continue
    #             if ref is None:
    #                 continue
    #             builder.define(cast(expr.Sym, name), cast(dom.Val, ref))

    #     if self.path is not None:
    #         for name, ref in _namespace_members(members_by_anchor, self.ref).items():
    #             builder.define(expr.Sym(name=name), cast(dom.Val, ref))

    #     return builder.build()

    # class Binding(sem.Binding):
    #     item: Mod

    #     @cached_property
    #     def ref(self):
    #         return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)


# def _namespace_members(
#     members_by_anchor: frozendict[dom.Anchor, frozenset[dom.Anchor]],
#     scope_ref: dom.Anchor,
# ) -> dict[str, dom.Ref]:
#     members: dict[str, dom.Ref] = {}
#     for anchor in members_by_anchor.get(scope_ref, frozenset()):
#         name = anchor.data[-1]
#         members.setdefault(name, anchor)
#     return members
