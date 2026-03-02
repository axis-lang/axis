from __future__ import annotations

from typing import Iterable

from protobase import Inmutable, frozendict

from axis import dom

from .entity import Entity


class Database(Inmutable):
    type EntitiesByRef = frozendict[dom.Anchor, Entity]
    type MembersByScope = frozendict[dom.Anchor, frozendict[str, dom.Ref]]

    entities_by_ref: EntitiesByRef
    members_by_scope: MembersByScope

    def specialize(self, ref: dom.Ref) -> Entity.View | None:
        anchor = ref.anchor
        base = self.entities_by_ref.get(anchor)
        if base is None:
            ref_segments = dom.ref_segments(anchor)
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

    @classmethod
    def from_contributions(
        cls, contributions: Iterable["Entity.Contribution"]
    ) -> "Database":
        entities: dict[dom.Anchor, list[Entity.Contribution]] = {}
        members_by_scope: dict[dom.Anchor, dict[str, dom.Ref]] = {}

        for contribution in contributions:
            anchor = contribution.anchor
            entities.setdefault(anchor, []).append(contribution)
            if isinstance(contribution, Entity.Member):
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

    def __rich__(self):
        from rich.table import Table

        table = Table(title="Database")
        table.add_column("Anchor")
        table.add_column("Specs", justify="right")
        table.add_column("Overloads", justify="right")
        table.add_column("Impls", justify="right")
        table.add_column("Members", justify="right")

        items = sorted(
            self.entities_by_ref.items(),
            key=lambda item: dom.ref_segments(item[0]),
        )
        for anchor, entity in items:
            members = self.members_by_scope.get(anchor)
            table.add_row(
                str(anchor),
                str(len(entity.spec_buckets)),
                str(len(entity.overloads)),
                str(len(entity.implementations)),
                "0" if members is None else str(len(members)),
            )
        return table
