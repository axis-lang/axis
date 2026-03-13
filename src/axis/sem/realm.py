from __future__ import annotations
from typing import Iterable
from protobase import Consed, flux, frozendict
import protomorph as pm

from .context import Context
from .entity import Entity

type Namespaces = frozendict[pm.Anchor, frozenset[pm.Anchor]]


class Realm(pm.SemanticBridgeBase, Consed):

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
    ) -> frozendict[pm.Anchor, frozenset[Context.Contribution]]:
        by_anchors: dict[pm.Anchor, list[Context.Contribution]] = {}
        for contribution in self.all_contributions:
            by_anchors.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in by_anchors.items()
        )

    @flux.property
    def all_anchors(self) -> frozenset[pm.Anchor]:
        return frozenset(self.contributions_by_anchor.keys())

    @flux.property
    def namespaces_by_anchor(self) -> Namespaces:
        namespaces: dict[pm.Anchor, set[pm.Anchor]] = {}
        for anchor in self.all_anchors:
            if (parent := anchor.parent) is not None:
                namespaces.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in namespaces.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[pm.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.contributions_by_anchor.items()
        )

    @property
    def all_entities(self) -> Iterable[Entity]:
        return self.entities_by_anchor.values()

    def __getitem__(self, anchor: pm.Anchor | str) -> Entity:
        if isinstance(anchor, str):
            anchor = pm.Anchor.from_str(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")

        return self.entities_by_anchor[anchor]

    def fields(self, type: pm.Type) -> pm.Struct[str, pm.Type] | None:
        _ = type
        return None

    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        return super().project(type, key)

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        return super().lift(qualifier, result)

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type:
        return super().combine(left, right, op=op)
    


    @flux.method
    def check(self):
        with self:
            for contribution in self.all_contexts:
                contribution.check()
            for contribution in self.all_contributions:
                contribution.check()
            for entity in self.all_entities:
                entity.check()
