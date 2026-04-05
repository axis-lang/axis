from __future__ import annotations

from protobase import frozendict

import pm
from pm import reasoning as urs
from pm.foundation import Builtin

from .model import CycleMember, CycleTrace


class DependencyGraph(Builtin):
    anchors: tuple[str, ...] = ()
    positive: frozendict[str, tuple[str, ...]] = frozendict()
    negative: frozendict[str, tuple[str, ...]] = frozendict()

    def positive_of(self, anchor: str) -> tuple[str, ...]:
        return self.positive.get(anchor, ())

    def negative_of(self, anchor: str) -> tuple[str, ...]:
        return self.negative.get(anchor, ())

    def all_of(self, anchor: str) -> tuple[str, ...]:
        merged = (*self.positive_of(anchor), *self.negative_of(anchor))
        return tuple(dict.fromkeys(merged))


class Scc(Builtin):
    id: int
    anchors: tuple[str, ...] = ()


class StratificationPlan(Builtin):
    graph: urs.DependencyGraph
    components: tuple[urs.Scc, ...] = ()
    component_by_anchor: frozendict[str, int] = frozendict()
    stratum_by_component: tuple[int, ...] = ()
    negative_cycle_components: frozenset[int] = frozenset()

    def component_of(self, anchor: str) -> int:
        return self.component_by_anchor.get(anchor, -1)

    def stratum_of(self, anchor: str) -> int:
        component = self.component_of(anchor)
        if component < 0:
            return 0
        return self.stratum_by_component[component]

    def has_negative_cycle(self, anchor: str) -> bool:
        component = self.component_of(anchor)
        return component >= 0 and component in self.negative_cycle_components

    def negative_cycle_trace(self, anchor: str) -> urs.CycleTrace | None:
        component_id = self.component_of(anchor)
        if component_id < 0 or component_id not in self.negative_cycle_components:
            return None
        component = next((item for item in self.components if item.id == component_id), None)
        if component is None:
            return None
        members = tuple(CycleMember(pm.Spec.of(item), False, True) for item in component.anchors)
        return CycleTrace(members, "negative", "negative cycle in stratification", True)


def build_dependency_graph(
    rules: tuple[urs.Rule, ...],
    *,
    fact_anchors: frozenset[str] = frozenset(),
) -> urs.DependencyGraph:
    anchors = {str(rule.head.anchor) for rule in rules} | set(fact_anchors)
    positive: dict[str, set[str]] = {anchor: set() for anchor in anchors}
    negative: dict[str, set[str]] = {anchor: set() for anchor in anchors}

    for rule in rules:
        head_anchor = str(rule.head.anchor)
        for goal in rule.positive_goals:
            dep = str(goal.anchor)
            anchors.add(dep)
            positive.setdefault(head_anchor, set()).add(dep)
        for goal in rule.negative_goals:
            dep = str(goal.anchor)
            anchors.add(dep)
            negative.setdefault(head_anchor, set()).add(dep)

    ordered_anchors = tuple(sorted(anchors))
    for anchor in ordered_anchors:
        positive.setdefault(anchor, set())
        negative.setdefault(anchor, set())

    return DependencyGraph(
        ordered_anchors,
        frozendict((anchor, tuple(sorted(deps))) for anchor, deps in positive.items()),
        frozendict((anchor, tuple(sorted(deps))) for anchor, deps in negative.items()),
    )


def compute_sccs(graph: urs.DependencyGraph) -> tuple[urs.Scc, ...]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[Scc] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for dep in graph.all_of(node):
            if dep not in indices:
                strongconnect(dep)
                lowlinks[node] = min(lowlinks[node], lowlinks[dep])
            elif dep in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[dep])

        if lowlinks[node] != indices[node]:
            return

        members: list[str] = []
        while True:
            item = stack.pop()
            on_stack.remove(item)
            members.append(item)
            if item == node:
                break
        components.append(Scc(len(components), tuple(sorted(members))))

    for anchor in graph.anchors:
        if anchor not in indices:
            strongconnect(anchor)

    return tuple(components)


def compute_stratification(
    graph: urs.DependencyGraph,
    components: tuple[urs.Scc, ...],
) -> urs.StratificationPlan:
    component_by_anchor = {
        anchor: component.id
        for component in components
        for anchor in component.anchors
    }

    positive_by_component: dict[int, set[int]] = {component.id: set() for component in components}
    negative_by_component: dict[int, set[int]] = {component.id: set() for component in components}
    negative_cycle_components: set[int] = set()

    for anchor in graph.anchors:
        owner = component_by_anchor[anchor]
        for dep in graph.positive_of(anchor):
            positive_by_component[owner].add(component_by_anchor[dep])
        for dep in graph.negative_of(anchor):
            dep_component = component_by_anchor[dep]
            if dep_component == owner:
                negative_cycle_components.add(owner)
                continue
            negative_by_component[owner].add(dep_component)

    strata = [0 for _ in components]
    changed = True
    while changed:
        changed = False
        for component in components:
            current = strata[component.id]
            next_value = current
            for dep in positive_by_component[component.id]:
                next_value = max(next_value, strata[dep])
            for dep in negative_by_component[component.id]:
                next_value = max(next_value, strata[dep] + 1)
            if next_value != current:
                strata[component.id] = next_value
                changed = True

    return StratificationPlan(
        graph,
        components,
        frozendict(component_by_anchor.items()),
        tuple(strata),
        frozenset(negative_cycle_components),
    )
