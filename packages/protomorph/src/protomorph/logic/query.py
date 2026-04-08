from __future__ import annotations

from typing import TYPE_CHECKING

from protobase import Consed

import protomorph as pm

from .canonical import canonicalize_goal, ordered_placeholders, public_answer
from .model import Cycle, Edge

if TYPE_CHECKING:
    from .model import (
        Answer,
        Ambiguous,
        Deferred,
        Floundered,
        InsufficientBindings,
        MissingProof,
        NoSolution,
        QueryRoot,
        QueryTable,
        SolverResult,
        Unique,
    )
    from .queryset import QuerySet
else:
    Answer = pm.Builtin
    Ambiguous = pm.Builtin
    Deferred = pm.Builtin
    Floundered = pm.Builtin
    InsufficientBindings = pm.Builtin
    MissingProof = pm.Builtin
    NoSolution = pm.Builtin
    QueryRoot = pm.Builtin
    QueryTable = pm.Builtin
    SolverResult = pm.Builtin
    Unique = pm.Builtin
    QuerySet = pm.Builtin


class Query(Consed):
    queryset: QuerySet
    goal: pm.Val

    @property
    def root(self) -> QueryRoot:
        for root in self.queryset.state.roots:
            if root.goal == self.goal:
                return root
        canonical = canonicalize_goal(self.goal)
        from .model import QueryRoot

        return QueryRoot(self.goal, canonical.key, ordered_placeholders(self.goal))

    @property
    def table(self) -> QueryTable:
        return self.queryset.state.tables_by_key.get(self.root.table_key, self.queryset.table(self.goal))

    @property
    def answers(self) -> tuple[Answer, ...]:
        answers = tuple(public_answer(self.goal, self.root.placeholders, answer) for answer in self.table.answers)
        if self.root.placeholders:
            answers = tuple(answer for answer in answers if answer.subst)
        deduped: dict[tuple[tuple[pm.Placeholder, pm.Val], ...], Answer] = {}
        for answer in answers:
            deduped[tuple(answer.subst.items())] = answer
        return tuple(deduped.values())

    @property
    def is_blocked(self) -> bool:
        return self.table.is_blocked

    @property
    def is_closed(self) -> bool:
        return self.table.closed

    @property
    def result(self) -> SolverResult:
        from .model import Ambiguous, Deferred, Floundered, InsufficientBindings, MissingProof, NoSolution, Unique

        table = self.table
        answers = self.answers

        if table.cycle_issue is not None:
            return NoSolution(self.goal, _public_cycle(self.queryset, table.cycle_issue.cycle))

        if table.pending:
            outcome_cls = Floundered if any(isinstance(branch.blocker, InsufficientBindings) for branch in table.pending) else Deferred
            return outcome_cls(self.goal, table.pending, answers, table.failures)

        if not answers:
            judgment = table.failures[0] if table.failures else None
            return NoSolution(self.goal, MissingProof(judgment))

        if len(answers) == 1:
            return Unique(self.goal, answers[0])

        return Ambiguous(self.goal, answers)

    def continue_(self) -> Query:
        queryset = self.queryset.continue_()
        return Query(queryset, self.goal)


def _public_cycle(queryset: QuerySet, cycle: Cycle) -> Cycle:
    solver = queryset.session.solver
    return Cycle.of(
        *(
            Edge(solver.head_key(edge.from_), solver.head_key(edge.to), edge.affirmative)
            for edge in cycle.edges
        )
    )
