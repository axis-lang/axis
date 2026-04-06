from __future__ import annotations

from protobase import frozendict

from protomorph.foundation import Builtin

from .model import Assertion, Key


class DependencyGraph(Builtin):
    keys: frozenset[Key] = frozenset()
    positive: frozendict[Key, frozenset[Key]] = frozendict()
    negative: frozendict[Key, frozenset[Key]] = frozendict()

    def positive_of(self, key: Key) -> frozenset[Key]:
        return self.positive.get(key, frozenset())

    def negative_of(self, key: Key) -> frozenset[Key]:
        return self.negative.get(key, frozenset())

    def all_of(self, key: Key) -> frozenset[Key]:
        return self.positive_of(key) | self.negative_of(key)


class Scc(Builtin):
    id: int
    keys: frozenset[Key] = frozenset()


class StratificationPlan(Builtin):
    graph: DependencyGraph
    components: tuple[Scc, ...] = ()
    component_by_key: frozendict[Key, int] = frozendict()
    stratum_by_component: tuple[int, ...] = ()
    negative_cycle_components: frozenset[int] = frozenset()

    def component_of(self, key: Key) -> int:
        return self.component_by_key.get(key, -1)

    def stratum_of(self, key: Key) -> int:
        component = self.component_of(key)
        if component < 0:
            return 0
        return self.stratum_by_component[component]

    def has_negative_cycle(self, key: Key) -> bool:
        component = self.component_of(key)
        return component >= 0 and component in self.negative_cycle_components


def build_dependency_graph(
    assertions: frozenset[Assertion] | tuple[Assertion, ...],
    *,
    fact_keys: frozenset[Key] = frozenset(),
    dependencies_of,
) -> DependencyGraph:
    all_keys = set(fact_keys)
    positive: dict[Key, set[Key]] = {}
    negative: dict[Key, set[Key]] = {}

    for assertion in assertions:
        head_key = dependencies_of(assertion.fact)
        all_keys.add(head_key)
        positive.setdefault(head_key, set())
        negative.setdefault(head_key, set())
        for dep in dependencies_of(assertion):
            all_keys.add(dep.key)
            buckets = negative if dep.negated else positive
            buckets.setdefault(head_key, set()).add(dep.key)

    for key in all_keys:
        positive.setdefault(key, set())
        negative.setdefault(key, set())

    return DependencyGraph(
        frozenset(all_keys),
        frozendict((key, frozenset(deps)) for key, deps in positive.items()),
        frozendict((key, frozenset(deps)) for key, deps in negative.items()),
    )


def compute_sccs(graph: DependencyGraph) -> tuple[Scc, ...]:
    index = 0
    indices: dict[Key, int] = {}
    lowlinks: dict[Key, int] = {}
    stack: list[Key] = []
    on_stack: set[Key] = set()
    components: list[Scc] = []

    def strongconnect(node: Key) -> None:
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

        members: list[Key] = []
        while True:
            item = stack.pop()
            on_stack.remove(item)
            members.append(item)
            if item == node:
                break
        components.append(Scc(len(components), frozenset(members)))

    for key in sorted(graph.keys, key=repr):
        if key not in indices:
            strongconnect(key)

    return tuple(components)


def compute_stratification(
    graph: DependencyGraph,
    components: tuple[Scc, ...],
) -> StratificationPlan:
    component_by_key: dict[Key, int] = {
        key: component.id
        for component in components
        for key in component.keys
    }

    positive_by_component: dict[int, set[int]] = {component.id: set() for component in components}
    negative_by_component: dict[int, set[int]] = {component.id: set() for component in components}
    negative_cycle_components: set[int] = set()

    for key in graph.keys:
        owner = component_by_key[key]
        for dep in graph.positive_of(key):
            positive_by_component[owner].add(component_by_key[dep])
        for dep in graph.negative_of(key):
            dep_component = component_by_key[dep]
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
        frozendict(component_by_key.items()),
        tuple(strata),
        frozenset(negative_cycle_components),
    )
