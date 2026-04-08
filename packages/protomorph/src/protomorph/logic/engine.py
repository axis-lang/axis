from __future__ import annotations

from typing import Any, cast

from protobase import Consed, flux, frozendict

import protomorph as pm

from .canonical import canonicalize_goal
from .model import (
    Assertion,
    Answer,
    Answers,
    Blocked,
    CoinductiveCycle,
    CoinductiveEdge,
    COINDUCTIVE_CYCLE_KEY,
    COINDUCTIVE_EDGE_KEY,
    REDUCIBLE_KEY,
    Ctrl,
    Cycle,
    Dependency,
    Expand,
    Failed,
    Goal,
    Key,
    Premise,
    Reduced,
    Reducible,
    TableKey,
    SolverTables,
)
from .session import Session
from .stratify import DependencyGraph, Scc, StratificationPlan, build_dependency_graph, compute_sccs, compute_stratification


class Solver(Consed):
    realm: pm.Realm
    assertions: frozenset[Assertion] = frozenset()

    @flux.property
    def ctrl_type(self) -> pm.Type:
        return cast(pm.Type, pm.val(Ctrl).fetch())

    @flux.property
    def all_assertions(self) -> frozenset[Assertion]:
        return self.realm.logic_assertions | self.assertions

    @flux.property
    def assertions_by_key(self) -> frozendict[Key, frozenset[Assertion]]:
        buckets: dict[Key, set[Assertion]] = {}
        for assertion in self.all_assertions:
            buckets.setdefault(self.head_key(assertion.fact), set()).add(assertion)
        return frozendict((key, frozenset(items)) for key, items in sorted(buckets.items(), key=lambda item: repr(item[0])))

    @flux.property
    def seed_facts_by_key(self) -> frozendict[Key, frozenset[pm.Val]]:
        buckets: dict[Key, set[pm.Val]] = {}
        for assertion in self.all_assertions:
            if not assertion.is_fact:
                continue
            buckets.setdefault(self.head_key(assertion.fact), set()).add(assertion.fact)
        return frozendict((key, frozenset(items)) for key, items in sorted(buckets.items(), key=lambda item: repr(item[0])))

    @flux.property
    def dependency_graph(self) -> DependencyGraph:
        return build_dependency_graph(
            self.all_assertions,
            fact_keys=frozenset((*self.assertions_by_key.keys(), *self.seed_facts_by_key.keys())),
            dependencies_of=self._dependencies_for_graph,
        )

    @flux.property
    def sccs(self) -> tuple[Scc, ...]:
        return compute_sccs(self.dependency_graph)

    @flux.property
    def strata(self) -> StratificationPlan:
        return compute_stratification(self.dependency_graph, self.sccs)

    @flux.property
    def global_tables(self) -> SolverTables:
        return _compute_global_tables(self)

    def head_key(self, x: pm.Val) -> Key:
        value = x.fetch()
        if isinstance(value, pm.Spec):
            return cast(Key, pm.val(value.anchor))
        return pm.val(x.descriptor)

    def is_coinductive(self, cycle: Cycle[TableKey]) -> bool:
        if cycle.is_negative:
            return False

        coinductive_cycle = self._project_coinductive_cycle(cycle)
        cycle_facts = self.global_tables.facts_by_key.get(COINDUCTIVE_CYCLE_KEY, frozenset())
        if pm.val(coinductive_cycle) in cycle_facts:
            return True

        edge_facts = self.global_tables.facts_by_key.get(COINDUCTIVE_EDGE_KEY, frozenset())
        if not cycle.edges:
            return False
        return all(
            pm.val(CoinductiveEdge(self.head_key(edge.from_), self.head_key(edge.to))) in edge_facts
            for edge in cycle.edges
            if edge.affirmative
        )

    def _project_coinductive_cycle(self, cycle: Cycle[TableKey]) -> CoinductiveCycle:
        return CoinductiveCycle.of(
            *(
                CoinductiveEdge(self.head_key(edge.from_), self.head_key(edge.to))
                for edge in cycle.edges
                if edge.affirmative
            )
        )

    def dependencies_of(self, assertion: Assertion) -> tuple[Dependency, ...]:
        return tuple(
            Dependency(self.head_key(premise.goal), not premise.affirmative)
            for premise in assertion.premises
        )

    def _dependencies_for_graph(self, item: Assertion | pm.Val):
        if isinstance(item, Assertion):
            return self.dependencies_of(item)
        return self.head_key(cast(pm.Val, item))

    def is_reducible(self, x: pm.Val) -> bool:
        reducible_facts = self.global_tables.facts_by_key.get(REDUCIBLE_KEY, frozenset())
        return pm.val(Reducible(x.descriptor)) in reducible_facts

    def eval_as_ctrl(self, x: pm.Val) -> pm.Val:
        try:
            result = self.realm.eval(x, to=self.ctrl_type)
        except Exception as exc:
            return pm.val(Failed(f"evaluation error: {exc}"))

        carrier = _coerce_eval_result(result)
        if carrier is not None and isinstance(carrier.fetch(), Ctrl):
            return carrier
        if carrier is None:
            return pm.val(Failed("evaluation error: realm.eval returned no value"))
        return pm.val(Failed("realm.eval did not return pm.logic.Ctrl", carrier))

    def facts_for(self, key: Key) -> frozenset[pm.Val]:
        return self.global_tables.facts_by_key.get(key, frozenset())

    def assertions_for(self, key: Key) -> frozenset[Assertion]:
        return self.assertions_by_key.get(key, frozenset())

    def facts_for_component(self, component_id: int) -> frozenset[pm.Val]:
        return self.global_tables.facts_by_component.get(component_id, frozenset())

    def derived_facts_for_component(self, component_id: int) -> frozenset[pm.Val]:
        return self.global_tables.derived_facts_by_component.get(component_id, frozenset())

    def session(self, *, local_facts: tuple[pm.Val, ...] = (), label: str = "") -> Session:
        return Session(self, frozenset(local_facts), label)


def _coerce_eval_result(value: Any) -> pm.Val | None:
    if value is None:
        return None
    carrier = value if isinstance(value, pm.Val) else pm.val(value)
    if isinstance(carrier, pm.Result):
        if carrier.is_err:
            return pm.val(Failed("evaluation error", carrier.error_carrier()))
        return cast(pm.Val, carrier.unwrap())
    if isinstance(carrier, pm.Option):
        if carrier.is_none:
            return None
        return cast(pm.Val, carrier.unwrap())
    return carrier


def _is_logic_var(carrier: pm.Val) -> bool:
    return isinstance(carrier.fetch(), (pm.Placeholder, pm.Var))


def _contains_logic_vars(carrier: pm.Val) -> bool:
    for leaf in carrier.deep_iter():
        if _is_logic_var(leaf):
            return True
    return False


def _matches_any_fact(goal: pm.Val, facts: frozenset[pm.Val] | set[pm.Val]) -> bool:
    for fact in facts:
        uf = pm.UnionFind(_is_logic_var)
        if pm.unify(goal, fact, subst=uf) is not None:
            return True
    return False


def _is_reducible_with_facts(goal: Goal, reducible_facts: frozenset[pm.Val] | set[pm.Val]) -> bool:
    return pm.val(Reducible(goal.descriptor)) in reducible_facts


def _apply_public_answer(target: Goal, answer: Answer, uf: pm.UnionFind) -> bool:
    if not answer.subst:
        return True

    canonical = canonicalize_goal(target, uf)
    slot_by_placeholder: dict[pm.Placeholder, Goal] = {}
    for slot in canonical.slots:
        value = slot.fetch()
        if isinstance(value, pm.Placeholder):
            slot_by_placeholder[value] = slot

    for placeholder, value in answer.subst.items():
        slot = slot_by_placeholder.get(placeholder)
        if slot is None or pm.unify(slot, value, subst=uf) is None:
            return False
    return True


def _derive_ground_facts(
    solver: Solver,
    assertion: Assertion,
    known: dict[Key, set[pm.Val]],
    current_stratum: int,
    reducible_facts: frozenset[pm.Val] | set[pm.Val],
) -> frozenset[pm.Val]:
    answers: list[pm.Val] = []
    uf = pm.UnionFind(_is_logic_var)

    def proof_state_for_goal(goal: Goal) -> str:
        blocked = False
        if _is_reducible_with_facts(goal, reducible_facts):
            ctrl = solver.eval_as_ctrl(goal).fetch()
            if isinstance(ctrl, Reduced):
                state = proof_state_for_goal(uf.reify(ctrl.value))
                if state != "missing":
                    return state
            elif isinstance(ctrl, Expand):
                state = proof_state_for_sequence(tuple(Premise(uf.reify(item)) for item in ctrl.goals))
                if state != "missing":
                    return state
            elif isinstance(ctrl, Answers):
                for answer in ctrl.items:
                    snap = uf.snapshot()
                    if _apply_public_answer(goal, answer, uf):
                        uf.rollback(snap)
                        return "proved"
                    uf.rollback(snap)
            elif isinstance(ctrl, Blocked):
                blocked = True
            elif isinstance(ctrl, Failed):
                pass

        key = solver.head_key(goal)
        if _matches_any_fact(goal, frozenset(known.get(key, set()))):
            return "proved"
        return "blocked" if blocked else "missing"

    def proof_state_for_sequence(premises: tuple[Premise, ...]) -> str:
        if not premises:
            return "proved"

        premise = premises[0]
        remaining = premises[1:]
        target = uf.reify(premise.goal)

        if not premise.affirmative:
            inner = target
            key = solver.head_key(inner)
            if solver.strata.has_negative_cycle(key):
                return "blocked"
            if solver.strata.stratum_of(key) >= current_stratum:
                return "blocked"
            if _contains_logic_vars(inner):
                return "blocked"
            state = proof_state_for_goal(inner)
            if state == "proved":
                return "missing"
            if state == "blocked":
                return "blocked"
            return proof_state_for_sequence(remaining)

        blocked = False
        if _is_reducible_with_facts(target, reducible_facts):
            ctrl = solver.eval_as_ctrl(target).fetch()
            if isinstance(ctrl, Reduced):
                state = proof_state_for_sequence((Premise(uf.reify(ctrl.value)), *remaining))
                if state == "proved":
                    return state
                blocked = blocked or state == "blocked"
            elif isinstance(ctrl, Expand):
                state = proof_state_for_sequence(tuple(Premise(uf.reify(item)) for item in ctrl.goals) + remaining)
                if state == "proved":
                    return state
                blocked = blocked or state == "blocked"
            elif isinstance(ctrl, Answers):
                for answer in ctrl.items:
                    snap = uf.snapshot()
                    if _apply_public_answer(target, answer, uf):
                        state = proof_state_for_sequence(remaining)
                        uf.rollback(snap)
                        if state == "proved":
                            return state
                        blocked = blocked or state == "blocked"
                        continue
                    uf.rollback(snap)
            elif isinstance(ctrl, Blocked):
                blocked = True
            elif isinstance(ctrl, Failed):
                pass

        key = solver.head_key(target)
        for fact in known.get(key, set()):
            snap = uf.snapshot()
            if pm.unify(target, fact, subst=uf) is not None:
                state = proof_state_for_sequence(remaining)
                uf.rollback(snap)
                if state == "proved":
                    return state
                blocked = blocked or state == "blocked"
                continue
            uf.rollback(snap)
        return "blocked" if blocked else "missing"

    def solve_sequence(premises: tuple[Premise, ...]) -> bool:
        if not premises:
            grounded = uf.reify(assertion.fact)
            if _contains_logic_vars(grounded):
                return False
            answers.append(grounded)
            return True

        premise = premises[0]
        remaining = premises[1:]
        target = uf.reify(premise.goal)
        if not premise.affirmative:
            inner = target
            key = solver.head_key(inner)
            if solver.strata.has_negative_cycle(key):
                return False
            if solver.strata.stratum_of(key) >= current_stratum:
                return False
            if _contains_logic_vars(inner):
                return False
            state = proof_state_for_goal(inner)
            if state != "missing":
                return False
            return solve_sequence(remaining)

        produced = False

        if _is_reducible_with_facts(target, reducible_facts):
            ctrl = solver.eval_as_ctrl(target).fetch()
            if isinstance(ctrl, Reduced):
                produced |= solve_sequence((Premise(uf.reify(ctrl.value)), *remaining))
            elif isinstance(ctrl, Expand):
                produced |= solve_sequence(tuple(Premise(uf.reify(item)) for item in ctrl.goals) + remaining)
            elif isinstance(ctrl, Answers):
                for answer in ctrl.items:
                    snap = uf.snapshot()
                    if _apply_public_answer(target, answer, uf):
                        produced |= solve_sequence(remaining)
                    uf.rollback(snap)
            elif isinstance(ctrl, (Blocked, Failed)):
                pass

        key = solver.head_key(target)
        for fact in known.get(key, set()):
            snap = uf.snapshot()
            if pm.unify(target, fact, subst=uf) is not None:
                produced |= solve_sequence(remaining)
            uf.rollback(snap)

        return produced

    solve_sequence(assertion.premises)
    return frozenset(answers)


def _compute_global_tables(solver: Solver) -> SolverTables:
    known: dict[Key, set[pm.Val]] = {
        key: set(values)
        for key, values in solver.seed_facts_by_key.items()
    }
    derived: dict[Key, set[pm.Val]] = {key: set() for key in (*solver.assertions_by_key.keys(), *solver.seed_facts_by_key.keys())}
    closed_components: set[int] = set()
    closed_strata: set[int] = set()

    strata_values = sorted(set(solver.strata.stratum_by_component))
    for stratum in strata_values:
        components = tuple(
            component
            for component in solver.sccs
            if solver.strata.stratum_by_component[component.id] == stratum
        )
        while True:
            changed = False
            for component in components:
                if component.id in solver.strata.negative_cycle_components:
                    continue
                reducible_facts = frozenset(known.get(REDUCIBLE_KEY, set()))
                for key in component.keys:
                    for assertion in solver.assertions_by_key.get(key, frozenset()):
                        if assertion.is_fact:
                            continue
                        for fact in _derive_ground_facts(solver, assertion, known, stratum, reducible_facts):
                            bucket = known.setdefault(key, set())
                            if fact in bucket:
                                continue
                            bucket.add(fact)
                            if fact not in solver.seed_facts_by_key.get(key, frozenset()):
                                derived.setdefault(key, set()).add(fact)
                            changed = True
            if not changed:
                break
        for component in components:
            closed_components.add(component.id)
        closed_strata.add(stratum)

    facts_by_component: dict[int, frozenset[pm.Val]] = {}
    derived_by_component: dict[int, frozenset[pm.Val]] = {}
    for component in solver.sccs:
        if component.id not in closed_components:
            continue
        facts_by_component[component.id] = frozenset(
            fact
            for key in component.keys
            for fact in known.get(key, set())
        )
        derived_by_component[component.id] = frozenset(
            fact
            for key in component.keys
            for fact in derived.get(key, set())
        )

    return SolverTables(
        facts_by_key=frozendict((key, frozenset(values)) for key, values in known.items()),
        derived_facts_by_key=frozendict((key, frozenset(values)) for key, values in derived.items()),
        facts_by_component=frozendict(sorted(facts_by_component.items())),
        derived_facts_by_component=frozendict(sorted(derived_by_component.items())),
        assertions_by_key=solver.assertions_by_key,
        closed_components=frozenset(closed_components),
        closed_strata=frozenset(closed_strata),
    )
