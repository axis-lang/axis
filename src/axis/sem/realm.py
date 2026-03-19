from __future__ import annotations
from typing import Any, Iterable, cast

from protobase import Consed, flux, frozendict
import protomorph as pm

from axis import sem

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

    @property
    def all_context_anchors(self) -> frozenset[pm.Anchor]:
        return frozenset(cast(Any, ctx).anchor for ctx in self.all_contexts)

    @flux.property
    def entity_contributions_by_anchor(
        self,
    ) -> frozendict[pm.Anchor, frozenset[Context.EntityContribution]]:
        grouped: dict[pm.Anchor, list[Context.EntityContribution]] = {}
        for contribution in self.all_contributions:
            if isinstance(contribution, Context.EntityContribution):
                grouped.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in grouped.items()
        )

    @flux.property
    def all_facts(self) -> frozenset[pm.Spec]:
        return frozenset(fact for entity in self.all_entities for fact in entity.facts)

    @flux.property
    def facts_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Spec]]:
        grouped: dict[pm.Anchor, list[pm.Spec]] = {}
        for fact in self.all_facts:
            grouped.setdefault(fact.anchor, []).append(fact)
        return frozendict(
            (anchor, frozenset(facts)) for anchor, facts in grouped.items()
        )

    @flux.property
    def all_clauses(self) -> frozenset[pm.Clause]:
        return frozenset(
            clause for entity in self.all_entities for clause in entity.clauses
        )

    @flux.property
    def clauses_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Clause]]:
        grouped: dict[pm.Anchor, list[pm.Clause]] = {}
        for clause in self.all_clauses:
            grouped.setdefault(clause.head.anchor, []).append(clause)
        return frozendict(
            (anchor, frozenset(clauses)) for anchor, clauses in grouped.items()
        )

    @flux.property
    def namespaces_by_anchor(self) -> Namespaces:
        namespaces: dict[pm.Anchor, set[pm.Anchor]] = {}
        for anchor in self.all_context_anchors:
            if (parent := anchor.parent) is not None:
                namespaces.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in namespaces.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[pm.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.entity_contributions_by_anchor.items()
        )

    @flux.property
    def logic_solver(self):
        return pm.GlobalFixedPointSolver(backend=self)

    @property
    def all_entities(self) -> Iterable[Entity]:
        return self.entities_by_anchor.values()

    def __getitem__(self, anchor: pm.Anchor | str) -> Entity:
        if isinstance(anchor, str):
            anchor = pm.Anchor.from_str(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")

        return self.entities_by_anchor[anchor]

    def layout(self, type: pm.Type) -> pm.Layout | None:
        _ = type
        return None

    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        raise RuntimeError(
            "Semantic layout disabled: Realm.project(...) is temporarily unavailable "
            "while the semantic layout layer is being rebuilt"
        )

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        if isinstance(qualifier, pm.NominalQualifier):
            return pm.nominal_qual(
                qualifier.spec_ref.anchor,
                cast(pm.Const | None, qualifier.spec_ref._args_const()),
                underlying=result,
            )

        raise RuntimeError(
            f"Realm.lift does not support qualifier {type(qualifier).__name__}"
        )

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type:
        raise RuntimeError(
            f"Realm.combine has no semantic rule for {left!r} {op or '?'} {right!r}"
        )

    @flux.method
    def check(self):
        with self:
            for contribution in self.all_contexts:
                contribution.check()
            for contribution in self.all_contributions:
                contribution.check()
            for entity in self.all_entities:
                entity.check()
