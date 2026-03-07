from __future__ import annotations

from protobase import Consed, flux, frozendict

from axis import dom

from .context import Context
from .entity import Entity


class Realm(Consed, abstract=True):

    @property
    def all_contexts(self) -> tuple[Context, ...]:
        raise NotImplementedError

    @flux.property
    def all_contributions(self) -> frozenset[Context.Contribution]:
        return frozenset(
            contribution
            for ctx in self.all_contexts
            for contribution in ctx.contributions
        )

    @flux.property
    def contributions_by_anchor(
        self,
    ) -> frozendict[dom.Anchor, frozenset[Context.Contribution]]:
        by_anchors: dict[dom.Anchor, list[Context.Contribution]] = {}
        for contribution in self.all_contributions:
            by_anchors.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in by_anchors.items()
        )

    @flux.property
    def all_anchors(self) -> frozenset[dom.Anchor]:
        return frozenset(self.contributions_by_anchor.keys())

    @flux.property
    def members_by_anchor(self) -> frozendict[dom.Anchor, frozenset[dom.Anchor]]:
        members: dict[dom.Anchor, set[dom.Anchor]] = {}
        for anchor in self.all_anchors:
            if (parent := anchor.parent) is not None:
                members.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in members.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[dom.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.contributions_by_anchor.items()
        )

    def __getitem__(self, anchor: dom.Anchor|str) -> Entity:
        if isinstance(anchor, str):
            anchor = dom.Anchor.from_str(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")
        
        return self.entities_by_anchor[anchor]