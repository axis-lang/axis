from __future__ import annotations

from protobase import Consed, frozendict

import pm
from pm import reasoning as urs
from pm.foundation import Builtin

from .model import BindingsChanged, LocalFactsChanged
from .subst import BindingSnapshot, ground_fact_for
from .tabling import SessionTables


class SolveContext(Builtin):
    label: str = ""


urs.SolveContext = SolveContext
urs.SessionTables = SessionTables


class SessionState(Builtin):
    bindings: BindingSnapshot = BindingSnapshot()
    local_facts: tuple[pm.Spec, ...] = ()
    deferred: tuple[urs.DeferredGoal, ...] = ()
    tables: urs.SessionTables = SessionTables()
    epoch: int = 0
    binding_epoch: int = 0
    local_facts_epoch: int = 0
    recent_binding_updates: tuple[pm.Placeholder, ...] = ()
    recent_local_fact_anchors: tuple[str, ...] = ()


urs.SessionState = SessionState


class Session(Consed):
    engine: urs.Engine
    context: urs.SolveContext = SolveContext()
    state: urs.SessionState = SessionState()

    def query(self, goal: pm.Spec) -> urs.Query:
        return urs.Query(self, goal)

    def solve(self, goal: pm.Spec):
        return self.query(goal).result.outcome

    def with_bindings(
        self,
        bindings: frozendict[pm.Placeholder, urs.ReasoningValue],
    ) -> urs.Session:
        merged = dict(self.state.bindings.values)
        merged.update(bindings)
        next_state = SessionState(
            BindingSnapshot(frozendict(merged.items())),
            self.state.local_facts,
            self.state.deferred,
            self.state.tables,
            self.state.epoch + 1,
            self.state.binding_epoch + 1,
            self.state.local_facts_epoch,
            tuple(bindings.keys()),
            (),
        )
        return Session(self.engine, self.context, next_state)

    def with_deferred(self, deferred: tuple[urs.DeferredGoal, ...]) -> urs.Session:
        merged: dict[tuple[pm.Spec, object], urs.DeferredGoal] = {
            (item.goal, item.blocker): item for item in self.state.deferred
        }
        for item in deferred:
            merged[(item.goal, item.blocker)] = item
        next_state = SessionState(
            self.state.bindings,
            self.state.local_facts,
            tuple(merged.values()),
            self.state.tables,
            self.state.epoch + 1,
            self.state.binding_epoch,
            self.state.local_facts_epoch,
            self.state.recent_binding_updates,
            self.state.recent_local_fact_anchors,
        )
        return Session(self.engine, self.context, next_state)

    def clear_deferred(self) -> urs.Session:
        next_state = SessionState(
            self.state.bindings,
            self.state.local_facts,
            (),
            self.state.tables,
            self.state.epoch + 1,
            self.state.binding_epoch,
            self.state.local_facts_epoch,
            self.state.recent_binding_updates,
            self.state.recent_local_fact_anchors,
        )
        return Session(self.engine, self.context, next_state)

    def with_query_table(self, key: pm.Spec, table: urs.QueryTable) -> urs.Session:
        tables_by_goal = dict(self.state.tables.query_tables)
        answers_by_anchor = {anchor: list(values) for anchor, values in self.state.tables.answers_by_anchor.items()}
        tables_by_goal[key] = table
        for fact in _promoted_facts(table):
            answers_by_anchor.setdefault(str(fact.anchor), []).append(fact)
        normalized_answers = frozendict(
            (anchor, tuple(_dedupe_specs(values)))
            for anchor, values in answers_by_anchor.items()
        )
        next_tables = _build_session_tables(tables_by_goal, normalized_answers)
        next_state = SessionState(
            self.state.bindings,
            self.state.local_facts,
            self.state.deferred,
            next_tables,
            self.state.epoch + 1,
            self.state.binding_epoch,
            self.state.local_facts_epoch,
            self.state.recent_binding_updates,
            self.state.recent_local_fact_anchors,
        )
        return Session(self.engine, self.context, next_state)

    def without_goal(self, key: pm.Spec) -> urs.Session:
        tables_by_goal = dict(self.state.tables.query_tables)
        tables_by_goal.pop(key, None)
        next_tables = _build_session_tables(tables_by_goal, self.state.tables.answers_by_anchor)
        next_state = SessionState(
            self.state.bindings,
            self.state.local_facts,
            self.state.deferred,
            next_tables,
            self.state.epoch + 1,
            self.state.binding_epoch,
            self.state.local_facts_epoch,
            self.state.recent_binding_updates,
            self.state.recent_local_fact_anchors,
        )
        return Session(self.engine, self.context, next_state)

    def with_local_facts(self, *facts: pm.Spec) -> urs.Session:
        next_state = SessionState(
            self.state.bindings,
            (*self.state.local_facts, *facts),
            self.state.deferred,
            self.state.tables,
            self.state.epoch + 1,
            self.state.binding_epoch,
            self.state.local_facts_epoch + 1,
            (),
            tuple(dict.fromkeys(str(fact.anchor) for fact in facts)),
        )
        return Session(self.engine, self.context, next_state)

    def retry_deferred(self) -> urs.Session:
        return urs.SessionSolveCore(self).run()

    def resume_open_queries(self) -> urs.Session:
        return self.retry_deferred()


def _promoted_facts(table: urs.QueryTable) -> tuple[pm.Spec, ...]:
    facts: list[pm.Spec] = []
    if not table.closed or table.deferred or table.cycle_issue is not None:
        return ()
    for answer in table.answers:
        fact = ground_fact_for(table.key, answer.subst)
        if fact is not None:
            facts.append(fact)
    return tuple(_dedupe_specs(facts))


def _dedupe_specs(values: list[pm.Spec]) -> list[pm.Spec]:
    deduped: dict[pm.Spec, pm.Spec] = {}
    for value in values:
        deduped[value] = value
    return list(deduped.values())


def _build_session_tables(
    query_tables: dict[pm.Spec, urs.QueryTable],
    answers_by_anchor: frozendict[str, tuple[pm.Spec, ...]],
) -> urs.SessionTables:
    deferred_by_anchor: dict[str, set[pm.Spec]] = {}
    deferred_by_placeholder: dict[pm.Placeholder, set[pm.Spec]] = {}

    for key, table in query_tables.items():
        for branch in table.continuation_state:
            for wake in branch.blocked.wake_on:
                if isinstance(wake, BindingsChanged):
                    for placeholder in wake.placeholders:
                        deferred_by_placeholder.setdefault(placeholder, set()).add(key)
                elif isinstance(wake, LocalFactsChanged):
                    for anchor in wake.anchors:
                        deferred_by_anchor.setdefault(anchor, set()).add(key)

    return SessionTables(
        frozendict(query_tables.items()),
        answers_by_anchor,
        frozendict((anchor, tuple(sorted(values, key=repr))) for anchor, values in deferred_by_anchor.items()),
        frozendict((placeholder, tuple(sorted(values, key=repr))) for placeholder, values in deferred_by_placeholder.items()),
    )
