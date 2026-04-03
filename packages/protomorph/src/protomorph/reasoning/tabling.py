from __future__ import annotations

from protobase import frozendict

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Anchor, Builtin


class StoredAnswer(Builtin):
    subst: tuple[tuple[int, protomorph.Carrier], ...] = ()
    evidence: protomorph.Spec | None = None
    judgment: urs.Judgment | None = None


class EngineTables(Builtin):
    facts_by_anchor: frozendict[Anchor, tuple[protomorph.Spec, ...]] = frozendict()
    derived_facts_by_anchor: frozendict[Anchor, tuple[protomorph.Spec, ...]] = frozendict()
    facts_by_component: frozendict[int, tuple[protomorph.Spec, ...]] = frozendict()
    derived_facts_by_component: frozendict[int, tuple[protomorph.Spec, ...]] = frozendict()
    rules_by_anchor: frozendict[Anchor, tuple[urs.Rule, ...]] = frozendict()
    closed_components: frozenset[int] = frozenset()
    closed_strata: frozenset[int] = frozenset()

    def facts_of_component(self, component_id: int) -> tuple[protomorph.Spec, ...]:
        return self.facts_by_component.get(component_id, ())

    def derived_facts_of_component(self, component_id: int) -> tuple[protomorph.Spec, ...]:
        return self.derived_facts_by_component.get(component_id, ())

    def is_component_closed(self, component_id: int) -> bool:
        return component_id in self.closed_components


class QueryTable(Builtin):
    key: protomorph.Spec
    origin: protomorph.Spec | None = None
    query_slot_indices: tuple[int, ...] = ()
    status: str = "closed"
    answers: tuple[StoredAnswer, ...] = ()
    failures: tuple[urs.Judgment, ...] = ()
    deferred: tuple[urs.DeferredGoal, ...] = ()
    cycle_issue: urs.CycleIssue | None = None
    frontier: tuple[protomorph.Spec, ...] = ()
    continuation_state: tuple[urs.PendingBranch, ...] = ()
    active: bool = False
    closed: bool = True
    binding_epoch: int = 0
    local_facts_epoch: int = 0
    placeholders: tuple[protomorph.Placeholder, ...] = ()

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
    query_tables: frozendict[protomorph.Spec, QueryTable] = frozendict()
    answers_by_anchor: frozendict[Anchor, tuple[protomorph.Spec, ...]] = frozendict()
    deferred_by_anchor: frozendict[Anchor, tuple[protomorph.Spec, ...]] = frozendict()
    deferred_by_placeholder: frozendict[protomorph.Placeholder, tuple[protomorph.Spec, ...]] = frozendict()
