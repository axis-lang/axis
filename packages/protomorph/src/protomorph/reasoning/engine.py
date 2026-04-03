from __future__ import annotations

from protobase import Consed, flux, frozendict

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Anchor

from .core import EngineSolveCore
from .stratify import (
    build_dependency_graph,
    compute_sccs,
    compute_stratification,
)


class Engine(Consed):
    realm: protomorph.Realm

    @property
    def db(self):
        return self.realm

    @flux.property
    def anchors(self) -> frozenset[Anchor]:
        return self.realm.anchors

    @flux.property
    def rules_by_anchor(self) -> frozendict[Anchor, tuple[urs.Rule, ...]]:
        return frozendict(
            (anchor, self.realm.rules_for_anchor(anchor))
            for anchor in sorted(self.anchors)
        )

    @flux.property
    def facts_by_anchor(self) -> frozendict[Anchor, tuple[protomorph.Spec, ...]]:
        return frozendict(
            (anchor, self.realm.facts_by_anchor(anchor))
            for anchor in sorted(self.anchors)
        )

    @flux.property
    def all_rules(self) -> tuple[urs.Rule, ...]:
        ordered: list[urs.Rule] = []
        for anchor in sorted(self.rules_by_anchor):
            ordered.extend(self.rules_by_anchor[anchor])
        return tuple(ordered)

    @flux.property
    def dependency_graph(self) -> urs.DependencyGraph:
        return build_dependency_graph(self.all_rules, fact_anchors=self.anchors)

    @flux.property
    def sccs(self) -> tuple[urs.Scc, ...]:
        return compute_sccs(self.dependency_graph)

    @flux.property
    def strata(self) -> urs.StratificationPlan:
        return compute_stratification(self.dependency_graph, self.sccs)

    @flux.property
    def global_tables(self) -> urs.EngineTables:
        return EngineSolveCore(self).run()

    @flux.method
    def rules_for_anchor(self, anchor: Anchor) -> tuple[urs.Rule, ...]:
        return self.rules_by_anchor.get(anchor, ())

    @flux.method
    def facts_for_anchor(self, anchor: Anchor) -> tuple[protomorph.Spec, ...]:
        return self.global_tables.facts_by_anchor.get(anchor, ())

    @flux.method
    def facts_for_component(self, component_id: int) -> tuple[protomorph.Spec, ...]:
        return self.global_tables.facts_by_component.get(component_id, ())

    @flux.method
    def derived_facts_for_component(self, component_id: int) -> tuple[protomorph.Spec, ...]:
        return self.global_tables.derived_facts_by_component.get(component_id, ())

    @flux.method
    def session(self, context=None, state=None):
        return urs.Session(
            self,
            context if context is not None else urs.SolveContext(),
            state if state is not None else urs.SessionState(),
        )
