from __future__ import annotations

from protobase import frozendict

import pm
from pm.foundation import Builtin

from .model import CycleIssue, DeferredGoal, Judgment, PendingBranch, Rule


class StoredAnswer(Builtin):
    subst: tuple[tuple[int, pm.Carrier], ...] = ()
    evidence: pm.Spec | None = None
    judgment: Judgment | None = None


class EngineTables(Builtin):
    facts_by_anchor: frozendict[str, tuple[pm.Spec, ...]] = frozendict()
    derived_facts_by_anchor: frozendict[str, tuple[pm.Spec, ...]] = frozendict()
    facts_by_component: frozendict[int, tuple[pm.Spec, ...]] = frozendict()
    derived_facts_by_component: frozendict[int, tuple[pm.Spec, ...]] = frozendict()
    rules_by_anchor: frozendict[str, tuple[Rule, ...]] = frozendict()
    closed_components: frozenset[int] = frozenset()
    closed_strata: frozenset[int] = frozenset()

    def facts_of_component(self, component_id: int) -> tuple[pm.Spec, ...]:
        return self.facts_by_component.get(component_id, ())

    def derived_facts_of_component(self, component_id: int) -> tuple[pm.Spec, ...]:
        return self.derived_facts_by_component.get(component_id, ())

    def is_component_closed(self, component_id: int) -> bool:
        return component_id in self.closed_components


class QueryTable(Builtin):
    key: pm.Spec
    origin: pm.Spec | None = None
    query_slot_indices: tuple[int, ...] = ()
    status: str = "closed"
    answers: tuple[StoredAnswer, ...] = ()
    failures: tuple[Judgment, ...] = ()
    deferred: tuple[DeferredGoal, ...] = ()
    cycle_issue: CycleIssue | None = None
    frontier: tuple[pm.Spec, ...] = ()
    continuation_state: tuple[PendingBranch, ...] = ()
    active: bool = False
    closed: bool = True
    binding_epoch: int = 0
    local_facts_epoch: int = 0
    placeholders: tuple[pm.Placeholder, ...] = ()

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)

    @property
    def is_cycle(self) -> bool:
        return self.cycle_issue is not None

    @property
    def is_blocked(self) -> bool:
        return bool(self.deferred or self.continuation_state)


class SessionTables(Builtin):
    query_tables: frozendict[pm.Spec, QueryTable] = frozendict()
    answers_by_anchor: frozendict[str, tuple[pm.Spec, ...]] = frozendict()
    deferred_by_anchor: frozendict[str, tuple[pm.Spec, ...]] = frozendict()
    deferred_by_placeholder: frozendict[pm.Placeholder, tuple[pm.Spec, ...]] = frozendict()
