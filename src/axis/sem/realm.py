from __future__ import annotations
from typing import Iterable
from protobase import Consed, flux, frozendict

from axis import dom

from .context import Context
from .entity import Entity

type Namespaces = frozendict[dom.Anchor, frozenset[dom.Anchor]]

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
    def namespaces_by_anchor(self) -> Namespaces:
        namespaces: dict[dom.Anchor, set[dom.Anchor]] = {}
        for anchor in self.all_anchors:
            if (parent := anchor.parent) is not None:
                namespaces.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in namespaces.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[dom.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.contributions_by_anchor.items()
        )

    @property
    def all_entities(self) -> Iterable[Entity]:
        return self.entities_by_anchor.values()

    def __getitem__(self, anchor: dom.Anchor|str) -> Entity:
        if isinstance(anchor, str):
            anchor = dom.Anchor.from_str(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")
        
        return self.entities_by_anchor[anchor]
    


    @flux.method
    def check(self):
        for contribution in self.all_contexts:
            contribution.check()
        for contribution in self.all_contributions:
            contribution.check()
        for entity in self.all_entities:
            entity.check()