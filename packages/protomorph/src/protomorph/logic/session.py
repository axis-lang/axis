from __future__ import annotations

from typing import TYPE_CHECKING

from protobase import Consed, frozendict

import protomorph as pm

if TYPE_CHECKING:
    from .engine import Solver
    from .queryset import QuerySet
else:
    Solver = pm.Builtin
    QuerySet = pm.Builtin


class Session(Consed):
    solver: Solver
    local_facts: frozenset[pm.Carrier] = frozenset()
    label: str = ""

    def with_local_facts(self, *facts: pm.Carrier | pm.Datum) -> Session:
        coerced = frozenset(fact if isinstance(fact, pm.Carrier) else pm.wrap(fact) for fact in facts)
        return Session(self.solver, self.local_facts | coerced, self.label)

    def queryset(self, *goals: pm.Carrier | pm.Datum) -> QuerySet:
        from .queryset import QuerySet

        queryset = QuerySet(self)
        return queryset.add(*goals)

    def continue_(self, queryset: QuerySet) -> QuerySet:
        from .model import QuerySetState
        from .queryset import QuerySet, _dependent_tables_for_keys

        if queryset.session == self:
            return queryset.continue_()
        state = queryset.state
        if queryset.session.solver == self.solver and queryset.session.local_facts == self.local_facts:
            return QuerySet(self, state).continue_()

        binding_epoch = state.binding_epoch
        binding_epochs = dict(state.binding_epochs_by_key)

        if queryset.session.solver != self.solver:
            dirty_keys = tuple(state.tables_by_key.keys())
            if dirty_keys or binding_epochs:
                binding_epoch += 1
            for table in state.tables_by_key.values():
                binding_epochs[self.solver.head_key(table.goal)] = binding_epoch
        else:
            changed_fact_keys = {
                self.solver.head_key(fact)
                for fact in queryset.session.local_facts ^ self.local_facts
            }
            dirty: set[pm.Carrier] = set()
            dirty.update(
                key
                for key, table in state.tables_by_key.items()
                if self.solver.head_key(table.goal) in changed_fact_keys
            )
            dirty.update(
                _dependent_tables_for_keys(
                    state.tables_by_positive_key,
                    state.tables_by_negative_key,
                    frozenset(changed_fact_keys),
                )
            )
            dirty_keys = tuple(dirty)
            if changed_fact_keys:
                binding_epoch += 1
                for key in changed_fact_keys:
                    binding_epochs[key] = binding_epoch

        refreshed = QuerySetState(
            roots=state.roots,
            tables_by_key=state.tables_by_key,
            tables_by_positive_key=state.tables_by_positive_key,
            tables_by_negative_key=state.tables_by_negative_key,
            tables_by_binding_key=state.tables_by_binding_key,
            open_keys=state.open_keys,
            dirty_keys=dirty_keys,
            promoted_answers_by_key=state.promoted_answers_by_key,
            epoch=state.epoch,
            binding_epoch=binding_epoch,
            binding_epochs_by_key=frozendict(binding_epochs.items()),
            promoted_epoch=state.promoted_epoch,
        )
        return QuerySet(self, refreshed).continue_()
