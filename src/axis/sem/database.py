from __future__ import annotations

from typing import Iterable

from protobase import Consed, Inmutable, frozendict

from axis import dom, syn

from .entity import Entity


class Database(Inmutable):
    type EntitiesByRef = frozendict[dom.Ref, Entity]
    type MembersByScope = frozendict[dom.Ref, frozendict[str, dom.Ref]]

    entities_by_ref: EntitiesByRef
    members_by_scope: MembersByScope

    def specialize(self, ref: dom.Ref) -> Entity.View | None:
        base = self.entities_by_ref.get(ref)
        if base is None:
            ref_segments = dom.ref_segments(ref)
            base = next(
                (
                    entity
                    for candidate, entity in self.entities_by_ref.items()
                    if dom.ref_segments(candidate) == ref_segments
                ),
                None,
            )
        if base is None:
            return None
        return base.view(ref)

    class Contribution(Consed, abstract=True):
        anchor: dom.Ref
        origin: syn.Node
        ctx: syn.Item

    class Namespace(Contribution):
        ...

    class Member(Contribution):
        name: str
        target: dom.Ref

    class Overload(Contribution):
        takes_shape: dom.Tuple[str, syn.Expr]
        where_shape: dom.Tuple[str, syn.Expr] | None

    class Returns(Contribution):
        takes_shape: dom.Tuple[str, syn.Expr] | None
        where_shape: dom.Tuple[str, syn.Expr] | None
        returns_shape: dom.Tuple[str, syn.Expr]

    class Constraint(Contribution):
        predicate: syn.Node

    class Fact(Contribution):
        args: tuple[syn.Expr, ...]

    @classmethod
    def from_contributions(
        cls, contributions: Iterable["Database.Contribution"]
    ) -> "Database":
        entities: dict[dom.Ref, list[Database.Contribution]] = {}
        members_by_scope: dict[dom.Ref, dict[str, dom.Ref]] = {}

        for contribution in contributions:
            anchor = contribution.anchor
            entities.setdefault(anchor, []).append(contribution)
            if isinstance(contribution, Database.Member):
                members_by_scope.setdefault(anchor, {})[contribution.name] = (
                    contribution.target
                )

        entities_by_ref = {
            anchor: Entity.from_contributions(anchor, contribs)
            for anchor, contribs in entities.items()
        }
        return Database(
            entities_by_ref=frozendict(entities_by_ref),
            members_by_scope=frozendict(
                {
                    scope: frozendict(members)
                    for scope, members in members_by_scope.items()
                }
            ),
        )
