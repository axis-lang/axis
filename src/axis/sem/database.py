from __future__ import annotations

from typing import Iterable

from protobase import Inmutable, flux, frozendict

from axis import dom

from .entity import Entity


class Database(Inmutable):
    type EntitiesByRef = frozendict[dom.Anchor, Entity]
    type MembersByScope = frozendict[dom.Anchor, frozendict[str, dom.Ref]]

    entities_by_ref: EntitiesByRef
    members_by_scope: MembersByScope

    @flux.method
    def entity(self, anchor: dom.Anchor) -> Entity | None:
        return self.entities_by_ref.get(anchor)

    def __getitem__(self, item: str | dom.Anchor) -> Entity | None:
        anchor = dom.Anchor.from_str(item) if isinstance(item, str) else item
        return self.entity(anchor)

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
        table.add_column("Spec Buckets", justify="right")
        table.add_column("Overload Buckets", justify="right")
        table.add_column("Deref", justify="right")
        table.add_column("Members", justify="right")

        items = sorted(
            self.entities_by_ref.items(),
            key=lambda item: dom.ref_segments(item[0]),
        )
        for anchor, entity in items:
            members = self.members_by_scope.get(anchor)
            table.add_row(
                str(anchor),
                str(len(entity.spec_by_shape)),
                str(len(entity.overload_by_shape)),
                str(len(entity.impl_by_result)),
                "0" if members is None else str(len(members)),
            )
        return table
