from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, cast, runtime_checkable

from protobase import Consed, flux, frozendict

import protomorph as pm

__all__ = [
    "LogicBackend",
    "LogicSolver",
    "GlobalFixedPointSolver",
]


@runtime_checkable
class LogicBackend(Protocol):
    @property
    def all_facts(self) -> frozenset[pm.Spec]: ...

    @property
    def facts_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Spec]]: ...

    @property
    def all_clauses(self) -> frozenset[pm.Clause]: ...

    @property
    def clauses_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Clause]]: ...


@runtime_checkable
class LogicSolver(Protocol):
    def table(self, anchor: pm.Anchor) -> frozenset[pm.Spec]: ...

    def answers(
        self,
        goal: pm.Spec,
        state: pm.Subst | None = None,
    ) -> tuple[pm.Subst, ...]: ...


class GlobalFixedPointSolver(Consed):
    backend: pm.SemanticBridgeBase

    @flux.property
    def empirical_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Spec]]:
        return _logic_backend(self.backend).facts_by_anchor

    @flux.property
    def derived_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Spec]]:
        known: dict[pm.Anchor, set[pm.Spec]] = {
            anchor: set(facts)
            for anchor, facts in self.empirical_by_anchor.items()
        }
        derived: dict[pm.Anchor, set[pm.Spec]] = {}

        changed = True
        while changed:
            changed = False
            snapshot = _freeze_known(known)
            for clause in _logic_backend(self.backend).all_clauses:
                for fact in _apply_clause(clause, snapshot, bridge=self._match_bridge()):
                    bucket = known.setdefault(fact.anchor, set())
                    if fact in bucket:
                        continue
                    bucket.add(fact)
                    derived.setdefault(fact.anchor, set()).add(fact)
                    changed = True

        return frozendict(
            (anchor, frozenset(facts)) for anchor, facts in derived.items() if facts
        )

    @flux.property
    def saturated_by_anchor(self) -> frozendict[pm.Anchor, frozenset[pm.Spec]]:
        merged: dict[pm.Anchor, set[pm.Spec]] = {
            anchor: set(facts)
            for anchor, facts in self.empirical_by_anchor.items()
        }

        for anchor, facts in self.derived_by_anchor.items():
            merged.setdefault(anchor, set()).update(facts)

        return frozendict(
            (anchor, frozenset(facts)) for anchor, facts in merged.items() if facts
        )

    @flux.property
    def saturated_facts(self) -> frozenset[pm.Spec]:
        return frozenset(
            fact
            for facts in self.saturated_by_anchor.values()
            for fact in facts
        )

    @flux.method
    def table(self, anchor: pm.Anchor) -> frozenset[pm.Spec]:
        return self.saturated_by_anchor[anchor] if anchor in self.saturated_by_anchor else frozenset()

    @flux.method
    def answers(
        self,
        goal: pm.Spec,
        state: pm.Subst | None = None,
    ) -> tuple[pm.Subst, ...]:
        state = pm.Subst() if state is None else state
        bridge = self._match_bridge()
        return _solve_goal_against_facts(
            goal,
            self.table(goal.anchor),
            state=state,
            bridge=bridge,
        )

    def _match_bridge(self) -> pm.SemanticBridge:
        return self.backend


def _apply_clause(
    clause: pm.Clause,
    known_by_anchor: frozendict[pm.Anchor, frozenset[pm.Spec]],
    *,
    bridge: pm.SemanticBridge,
) -> tuple[pm.Spec, ...]:
    states: tuple[pm.Subst, ...] = (pm.Subst(),)
    for goal in clause.body:
        next_states: set[pm.Subst] = set()
        for state in states:
            instantiated = _instantiate_goal(goal, state)
            if not isinstance(instantiated, pm.Spec):
                continue
            next_states.update(
                _solve_goal_against_facts(
                    instantiated,
                    (
                        known_by_anchor[instantiated.anchor]
                        if instantiated.anchor in known_by_anchor
                        else frozenset()
                    ),
                    state=state,
                    bridge=bridge,
                )
            )
        if not next_states:
            return ()
        states = tuple(next_states)

    derived: set[pm.Spec] = set()
    for state in states:
        instantiated = _instantiate_goal(clause.head, state)
        if isinstance(instantiated, pm.Spec):
            derived.add(instantiated)
    return tuple(sorted(derived, key=repr))


def _instantiate_goal(goal: pm.Spec, state: pm.Subst) -> pm.Val:
    def resolve(value: pm.Val) -> pm.Val | None:
        if not isinstance(value, pm.Var):
            return None
        return state.bindings.get(value)

    return goal.subst(resolve)


def _freeze_known(
    known: dict[pm.Anchor, set[pm.Spec]],
) -> frozendict[pm.Anchor, frozenset[pm.Spec]]:
    return frozendict(
        (anchor, frozenset(facts)) for anchor, facts in known.items() if facts
    )


def _logic_backend(backend: pm.SemanticBridgeBase):
    return cast(LogicBackend, backend)


def _solve_goal_against_facts(
    goal: pm.Spec,
    facts: frozenset[pm.Spec],
    *,
    state: pm.Subst,
    bridge: pm.SemanticBridge,
) -> tuple[pm.Subst, ...]:
    states: set[pm.Subst] = set()
    visible_vars = frozenset((*state.bindings.keys(), *_goal_vars(goal)))
    for fact in facts:
        states.update(
            _visible_state(result.subst, visible_vars)
            for result in pm.unify(goal, fact, subst=state, bridge=bridge)
        )
    return tuple(sorted(states, key=repr))


def _visible_state(
    state: pm.Subst,
    visible_vars: frozenset[pm.Val],
) -> pm.Subst:
    if not visible_vars:
        return pm.Subst()
    bindings = frozendict(
        (key, value)
        for key, value in state.bindings.items()
        if key in visible_vars
    )
    return pm.Subst(bindings=bindings)


def _goal_vars(goal: pm.Spec) -> tuple[pm.Var, ...]:
    found: dict[pm.Var, None] = {}
    _collect_vars(goal, found)
    return tuple(found.keys())


def _collect_vars(value: object, found: dict[pm.Var, None]) -> None:
    if isinstance(value, pm.Var):
        found.setdefault(value, None)
        return

    if isinstance(value, pm.Spec):
        _collect_vars(value.anchor, found)
        args = value.args
        if args is not None:
            for item in args.values:
                _collect_vars(item, found)
        return

    if isinstance(value, pm.Const):
        attrs = value.attrs
        if attrs is not None:
            for item in attrs.values:
                _collect_vars(item, found)
            return
        if isinstance(value.__data__, pm.Type):
            _collect_vars(value.__data__, found)
        return

    if isinstance(value, pm.NominalQualifier):
        _collect_vars(value.spec_ref, found)
        _collect_vars(value.underlying, found)
        return

    if isinstance(value, pm.NominalType):
        _collect_vars(value.spec_ref, found)
        return

    if isinstance(value, pm.StructType):
        for item in value.meta_attrs.values:
            _collect_vars(item, found)
        return

    if isinstance(value, pm.UnionType):
        for item in value.types:
            _collect_vars(item, found)
