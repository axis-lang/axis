from __future__ import annotations

from typing import Mapping, cast

from protobase import Consed, flux, frozendict

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Builtin

from .core import QueryCore
from .model import Answer, BindingsChanged, DeferredGoal, DirectCompletion, Judgment, NegativeCycleIssue, NonGroundNegation, PendingBranch
from .result import Ambiguous, Deferred, Floundered, MixedCycle, NegativeCycle, NoSolution, Unique
from .subst import canonicalize, canonicalize_branch_specs, goal_placeholder_info, goal_query_slot_indices, instantiate_query, make_union_find, public_goal, seed_query_bindings
from .tabling import QueryTable, StoredAnswer


class Query(Consed):
    session: urs.Session
    goal: protomorph.Spec

    @flux.property
    def semantic_goal(self):
        runtime_goal, _, slots = instantiate_query(self.goal)
        uf = make_union_find()
        placeholders = self.query_placeholders
        if not seed_query_bindings(uf, slots, placeholders, self.session.state.bindings):
            return None
        return canonicalize(runtime_goal, uf)

    @flux.property
    def query_placeholders(self) -> tuple[protomorph.Placeholder, ...]:
        _, placeholders, _ = instantiate_query(self.goal)
        return placeholders

    @flux.property
    def semantic_key(self) -> protomorph.Spec | None:
        semantic = self.semantic_goal
        return None if semantic is None else semantic.key

    @flux.property
    def table(self) -> urs.QueryTable:
        semantic = self.semantic_goal
        if semantic is None:
            return QueryTable(key=self.goal, origin=self.goal)
        cached = self.session.state.tables.query_tables.get(semantic.key)
        if cached is not None:
            return cached
        canonical_goal, _, outcome = QueryCore(self.session, self.goal).run()
        stored_answers = tuple(StoredAnswer(answer.subst, answer.evidence, answer.judgment) for answer in outcome.answers)
        deferred = tuple(_specialize_deferred(blocked, self.query_placeholders) for blocked in outcome.deferred)
        branches = tuple(_specialize_branch_wakes(branch, self.query_placeholders) for branch in outcome.branches)
        if not branches and deferred:
            info_by_placeholder = goal_placeholder_info(canonical_goal)
            branches = tuple(
                _specialize_branch_wakes(
                    _branch_from_canonical_deferred(blocked, info_by_placeholder, DirectCompletion(rel=canonical_goal.key)),
                    self.query_placeholders,
                )
                for blocked in outcome.deferred
            )
        frontier = tuple(blocked.goal for blocked in deferred)
        status = "cycle" if outcome.cycle_issue is not None else "blocked" if branches or deferred else "closed"
        closed = status in {"closed", "cycle"}
        return QueryTable(
            key=canonical_goal.key,
            origin=self.goal,
            query_slot_indices=goal_query_slot_indices(canonical_goal),
            status=status,
            answers=stored_answers,
            failures=outcome.failures,
            deferred=deferred,
            cycle_issue=outcome.cycle_issue,
            frontier=frontier,
            continuation_state=branches,
            active=bool(frontier),
            closed=closed,
            binding_epoch=self.session.state.binding_epoch,
            local_facts_epoch=self.session.state.local_facts_epoch,
            placeholders=self.query_placeholders,
        )

    @flux.property
    def result(self) -> urs.Result:
        semantic = self.semantic_goal
        if semantic is None:
            outcome: urs.SolverResult = NoSolution(
                self.goal,
                "conflicting seed bindings",
                _no_solution_judgment(self.goal, "conflicting seed bindings"),
            )
            return Result(self, outcome)
        public_answers = self.public_answers
        table = self.table

        if table.cycle_issue is not None:
            judgment = _cycle_judgment(self.goal, table.cycle_issue)
            if isinstance(table.cycle_issue, NegativeCycleIssue):
                outcome: urs.SolverResult = NegativeCycle(
                    self.goal,
                    table.cycle_issue.cycle,
                    table.cycle_issue.reason,
                    table.cycle_issue.trace,
                    judgment,
                )
            else:
                outcome = MixedCycle(
                    self.goal,
                    table.cycle_issue.cycle,
                    table.cycle_issue.reason,
                    table.cycle_issue.trace,
                    judgment,
                )
            next_session = self.session.with_query_table(semantic.key, table)
            return Result(self, outcome, next_session)

        if table.deferred:
            outcome_cls = Floundered if any(isinstance(blocked.blocker, NonGroundNegation) for blocked in table.deferred) else Deferred
            outcome = outcome_cls(
                self.goal,
                table.deferred,
                public_answers,
                _deferred_judgments(table.deferred, public_answers),
                "deferred",
            )
            next_session = self.session.with_query_table(semantic.key, table).with_deferred(table.deferred)
            return Result(self, outcome, next_session, next_session.query(self.goal))

        if not public_answers:
            outcome = NoSolution(
                self.goal,
                "no matching proof",
                _root_no_solution_judgment(self.goal, table.failures, "no matching proof"),
            )
            next_session = self.session.with_query_table(semantic.key, table)
            return Result(self, outcome, next_session)

        if len(public_answers) == 1:
            answer = public_answers[0]
            outcome = Unique(self.goal, answer.subst, answer.evidence, answer.judgment)
            next_session = self.session.with_query_table(semantic.key, table)
            if answer.subst:
                next_session = next_session.with_bindings(answer.subst)
            return Result(self, outcome, next_session)

        outcome = Ambiguous(
            self.goal,
            _shared_subst(public_answers),
            _shared_evidence(public_answers),
            public_answers,
            tuple(answer.judgment for answer in public_answers if answer.judgment is not None),
            "multiple answers",
        )
        next_session = self.session.with_query_table(semantic.key, table)
        return Result(self, outcome, next_session)

    @flux.property
    def public_answers(self) -> tuple[Answer, ...]:
        semantic = self.semantic_goal
        if semantic is None:
            return ()
        placeholders = self.query_placeholders
        return tuple(
            Answer(
                self.goal,
                _merge_visible_bindings(self.session.state.bindings.values, placeholders, semantic, answer.subst),
                answer.evidence,
                answer.judgment or Judgment(self.goal, answer.evidence),
            )
            for answer in self.table.answers
        )


class Result(Builtin):
    query: urs.Query
    outcome: urs.SolverResult
    next_session: urs.Session | None = None
    continuation: urs.Query | None = None

    @property
    def can_continue(self) -> bool:
        return self.continuation is not None

    def resume(self) -> urs.Result:
        if self.continuation is None:
            return self
        return self.continuation.result


def _merge_visible_bindings(
    seed: frozendict[protomorph.Placeholder, urs.ReasoningValue],
    placeholders: tuple[protomorph.Placeholder, ...],
    canonical_goal,
    subst,
) -> frozendict[protomorph.Placeholder, urs.ReasoningValue]:
    from .subst import public_subst

    merged = dict(seed)
    merged.update(public_subst(placeholders, canonical_goal, subst))
    return frozendict(cast(tuple[tuple[protomorph.Placeholder, urs.ReasoningValue], ...], tuple(merged.items())))


def _shared_subst(answers: tuple[urs.Answer, ...]) -> frozendict[protomorph.Placeholder, urs.ReasoningValue]:
    shared = dict(answers[0].subst)
    for answer in answers[1:]:
        current = dict(answer.subst)
        for key, value in tuple(shared.items()):
            if key not in current or current[key] != value:
                shared.pop(key)
    return frozendict(cast(tuple[tuple[protomorph.Placeholder, urs.ReasoningValue], ...], tuple(shared.items())))


def _shared_evidence(answers: tuple[urs.Answer, ...]) -> protomorph.Spec | None:
    first = answers[0].evidence
    if all(answer.evidence == first for answer in answers):
        return first
    return None


def _deferred_judgments(blocked: tuple[urs.DeferredGoal, ...], answers: tuple[urs.Answer, ...]) -> tuple[urs.Judgment, ...]:
    ordered: list[urs.Judgment] = []
    seen: dict[urs.Judgment, None] = {}
    for judgment in (item.judgment for item in blocked):
        if judgment is None or judgment in seen:
            continue
        seen[judgment] = None
        ordered.append(judgment)
    for judgment in (answer.judgment for answer in answers):
        if judgment is None or judgment in seen:
            continue
        seen[judgment] = None
        ordered.append(judgment)
    return tuple(ordered)


def _cycle_judgment(goal: protomorph.Spec, issue) -> urs.Judgment:
    trace = issue.trace
    if isinstance(issue, NegativeCycleIssue):
        evidence = protomorph.Spec.of("std.logic.ByNegativeCycle", goal, trace if trace is not None else issue.cycle)
    else:
        evidence = protomorph.Spec.of("std.logic.ByMixedCycle", goal, trace if trace is not None else issue.cycle)
    return Judgment(goal, evidence, trace=trace)


def _no_solution_judgment(goal: protomorph.Spec, reason: str) -> urs.Judgment:
    evidence = protomorph.Spec.of("std.logic.ByNoSolution", goal, reason)
    return Judgment(goal, evidence)


def _root_no_solution_judgment(goal: protomorph.Spec, failures: tuple[urs.Judgment, ...], reason: str) -> urs.Judgment:
    if not failures:
        return _no_solution_judgment(goal, reason)
    return Judgment(goal, protomorph.Spec.of("std.logic.ByNoSolution", goal, reason), failures)


def _specialize_deferred(blocked, placeholders: tuple[protomorph.Placeholder, ...]):
    wakes = []
    for wake in blocked.wake_on:
        if isinstance(wake, BindingsChanged) and not wake.placeholders:
            wakes.append(BindingsChanged(placeholders))
        else:
            wakes.append(wake)
    return blocked.__class__(public_goal(blocked.goal, placeholders), blocked.blocker, blocked.evidence, tuple(wakes), blocked.judgment)


def _specialize_branch(branch: urs.PendingBranch, placeholders: tuple[protomorph.Placeholder, ...]) -> urs.PendingBranch:
    return PendingBranch(
        blocked=_specialize_deferred(branch.blocked, placeholders),
        remaining_goals=tuple(public_goal(goal, placeholders) for goal in branch.remaining_goals),
        subst=branch.subst,
        slot_info=branch.slot_info,
        blocked_is_negated=branch.blocked_is_negated,
        completion=branch.completion,
        subjudgments=branch.subjudgments,
    )


def _specialize_branch_wakes(branch: urs.PendingBranch, placeholders: tuple[protomorph.Placeholder, ...]) -> urs.PendingBranch:
    return PendingBranch(
        blocked=_specialize_deferred(branch.blocked, placeholders),
        remaining_goals=branch.remaining_goals,
        subst=branch.subst,
        slot_info=branch.slot_info,
        blocked_is_negated=branch.blocked_is_negated,
        completion=branch.completion,
        subjudgments=branch.subjudgments,
    )


def _branch_from_canonical_deferred(
    blocked: urs.DeferredGoal,
    info_by_placeholder: Mapping[protomorph.Placeholder, urs.EqClassInfo | None],
    completion,
) -> urs.PendingBranch:
    canonical_goal, remaining_goals, subst, slot_info = canonicalize_branch_specs(blocked.goal, (), info_by_placeholder)
    return PendingBranch(
        blocked=DeferredGoal(canonical_goal, blocked.blocker, blocked.evidence, blocked.wake_on, blocked.judgment),
        remaining_goals=remaining_goals,
        subst=subst,
        slot_info=slot_info,
        blocked_is_negated=False,
        completion=completion,
    )
