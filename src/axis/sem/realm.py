from __future__ import annotations
from typing import Any, Iterable, cast

from protobase import Consed, flux, frozendict
import protomorph
from protomorph import reasoning as urs

from axis import sem

from .context import Context
from .entity import Entity

type Namespaces = frozendict[protomorph.Anchor, frozenset[protomorph.Anchor]]


class Realm(protomorph.Realm, Consed):

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
    ) -> frozendict[protomorph.Anchor, frozenset[Context.Contribution]]:
        by_anchors: dict[protomorph.Anchor, list[Context.Contribution]] = {}
        for contribution in self.all_contributions:
            by_anchors.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in by_anchors.items()
        )

    @flux.property
    def all_anchors(self) -> frozenset[protomorph.Anchor]:
        return frozenset(self.contributions_by_anchor.keys())

    @property
    def all_context_anchors(self) -> frozenset[protomorph.Anchor]:
        return frozenset(cast(Any, ctx).anchor for ctx in self.all_contexts)

    @flux.property
    def entity_contributions_by_anchor(
        self,
    ) -> frozendict[protomorph.Anchor, frozenset[Context.EntityContribution]]:
        grouped: dict[protomorph.Anchor, list[Context.EntityContribution]] = {}
        for contribution in self.all_contributions:
            if isinstance(contribution, Context.EntityContribution):
                grouped.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in grouped.items()
        )

    @flux.property
    def all_facts(self) -> frozenset[protomorph.Spec]:
        return frozenset(fact for entity in self.all_entities for fact in entity.facts)

    @flux.property
    def fact_index(self) -> frozendict[protomorph.Anchor, frozenset[protomorph.Spec]]:
        grouped: dict[protomorph.Anchor, list[protomorph.Spec]] = {}
        for fact in self.all_facts:
            grouped.setdefault(fact.anchor, []).append(fact)
        return frozendict(
            (anchor, frozenset(facts)) for anchor, facts in grouped.items()
        )

    @flux.property
    def all_rules(self) -> frozenset[urs.Rule]:
        return frozenset(
            rule for entity in self.all_entities for rule in entity.rules
        )

    @flux.property
    def rule_index(self) -> frozendict[protomorph.Anchor, frozenset[urs.Rule]]:
        grouped: dict[protomorph.Anchor, list[urs.Rule]] = {}
        for rule in self.all_rules:
            grouped.setdefault(rule.head.anchor, []).append(rule)
        return frozendict(
            (anchor, frozenset(rules)) for anchor, rules in grouped.items()
        )

    @flux.property
    def namespaces_by_anchor(self) -> Namespaces:
        namespaces: dict[protomorph.Anchor, set[protomorph.Anchor]] = {}
        for anchor in self.all_context_anchors:
            if (parent := anchor.parent) is not None:
                namespaces.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in namespaces.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[protomorph.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.entity_contributions_by_anchor.items()
        )

    @property
    def anchors(self) -> frozenset[protomorph.Anchor]:
        return frozenset((*self.fact_index.keys(), *self.rule_index.keys()))

    def facts_by_anchor(self, anchor: protomorph.Anchor) -> tuple[protomorph.Spec, ...]:
        return tuple(self.fact_index.get(anchor, frozenset()))

    def rules_for_anchor(self, anchor: protomorph.Anchor) -> tuple[urs.Rule, ...]:
        return tuple(self.rule_index.get(anchor, frozenset()))

    def is_coinductive_anchor(self, anchor: protomorph.Anchor) -> bool:
        _ = anchor
        return False

    def schema_for(self, spec: protomorph.Spec):
        return protomorph.NATIVE_REALM.schema_for(spec)

    def val_is_leaf(self, meta: protomorph.Type, data: Any) -> bool:
        return protomorph.NATIVE_REALM.val_is_leaf(meta, data)

    def val_children(self, meta: protomorph.Type, data: Any) -> tuple[Any, ...]:
        return protomorph.NATIVE_REALM.val_children(meta, data)

    def val_reconstruct(self, meta: protomorph.Type, children: tuple[Any, ...]) -> Any:
        return protomorph.NATIVE_REALM.val_reconstruct(meta, children)

    def eval_logic_op(
        self,
        operator: protomorph.Placeholder,
        *,
        goal: protomorph.Spec,
        session: urs.Session,
    ) -> urs.LogicOpStep | None:
        _ = (operator, goal, session)
        return None

    @property
    def all_entities(self) -> Iterable[Entity]:
        return self.entities_by_anchor.values()

    def __getitem__(self, anchor: protomorph.Anchor | str) -> Entity:
        if isinstance(anchor, str):
            anchor = protomorph.Anchor(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")

        return self.entities_by_anchor[anchor]

    def layout(self, type: protomorph.Type) -> protomorph.Layout | None:
        _ = type
        return None

    def project(self, type: protomorph.Type, key: str | int) -> protomorph.Type:
        raise RuntimeError(
            "Semantic layout disabled: Realm.project(...) is temporarily unavailable "
            "while the semantic layout layer is being rebuilt"
        )

    def lift(self, qualifier: protomorph.Qualifier, result: protomorph.Type) -> protomorph.Type:
        if isinstance(qualifier, protomorph.Qual):
            return protomorph.Qual.of(result, *qualifier.qualifiers)
        return protomorph.Qual.of(result, qualifier)

    def combine(
        self,
        left: protomorph.Type,
        right: protomorph.Type,
        *,
        op: str | None = None,
    ) -> protomorph.Type:
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
