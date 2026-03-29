from __future__ import annotations

from protobase import Consed, flux, frozendict

import pm

from .database import Database
from .core import _EngineSolveCore
from .model import Rule
from .stratify import (
    DependencyGraph,
    Scc,
    StratificationPlan,
    build_dependency_graph,
    compute_sccs,
    compute_stratification,
)
from .tabling import EngineTables


class Engine(Consed):
    db: Database

    @flux.property
    def anchors(self) -> frozenset[str]:
        return self.db.anchors

    @flux.property
    def rules_by_anchor(self) -> frozendict[str, tuple[Rule, ...]]:
        return frozendict(
            (anchor, self.db.rules_for_anchor(anchor))
            for anchor in sorted(self.anchors)
        )

    @flux.property
    def facts_by_anchor(self) -> frozendict[str, tuple[pm.Spec, ...]]:
        return frozendict(
            (anchor, self.db.facts_by_anchor(anchor))
            for anchor in sorted(self.anchors)
        )

    @flux.property
    def all_rules(self) -> tuple[Rule, ...]:
        ordered: list[Rule] = []
        for anchor in sorted(self.rules_by_anchor):
            ordered.extend(self.rules_by_anchor[anchor])
        return tuple(ordered)

    @flux.property
    def dependency_graph(self) -> DependencyGraph:
        return build_dependency_graph(self.all_rules, fact_anchors=self.anchors)

    @flux.property
    def sccs(self) -> tuple[Scc, ...]:
        return compute_sccs(self.dependency_graph)

    @flux.property
    def strata(self) -> StratificationPlan:
        return compute_stratification(self.dependency_graph, self.sccs)

    @flux.property
    def global_tables(self) -> EngineTables:
        return _EngineSolveCore(self).run()

    @flux.method
    def rules_for_anchor(self, anchor: str) -> tuple[Rule, ...]:
        return self.rules_by_anchor.get(anchor, ())

    @flux.method
    def facts_for_anchor(self, anchor: str) -> tuple[pm.Spec, ...]:
        return self.global_tables.facts_by_anchor.get(anchor, ())

    @flux.method
    def facts_for_component(self, component_id: int) -> tuple[pm.Spec, ...]:
        return self.global_tables.facts_by_component.get(component_id, ())

    @flux.method
    def derived_facts_for_component(self, component_id: int) -> tuple[pm.Spec, ...]:
        return self.global_tables.derived_facts_by_component.get(component_id, ())

    @flux.method
    def session(self, context=None, state=None):
        from .session import Session, SessionState, SolveContext

        return Session(
            self,
            context if context is not None else SolveContext(),
            state if state is not None else SessionState(),
        )
