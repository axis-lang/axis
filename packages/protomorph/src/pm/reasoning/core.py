from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from protobase import frozendict

import pm
from pm import reasoning as urs
from pm.unification import UnionFind, unify

from .model import (
    BranchCompletion,
    CycleMember,
    CycleTrace,
    Judgment,
    CycleIssue,
    DeferredGoal,
    DirectCompletion,
    ExpandCompletion,
    MixedCycleIssue,
    NegativeCycleIssue,
    NonGroundNegation,
    OperatorPending,
    PendingBranch,
    ProjectionBlocked,
    Rule,
    RuleCompletion,
    StratumPending,
    TypeFunctionBlocked,
    default_wake_on,
    is_negation,
    unwrap_negation,
)
from .operators import OpAnswer, OpBind, OpDeferred, OpExpand, OpFailed, SolverOperator, relation_operator_for
from .subst import (
    CanonicalGoal,
    apply_answer,
    branch_placeholder_info,
    canonicalize,
    canonicalize_branch,
    canonicalize_branch_specs,
    compile_template,
    contains_goal_slots,
    extract_branch_answer,
    extract_visible_subst,
    goal_query_slot_indices,
    goal_slot_index_of,
    instantiate_query,
    instantiate_template,
    materialize_branch_goals,
    make_union_find,
    rebuild_branch_env,
    rule_context_for,
    seed_query_bindings,
    wrap_logic,
)
from .vars import EqClassInfo, RuleAppCtx, RuleCtx


class _CompiledLiteral(pm.Builtin):
    goal: pm.Carrier
    negated: bool = False


class _CompiledRule(pm.Builtin):
    rule: urs.Rule
    ctx: urs.RuleCtx
    head: pm.Carrier
    body: tuple[_CompiledLiteral, ...]


class _AnswerData(pm.Builtin):
    subst: tuple[tuple[int, pm.Carrier], ...]
    evidence: pm.Spec | None = None
    judgment: urs.Judgment | None = None


class _GoalOutcome(pm.Builtin):
    answers: tuple[_AnswerData, ...] = ()
    deferred: tuple[urs.DeferredGoal, ...] = ()
    branches: tuple[urs.PendingBranch, ...] = ()
    cycle_issue: urs.CycleIssue | None = None
    failures: tuple[urs.Judgment, ...] = ()


class _ResumeBranchResult(pm.Builtin):
    answers: tuple[_AnswerData, ...] = ()
    branches: tuple[urs.PendingBranch, ...] = ()
    cycle_issue: urs.CycleIssue | None = None
    failures: tuple[urs.Judgment, ...] = ()


@dataclass(slots=True)
class _ActiveFrame:
    goal: pm.Spec
    coinductive: bool = False
    via_negation: bool = False


@dataclass(slots=True)
class _GoalEntry:
    active: bool = False
    closed: bool = False
    coinductive: bool = False
    answers: dict[tuple[tuple[int, pm.Carrier], ...], _AnswerData] = field(default_factory=dict)
    deferred: dict[tuple[pm.Spec, object], DeferredGoal] = field(default_factory=dict)
    branches: dict[
        tuple[
            urs.DeferredGoal,
            tuple[pm.Spec, ...],
            tuple[tuple[int, pm.Carrier], ...],
            tuple[urs.EqClassInfo | None, ...],
        ],
        urs.PendingBranch,
    ] = field(default_factory=dict)
    cycle_issue: urs.CycleIssue | None = None
    failures: dict[urs.Judgment, None] = field(default_factory=dict)

    def outcome(self) -> _GoalOutcome:
        return _GoalOutcome(
            tuple(self.answers.values()),
            tuple(self.deferred.values()),
            tuple(self.branches.values()),
            self.cycle_issue,
            tuple(self.failures),
        )


class _QueryCore:
    def __init__(self, session: urs.Session, goal: pm.Spec):
        self.session = session
        self.goal = goal
        self.engine = session.engine
        self._compiled_rules: dict[urs.Rule, _CompiledRule] = {}
        self._tables: dict[pm.Spec, _GoalEntry] = {}
        self._next_owner = 1
        self._active_stack: list[_ActiveFrame] = []

    def run(self) -> tuple[CanonicalGoal, tuple[pm.Placeholder, ...], _GoalOutcome]:
        runtime_goal, placeholders, slots = instantiate_query(self.goal)
        uf = make_union_find()
        if not seed_query_bindings(uf, slots, placeholders, self.session.state.bindings):
            return CanonicalGoal(self.goal, ()), placeholders, _GoalOutcome()
        canonical_goal = canonicalize(runtime_goal, uf)
        outcome = self._solve_goal(canonical_goal)
        return canonical_goal, placeholders, outcome

    def _solve_goal(self, goal: CanonicalGoal, *, via_negation: bool = False) -> _GoalOutcome:
        if self.engine.strata.has_negative_cycle(str(goal.key.anchor)):
            trace = self.engine.strata.negative_cycle_trace(str(goal.key.anchor)) or CycleTrace(
                (CycleMember(goal.key, self.engine.db.is_coinductive_anchor(str(goal.key.anchor)), via_negation),),
                "negative",
                "negative cycle in stratification",
                via_negation,
            )
            return _GoalOutcome(cycle_issue=NegativeCycleIssue((goal.key,), trace.reason, trace))

        coinductive = self.engine.db.is_coinductive_anchor(str(goal.key.anchor))

        entry = self._tables.get(goal.key)
        if entry is not None:
            if entry.active or entry.closed:
                if entry.active:
                    cycle = self._active_cycle(goal.key, coinductive, via_negation)
                    if cycle is not None:
                        return cycle
                return entry.outcome()

        entry = _GoalEntry(active=True, coinductive=coinductive)
        self._tables[goal.key] = entry
        self._active_stack.append(_ActiveFrame(goal.key, coinductive, via_negation))

        while True:
            changed = False

            for answer in self._fact_answers(goal):
                if answer.subst not in entry.answers:
                    entry.answers[answer.subst] = answer
                    changed = True

            operator_outcome = self._operator_outcome(goal)
            changed |= self._merge_outcome(entry, operator_outcome)
            if entry.cycle_issue is not None:
                break

            for rule in self.engine.rules_for_anchor(str(goal.key.anchor)):
                changed |= self._merge_outcome(entry, self._rule_outcome(goal, rule))
                if entry.cycle_issue is not None:
                    break

            if entry.cycle_issue is not None or not changed:
                break

        entry.active = False
        entry.closed = True
        self._active_stack.pop()
        return entry.outcome()

    def _active_cycle(self, goal: pm.Spec, coinductive: bool, via_negation: bool = False) -> _GoalOutcome | None:
        index = next((i for i, frame in enumerate(self._active_stack) if frame.goal == goal), -1)
        if index < 0:
            return None
        trace = self._cycle_trace(index, goal, coinductive, via_negation)
        if trace.kind == "negative":
            return _GoalOutcome(cycle_issue=NegativeCycleIssue(tuple(member.goal for member in trace.members), trace.reason, trace))
        if trace.kind == "mixed":
            return _GoalOutcome(cycle_issue=MixedCycleIssue(tuple(member.goal for member in trace.members), trace.reason, trace))
        if trace.kind == "coinductive":
            evidence = _evidence_coinduction(goal)
            return _GoalOutcome(answers=(_AnswerData((), evidence, Judgment(goal, evidence, trace=trace)),))
        return None

    def _cycle_trace(self, index: int, goal: pm.Spec, coinductive: bool, via_negation: bool) -> urs.CycleTrace:
        frames = self._active_stack[index:]
        members = tuple(CycleMember(frame.goal, frame.coinductive, frame.via_negation) for frame in frames)
        internal_negative = via_negation or any(frame.via_negation for frame in frames[1:])
        any_coinductive = any(frame.coinductive for frame in frames) or coinductive
        any_inductive = any(not frame.coinductive for frame in frames) or not coinductive
        if internal_negative:
            return CycleTrace(members, "negative", "negative cycle in active goals", via_negation)
        if any_coinductive and any_inductive:
            return CycleTrace(members, "mixed", "mixed inductive/coinductive cycle", via_negation)
        if all(frame.coinductive for frame in frames) and coinductive:
            return CycleTrace(members, "coinductive", "coinductive cycle", via_negation)
        return CycleTrace(members, "inductive", "inductive cycle", via_negation)

    def _fact_answers(self, goal: CanonicalGoal) -> tuple[_AnswerData, ...]:
        goal_runtime = self._instantiate_goal(goal)
        answers: list[_AnswerData] = []
        for fact in self._facts_for_anchor(str(goal.key.anchor)):
            uf = make_union_find()
            if unify(goal_runtime, wrap_logic(fact), subst=uf) is None:
                continue
            evidence = _evidence_fact(fact)
            answers.append(_AnswerData(extract_visible_subst(goal, uf), evidence, Judgment(goal.key, evidence)))
        return tuple(answers)

    def _operator_outcome(self, goal: CanonicalGoal) -> _GoalOutcome:
        operator = relation_operator_for(goal.key)
        if operator is None:
            operator = self._first_operator(goal.key)
        if operator is None:
            return _GoalOutcome()

        step = operator.eval(goal=goal.key, session=self.session, db=self.engine.db)
        if isinstance(step, OpDeferred):
            return _GoalOutcome(deferred=(step.blocked,))
        if isinstance(step, OpFailed):
            return _GoalOutcome(failures=(_failure_judgment(goal.key, step.reason or "operator failed"),))
        if isinstance(step, OpBind):
            answer = self._from_bound_answer(goal, step)
            return _GoalOutcome(answers=(answer,))
        if isinstance(step, OpAnswer):
            answers = tuple(self._from_public_answer(goal, answer) for answer in step.answers)
            return _GoalOutcome(answers=answers)
        if isinstance(step, OpExpand):
            return self._expanded_outcome(goal, step.goals)
        return _GoalOutcome()

    def _expanded_outcome(self, goal: CanonicalGoal, goals: tuple[pm.Spec, ...]) -> _GoalOutcome:
        answers: list[_AnswerData] = []
        deferred: list[DeferredGoal] = []
        branches: list[PendingBranch] = []
        cycle_issue: urs.CycleIssue | None = None
        failures: list[Judgment] = []

        uf = make_union_find()
        if unify(self._instantiate_goal(goal), self._instantiate_goal(goal), subst=uf) is None:
            return _GoalOutcome()

        def solve_body(index: int, subjudgments: tuple[urs.Judgment, ...]) -> None:
            nonlocal cycle_issue
            if index == len(goals):
                evidence = _evidence_expand(goal.key, subjudgments)
                answers.append(_AnswerData(extract_visible_subst(goal, uf), evidence, Judgment(goal.key, evidence, subjudgments)))
                return

            subgoal = canonicalize(uf.reify(wrap_logic(goals[index])), uf)
            outcome = self._solve_goal(subgoal)
            if outcome.cycle_issue is not None:
                cycle_issue = outcome.cycle_issue
                return
            if outcome.deferred:
                deferred.extend(outcome.deferred)
                blocked_carrier = wrap_logic(goals[index])
                remaining_carriers = tuple(wrap_logic(goal) for goal in goals[index + 1 :])
                branches.extend(
                    self._persist_runtime_branch(
                        blocked,
                        blocked_carrier,
                        remaining_carriers,
                        uf,
                        False,
                        ExpandCompletion(rel=goal.key, subject=goal.key),
                        subjudgments,
                    )
                    for blocked in outcome.deferred
                )
                return
            if not outcome.answers:
                failures.append(_failure_judgment(goal.key, "expanded subgoal failed", _preferred_failures(outcome, subgoal.key)))
                return
            for answer in outcome.answers:
                snap = uf.snapshot()
                if apply_answer(uf, subgoal, answer.subst):
                    judgment = answer.judgment or Judgment(subgoal.key, answer.evidence)
                    solve_body(index + 1, (*subjudgments, judgment))
                uf.rollback(snap)

        solve_body(0, ())
        return _GoalOutcome(tuple(answers), tuple(_dedupe_deferred(deferred)), tuple(branches), cycle_issue, tuple(_dedupe_judgments(failures)))

    def _rule_outcome(self, goal: CanonicalGoal, rule: urs.Rule) -> _GoalOutcome:
        compiled = self._compile_rule(rule)
        app_ctx = self._new_rule_app_ctx(goal.key, compiled.ctx)
        goal_runtime = self._instantiate_goal(goal)
        uf = make_union_find()
        if unify(goal_runtime, instantiate_template(compiled.head, app_ctx), subst=uf) is None:
            return _GoalOutcome()

        answers: list[_AnswerData] = []
        deferred: list[DeferredGoal] = []
        branches: list[PendingBranch] = []
        cycle_issue: urs.CycleIssue | None = None
        failures: list[Judgment] = []

        def solve_body(index: int, subjudgments: tuple[urs.Judgment, ...]) -> None:
            nonlocal cycle_issue
            if index == len(compiled.body):
                evidence = _evidence_rule(rule, subjudgments)
                answers.append(_AnswerData(extract_visible_subst(goal, uf), evidence, Judgment(goal.key, evidence, subjudgments)))
                return

            literal = compiled.body[index]
            subgoal_carrier = uf.reify(instantiate_template(literal.goal, app_ctx))
            subgoal = canonicalize(subgoal_carrier, uf)

            cycle = self._active_cycle(subgoal.key, self.engine.db.is_coinductive_anchor(str(subgoal.key.anchor)), literal.negated)
            if cycle is not None:
                if cycle.cycle_issue is not None:
                    cycle_issue = cycle.cycle_issue
                    return
                if cycle.answers:
                    for answer in cycle.answers:
                        snap = uf.snapshot()
                        if apply_answer(uf, subgoal, answer.subst):
                            judgment = answer.judgment or Judgment(subgoal.key, answer.evidence)
                            solve_body(index + 1, (*subjudgments, judgment))
                        uf.rollback(snap)
                    return

            if literal.negated:
                negative = self._negative_outcome(goal, subgoal)
                if negative.cycle_issue is not None:
                    cycle_issue = negative.cycle_issue
                    return
                if negative.deferred:
                    deferred.extend(negative.deferred)
                    remaining = tuple(instantiate_template(literal.goal, app_ctx) for literal in compiled.body[index + 1 :])
                    blocked_carrier = instantiate_template(literal.goal, app_ctx)
                    branches.extend(
                        self._persist_runtime_branch(
                            blocked,
                            blocked_carrier,
                            remaining,
                            uf,
                            True,
                            RuleCompletion(rel=goal.key, rule_head=rule.head),
                            subjudgments,
                        )
                        for blocked in negative.deferred
                    )
                    return
                if negative.failures:
                    failures.append(_failure_judgment(goal.key, "negated goal succeeded", (*subjudgments, *negative.failures)))
                    return
                judgment = _negation_judgment(subgoal.key)
                solve_body(index + 1, (*subjudgments, judgment))
                return

            outcome = self._solve_goal(subgoal)
            if outcome.cycle_issue is not None:
                cycle_issue = outcome.cycle_issue
                return
            if outcome.deferred:
                deferred.extend(outcome.deferred)
                remaining = tuple(instantiate_template(item.goal, app_ctx) for item in compiled.body[index + 1 :])
                blocked_carrier = instantiate_template(literal.goal, app_ctx)
                branches.extend(
                    self._persist_runtime_branch(
                        blocked,
                        blocked_carrier,
                        remaining,
                        uf,
                        False,
                        RuleCompletion(rel=goal.key, rule_head=rule.head),
                        subjudgments,
                    )
                    for blocked in outcome.deferred
                )
                return
            if not outcome.answers:
                failures.append(_failure_judgment(goal.key, "rule subgoal failed", (*subjudgments, *_preferred_failures(outcome, subgoal.key))))
                return

            for answer in outcome.answers:
                snap = uf.snapshot()
                if apply_answer(uf, subgoal, answer.subst):
                    judgment = answer.judgment or Judgment(subgoal.key, answer.evidence)
                    solve_body(index + 1, (*subjudgments, judgment))
                uf.rollback(snap)

        solve_body(0, ())
        return _GoalOutcome(tuple(answers), tuple(_dedupe_deferred(deferred)), tuple(branches), cycle_issue, tuple(_dedupe_judgments(failures)))

    def _negative_outcome(self, parent: CanonicalGoal, goal: CanonicalGoal) -> _GoalOutcome:
        if goal.slots:
            return _GoalOutcome(deferred=(_deferred_goal(goal.key, NonGroundNegation(goal.key)),))

        target_anchor = str(goal.key.anchor)
        if self.engine.strata.has_negative_cycle(target_anchor):
            trace = self.engine.strata.negative_cycle_trace(target_anchor) or CycleTrace(
                (CycleMember(goal.key, self.engine.db.is_coinductive_anchor(target_anchor), True),),
                "negative",
                "negative cycle in stratification",
                True,
            )
            return _GoalOutcome(cycle_issue=NegativeCycleIssue((goal.key,), trace.reason, trace))

        parent_stratum = self.engine.strata.stratum_of(str(parent.key.anchor))
        target_stratum = self.engine.strata.stratum_of(target_anchor)
        if target_stratum >= parent_stratum:
            return _GoalOutcome(deferred=(_deferred_goal(goal.key, StratumPending(target_stratum, goal.key)),))

        if target_stratum not in self.engine.global_tables.closed_strata:
            return _GoalOutcome(deferred=(_deferred_goal(goal.key, StratumPending(target_stratum, goal.key)),))

        outcome = self._solve_goal(goal, via_negation=True)
        if outcome.cycle_issue is not None:
            return outcome
        if outcome.deferred:
            return outcome
        if outcome.answers:
            failures = tuple(
                judgment
                for judgment in (answer.judgment or Judgment(goal.key, answer.evidence) for answer in outcome.answers)
                if judgment is not None
            )
            return _GoalOutcome(failures=tuple(_dedupe_judgments(failures)))
        return _GoalOutcome()

    def _compile_rule(self, rule: urs.Rule) -> _CompiledRule:
        cached = self._compiled_rules.get(rule)
        if cached is not None:
            return cached
        rule_ctx = rule_context_for(rule)
        slot_by_placeholder: dict[pm.Placeholder, int] = {}
        body: list[_CompiledLiteral] = []
        for item in rule.body:
            if is_negation(item):
                body.append(_CompiledLiteral(compile_template(unwrap_negation(item), rule_ctx, slot_by_placeholder), True))
            else:
                body.append(_CompiledLiteral(compile_template(item, rule_ctx, slot_by_placeholder), False))
        compiled = _CompiledRule(rule, rule_ctx, compile_template(rule.head, rule_ctx, slot_by_placeholder), tuple(body))
        self._compiled_rules[rule] = compiled
        return compiled

    def _facts_for_anchor(self, anchor: str) -> tuple[pm.Spec, ...]:
        local = tuple(fact for fact in self.session.state.local_facts if str(fact.anchor) == anchor)
        contextual = self.session.state.tables.answers_by_anchor.get(anchor, ())
        return (*self.engine.facts_for_anchor(anchor), *contextual, *local)

    def _instantiate_goal(self, goal: CanonicalGoal) -> pm.Carrier:
        return instantiate_goal_slots(wrap_logic(goal.key), goal.slots)

    def _merge_outcome(self, entry: _GoalEntry, outcome: _GoalOutcome) -> bool:
        changed = False
        for answer in outcome.answers:
            current = entry.answers.get(answer.subst)
            if current is None:
                entry.answers[answer.subst] = answer
                changed = True
                continue
            if _answer_score(answer) > _answer_score(current):
                entry.answers[answer.subst] = answer
                changed = True
        for blocked in outcome.deferred:
            key = (blocked.goal, blocked.blocker)
            if key not in entry.deferred:
                entry.deferred[key] = blocked
                changed = True
        for branch in outcome.branches:
            key = (branch.blocked, branch.remaining_goals, branch.subst, branch.slot_info)
            if key not in entry.branches:
                entry.branches[key] = branch
                changed = True
        for failure in outcome.failures:
            if failure not in entry.failures:
                entry.failures[failure] = None
                changed = True
        if entry.cycle_issue is None and outcome.cycle_issue is not None:
            entry.cycle_issue = outcome.cycle_issue
            changed = True
        return changed

    def _first_operator(self, goal: pm.Spec) -> SolverOperator | None:
        return _search_operator(goal)

    def _from_public_answer(self, goal: CanonicalGoal, answer: pm.Builtin) -> _AnswerData:
        from .model import Answer

        public_answer = answer
        if not isinstance(public_answer, Answer):
            raise TypeError("OpAnswer expects reasoning.Answer values")

        uf = make_union_find()
        query_placeholders = self.session.query(self.goal).query_placeholders
        if not seed_query_bindings(uf, goal.slots, query_placeholders, self.session.state.bindings):
            raise ValueError("Conflicting session bindings for operator answer")

        query_slot_indices = goal_query_slot_indices(goal)
        slot_by_placeholder = {
            query_placeholders[query_slot_indices[index]]: goal.slots[index]
            for index in range(len(goal.slots))
        }
        for placeholder, value in public_answer.subst.items():
            slot = slot_by_placeholder.get(placeholder)
            if slot is None:
                continue
            if unify(slot, _coerce_bound_value_for_carrier(slot, value), subst=uf) is None:
                raise ValueError(f"Conflicting operator answer for placeholder {placeholder!r}")

        judgment = public_answer.judgment or Judgment(goal.key, public_answer.evidence)
        return _AnswerData(extract_visible_subst(goal, uf), public_answer.evidence, judgment)

    def _from_bound_answer(self, goal: CanonicalGoal, step: OpBind) -> _AnswerData:
        subst: list[tuple[int, pm.Carrier]] = []
        for slot, value in step.subst:
            if slot < 0 or slot >= len(goal.slots):
                continue
            subst.append((slot, _coerce_bound_value(goal, slot, value)))
        evidence = step.evidence
        return _AnswerData(tuple(subst), evidence, Judgment(goal.key, evidence))

    def _new_rule_app_ctx(self, parent_goal: pm.Spec, rule_ctx: urs.RuleCtx) -> RuleAppCtx:
        owner = self._next_owner
        self._next_owner += 1
        return RuleAppCtx(parent_goal, rule_ctx, owner)

    def _persist_runtime_branch(
        self,
        blocked: urs.DeferredGoal,
        blocked_carrier: pm.Carrier,
        remaining_carriers: tuple[pm.Carrier, ...],
        uf: UnionFind,
        blocked_is_negated: bool,
        completion: urs.BranchCompletion,
        subjudgments: tuple[urs.Judgment, ...],
    ) -> urs.PendingBranch:
        blocked_goal, remaining_goals, subst, slot_info = canonicalize_branch(blocked_carrier, remaining_carriers, uf)
        return PendingBranch(
            blocked=DeferredGoal(blocked_goal, blocked.blocker, blocked.evidence, blocked.wake_on, blocked.judgment),
            remaining_goals=remaining_goals,
            subst=subst,
            slot_info=slot_info,
            blocked_is_negated=blocked_is_negated,
            completion=completion,
            subjudgments=subjudgments,
        )


class _SessionSolveCore:
    def __init__(self, session: urs.Session):
        self.session = session

    def run(self) -> urs.Session:
        session = self.session
        while True:
            before = _session_signature(session)
            open_tables = self._open_tables(session)
            session = session.clear_deferred()
            for table in open_tables:
                if not self._should_retry_table(table, session):
                    session = session.with_query_table(table.key, table).with_deferred(table.deferred)
                    continue
                retry_base = session.without_goal(table.key)
                resumed_table = self._resume_table(table, retry_base)
                session = retry_base.with_query_table(table.key, resumed_table).with_deferred(resumed_table.deferred)
            if _session_signature(session) == before:
                return session

    def _open_tables(self, session: urs.Session) -> tuple:
        candidates: dict[pm.Spec, object] = {}
        tables = session.state.tables.query_tables
        has_targeted_updates = bool(session.state.recent_binding_updates or session.state.recent_local_fact_anchors)

        for placeholder in session.state.recent_binding_updates:
            for key in session.state.tables.deferred_by_placeholder.get(placeholder, ()):
                table = tables.get(key)
                if table is not None:
                    candidates[key] = table

        for anchor in session.state.recent_local_fact_anchors:
            for key in session.state.tables.deferred_by_anchor.get(anchor, ()):
                table = tables.get(key)
                if table is not None:
                    candidates[key] = table

        for table in tables.values():
            if table.origin is None or (not table.active and table.closed):
                continue
            if _has_generic_wake(table) or (not has_targeted_updates and not candidates):
                candidates[table.key] = table

        return tuple(candidates.values())

    def _should_retry_table(self, table, session: urs.Session) -> bool:
        if not table.continuation_state:
            return False
        for branch in table.continuation_state:
            if any(self._wake_satisfied(table, wake, session) for wake in branch.blocked.wake_on):
                return True
        return False

    def _resume_table(self, table, session: urs.Session):
        next_branches: list[urs.PendingBranch] = []
        answers_by_subst: dict[tuple[tuple[int, pm.Carrier], ...], urs.StoredAnswer] = {
            answer.subst: answer for answer in table.answers
        }
        failures = list(table.failures)
        cycle_issue = table.cycle_issue

        for branch in table.continuation_state:
            resumed = self._resume_branch(branch, table, session)
            if resumed.cycle_issue is not None:
                cycle_issue = resumed.cycle_issue
            for answer in resumed.answers:
                stored = urs.StoredAnswer(answer.subst, answer.evidence, answer.judgment)
                current = answers_by_subst.get(stored.subst)
                if current is None or _stored_answer_score(stored) > _stored_answer_score(current):
                    answers_by_subst[stored.subst] = stored
            next_branches.extend(resumed.branches)
            failures.extend(resumed.failures)

        deferred = tuple(branch.blocked for branch in next_branches)
        frontier = tuple(branch.blocked.goal for branch in next_branches)
        status = "cycle" if cycle_issue is not None else "blocked" if next_branches else "closed"
        resumed_table = urs.QueryTable(
            key=table.key,
            origin=table.origin,
            query_slot_indices=table.query_slot_indices,
            status=status,
            answers=tuple(answers_by_subst.values()),
            failures=tuple(_dedupe_judgments(failures)),
            deferred=deferred,
            cycle_issue=cycle_issue,
            frontier=frontier,
            continuation_state=tuple(next_branches),
            active=bool(next_branches),
            closed=status in {"closed", "cycle"},
            binding_epoch=session.state.binding_epoch,
            local_facts_epoch=session.state.local_facts_epoch,
            placeholders=table.placeholders,
        )
        return resumed_table

    def _resume_branch(self, branch: urs.PendingBranch, table, session: urs.Session) -> _ResumeBranchResult:
        env = rebuild_branch_env(branch, session.state.bindings)
        if env is None:
            return _ResumeBranchResult()

        uf, current_carrier, remaining_carriers, slots = env
        return self._resume_branch_state(
            branch,
            table,
            session,
            uf,
            current_carrier,
            remaining_carriers,
            slots,
            branch.subjudgments,
            branch.blocked_is_negated,
        )

    def _resume_branch_state(
        self,
        branch: urs.PendingBranch,
        table,
        session: urs.Session,
        uf: UnionFind,
        current_carrier: pm.Carrier,
        remaining_carriers: tuple[pm.Carrier, ...],
        slots: tuple[pm.Carrier, ...],
        subjudgments: tuple[urs.Judgment, ...],
        current_is_negated: bool,
    ) -> _ResumeBranchResult:
        while True:
            current_goal = canonicalize(uf.reify(current_carrier), uf)
            outcome = self._solve_canonical_goal(session, current_goal)

            if outcome.cycle_issue is not None:
                return _ResumeBranchResult(cycle_issue=outcome.cycle_issue)

            if outcome.branches:
                trailing_goals = _specs_from_carriers(remaining_carriers, uf)
                outer_info = branch_placeholder_info(branch)
                return _ResumeBranchResult(
                    branches=tuple(
                        self._persist_spec_branch(
                            inner,
                            trailing_goals,
                            cast(dict[pm.Placeholder, EqClassInfo | None], {**outer_info, **branch_placeholder_info(inner)}),
                            branch.completion,
                            (*subjudgments, *inner.subjudgments),
                        )
                        for inner in outcome.branches
                    )
                )

            if outcome.deferred:
                return _ResumeBranchResult(
                    branches=tuple(
                        self._persist_resumed_branch(
                            blocked,
                            current_carrier,
                            remaining_carriers,
                            uf,
                            current_is_negated,
                            branch.completion,
                            subjudgments,
                        )
                        for blocked in outcome.deferred
                    )
                )

            if current_is_negated:
                if outcome.answers:
                    failures = tuple(
                        judgment
                        for judgment in (answer.judgment or Judgment(current_goal.key, answer.evidence) for answer in outcome.answers)
                        if judgment is not None
                    )
                    return _ResumeBranchResult(failures=(_failure_judgment(current_goal.key, "negated goal succeeded", failures),))
                judgment = _negation_judgment(current_goal.key)
                subjudgments = (*subjudgments, judgment)
                if not remaining_carriers:
                    completed = self._complete_branch(branch, table, current_goal, _AnswerData((), judgment.evidence, judgment), subjudgments, slots, uf)
                    if completed is None:
                        return _ResumeBranchResult(failures=(_failure_judgment(current_goal.key, "no matching proof", subjudgments),))
                    return _ResumeBranchResult(answers=(completed,))
                current_carrier, remaining_carriers = remaining_carriers[0], remaining_carriers[1:]
                current_is_negated = False
                continue

            if not outcome.answers:
                return _ResumeBranchResult(failures=_preferred_failures(outcome, current_goal.key))

            if len(outcome.answers) != 1:
                return self._resume_branch_answers(
                    branch,
                    table,
                    session,
                    current_goal,
                    outcome.answers,
                    remaining_carriers,
                    slots,
                    uf,
                    subjudgments,
                )

            answer = outcome.answers[0]
            if not apply_answer(uf, current_goal, answer.subst):
                return _ResumeBranchResult(failures=(_failure_judgment(current_goal.key, "failed to apply answer"),))
            judgment = answer.judgment or Judgment(current_goal.key, answer.evidence)
            subjudgments = (*subjudgments, judgment)

            if not remaining_carriers:
                completed = self._complete_branch(branch, table, current_goal, answer, subjudgments, slots, uf)
                if completed is None:
                    return _ResumeBranchResult(failures=(_failure_judgment(current_goal.key, "no matching proof", subjudgments),))
                return _ResumeBranchResult(answers=(completed,))

            current_carrier, remaining_carriers = remaining_carriers[0], remaining_carriers[1:]
            current_is_negated = False

    def _solve_canonical_goal(self, session: urs.Session, goal: CanonicalGoal) -> _GoalOutcome:
        return _QueryCore(session, goal.key)._solve_goal(goal)

    def _persist_resumed_branch(
        self,
        blocked: urs.DeferredGoal,
        current_carrier: pm.Carrier,
        remaining_carriers: tuple[pm.Carrier, ...],
        uf: UnionFind,
        blocked_is_negated: bool,
        completion: urs.BranchCompletion | None,
        subjudgments: tuple[urs.Judgment, ...],
    ) -> urs.PendingBranch:
        blocked_goal, remaining_goals, subst, slot_info = canonicalize_branch(current_carrier, remaining_carriers, uf)
        return PendingBranch(
            blocked=DeferredGoal(blocked_goal, blocked.blocker, blocked.evidence, blocked.wake_on, blocked.judgment),
            remaining_goals=remaining_goals,
            subst=subst,
            slot_info=slot_info,
            blocked_is_negated=blocked_is_negated,
            completion=completion,
            subjudgments=subjudgments,
        )

    def _persist_spec_branch(
        self,
        branch: urs.PendingBranch,
        trailing_goals: tuple[pm.Spec, ...],
        info_by_placeholder: dict[pm.Placeholder, EqClassInfo | None],
        completion: urs.BranchCompletion | None,
        subjudgments: tuple[urs.Judgment, ...],
    ) -> urs.PendingBranch:
        blocked_goal, remaining_goals = materialize_branch_goals(branch)
        canonical_blocked, canonical_remaining, subst, slot_info = canonicalize_branch_specs(
            blocked_goal,
            (*remaining_goals, *trailing_goals),
            info_by_placeholder,
        )
        return PendingBranch(
            blocked=DeferredGoal(
                canonical_blocked,
                branch.blocked.blocker,
                branch.blocked.evidence,
                branch.blocked.wake_on,
                branch.blocked.judgment,
            ),
            remaining_goals=canonical_remaining,
            subst=subst,
            slot_info=slot_info,
            blocked_is_negated=branch.blocked_is_negated,
            completion=completion,
            subjudgments=subjudgments,
        )

    def _resume_branch_answers(
        self,
        branch: urs.PendingBranch,
        table,
        session: urs.Session,
        current_goal: CanonicalGoal,
        answers: tuple[_AnswerData, ...],
        remaining_carriers: tuple[pm.Carrier, ...],
        slots: tuple[pm.Carrier, ...],
        uf: UnionFind,
        subjudgments: tuple[urs.Judgment, ...],
    ) -> _ResumeBranchResult:
        resumed_answers: list[_AnswerData] = []
        resumed_branches: list[PendingBranch] = []
        failures: list[Judgment] = []

        for answer in answers:
            snap = uf.snapshot()
            if not apply_answer(uf, current_goal, answer.subst):
                uf.rollback(snap)
                continue
            judgment = answer.judgment or Judgment(current_goal.key, answer.evidence)
            next_subjudgments = (*subjudgments, judgment)
            if not remaining_carriers:
                completed = self._complete_branch(branch, table, current_goal, answer, next_subjudgments, slots, uf)
                if completed is not None:
                    resumed_answers.append(completed)
                else:
                    failures.append(_failure_judgment(current_goal.key, "no matching proof", next_subjudgments))
            else:
                resumed = self._resume_branch_state(
                    branch,
                    table,
                    session,
                    uf,
                    remaining_carriers[0],
                    remaining_carriers[1:],
                    slots,
                    next_subjudgments,
                    False,
                )
                resumed_answers.extend(resumed.answers)
                resumed_branches.extend(resumed.branches)
                failures.extend(resumed.failures)
            uf.rollback(snap)

        return _ResumeBranchResult(tuple(resumed_answers), tuple(resumed_branches), None, tuple(_dedupe_judgments(failures)))

    def _complete_branch(
        self,
        branch: urs.PendingBranch,
        table,
        current_goal: CanonicalGoal,
        answer: _AnswerData,
        subjudgments: tuple[urs.Judgment, ...],
        slots: tuple[pm.Carrier, ...],
        uf: UnionFind,
    ) -> _AnswerData | None:
        completion = branch.completion or DirectCompletion(rel=table.key)
        subst = extract_branch_answer(table.key, table.query_slot_indices, branch, slots, uf)

        if isinstance(completion, DirectCompletion):
            judgment = answer.judgment or Judgment(current_goal.key, answer.evidence)
            return _AnswerData(subst, judgment.evidence, judgment)
        if isinstance(completion, ExpandCompletion):
            evidence = _evidence_expand(completion.subject, subjudgments)
            return _AnswerData(subst, evidence, Judgment(completion.rel, evidence, subjudgments))
        if isinstance(completion, RuleCompletion):
            evidence = _evidence_rule_head(completion.rule_head, subjudgments)
            return _AnswerData(subst, evidence, Judgment(completion.rel, evidence, subjudgments))
        return None

    def _wake_satisfied(self, table, wake, session: urs.Session) -> bool:
        from .model import BindingsChanged, LocalFactsChanged, OperatorRetriable, StratumClosed

        if isinstance(wake, BindingsChanged):
            return session.state.binding_epoch > table.binding_epoch
        if isinstance(wake, LocalFactsChanged):
            if session.state.local_facts_epoch <= table.local_facts_epoch:
                return False
            if not wake.anchors:
                return True
            return any(str(fact.anchor) in wake.anchors for fact in session.state.local_facts)
        if isinstance(wake, StratumClosed):
            return wake.target_stratum in session.engine.global_tables.closed_strata
        if isinstance(wake, OperatorRetriable):
            return True
        return False


class _EngineSolveCore:
    def __init__(self, engine):
        self.engine = engine

    def run(self):
        known: dict[str, set[pm.Spec]] = {
            anchor: set(self.engine.facts_by_anchor.get(anchor, ()))
            for anchor in self.engine.anchors
        }
        derived: dict[str, set[pm.Spec]] = {anchor: set() for anchor in self.engine.anchors}
        closed_components: set[int] = set()
        closed_strata: set[int] = set()

        strata_values = sorted(set(self.engine.strata.stratum_by_component))
        for stratum in strata_values:
            components = tuple(
                component
                for component in self.engine.sccs
                if self.engine.strata.stratum_by_component[component.id] == stratum
            )
            while True:
                changed = False
                for component in components:
                    if component.id in self.engine.strata.negative_cycle_components:
                        continue
                    for anchor in component.anchors:
                        for rule in self.engine.rules_by_anchor.get(anchor, ()):
                            for fact in _derive_ground_facts(rule, known, self.engine.strata, stratum):
                                bucket = known.setdefault(str(anchor), set())
                                if fact in bucket:
                                    continue
                                bucket.add(fact)
                                if fact not in self.engine.facts_by_anchor.get(str(anchor), ()):
                                    derived.setdefault(str(anchor), set()).add(fact)
                                changed = True
                if not changed:
                    break
            for component in components:
                closed_components.add(component.id)
            closed_strata.add(stratum)

        facts_by_component: dict[int, tuple[pm.Spec, ...]] = {}
        derived_by_component: dict[int, tuple[pm.Spec, ...]] = {}
        for component in self.engine.sccs:
            if component.id not in closed_components:
                continue
            facts: list[pm.Spec] = []
            component_derived: list[pm.Spec] = []
            for anchor in component.anchors:
                facts.extend(sorted(known.get(anchor, ()), key=repr))
                component_derived.extend(sorted(derived.get(anchor, ()), key=repr))
            facts_by_component[component.id] = tuple(_dedupe_specs(facts))
            derived_by_component[component.id] = tuple(_dedupe_specs(component_derived))

        return urs.EngineTables(
            facts_by_anchor=frozendict((anchor, tuple(sorted(values, key=repr))) for anchor, values in known.items()),
            derived_facts_by_anchor=frozendict((anchor, tuple(sorted(values, key=repr))) for anchor, values in derived.items()),
            facts_by_component=frozendict(sorted(facts_by_component.items())),
            derived_facts_by_component=frozendict(sorted(derived_by_component.items())),
            rules_by_anchor=self.engine.rules_by_anchor,
            closed_components=frozenset(closed_components),
            closed_strata=frozenset(closed_strata),
        )


def instantiate_goal_slots(carrier: pm.Carrier, slots: tuple[pm.Carrier, ...]) -> pm.Carrier:
    from .subst import instantiate_goal_slots as _instantiate_goal_slots

    return _instantiate_goal_slots(carrier, slots)


def _dedupe_deferred(items: list[DeferredGoal]) -> list[DeferredGoal]:
    deduped: dict[tuple[pm.Spec, object], DeferredGoal] = {}
    for item in items:
        deduped[(item.goal, item.blocker)] = item
    return list(deduped.values())


def _dedupe_specs(items: list[pm.Spec]) -> list[pm.Spec]:
    deduped: dict[pm.Spec, None] = {}
    for item in items:
        deduped[item] = None
    return list(deduped)


def _dedupe_judgments(items: list[Judgment] | tuple[urs.Judgment, ...]) -> tuple[urs.Judgment, ...]:
    deduped: dict[urs.Judgment, None] = {}
    for item in items:
        deduped[item] = None
    return tuple(deduped)


def _preferred_failures(outcome: _GoalOutcome, goal: pm.Spec) -> tuple[urs.Judgment, ...]:
    if outcome.failures:
        return outcome.failures
    return (_failure_judgment(goal, "no matching proof"),)


def _failure_judgment(goal: pm.Spec, reason: str, subjudgments: tuple[urs.Judgment, ...] = ()) -> urs.Judgment:
    evidence = pm.Spec.of("std.logic.ByNoSolution", goal, reason)
    return Judgment(goal, evidence, subjudgments)


def _answer_score(answer: _AnswerData) -> tuple[int, int]:
    return _judgment_score(answer.judgment)


def _stored_answer_score(answer) -> tuple[int, int]:
    return _judgment_score(answer.judgment)


def _judgment_score(judgment: urs.Judgment | None) -> tuple[int, int]:
    if judgment is None or judgment.evidence is None:
        return (0, 0)
    anchor = str(judgment.evidence.anchor)
    anchor_score = {
        "std.logic.ByRule": 4,
        "std.logic.ByExpand": 3,
        "std.logic.ByBuiltin": 3,
        "std.logic.ByCoinduction": 2,
        "std.logic.ByFact": 1,
    }.get(anchor, 0)
    return (anchor_score, len(judgment.subjudgments))


def _has_generic_wake(table) -> bool:
    from .model import BindingsChanged, LocalFactsChanged

    for blocked in table.continuation_state:
        for wake in blocked.blocked.wake_on:
            if isinstance(wake, BindingsChanged) and not wake.placeholders:
                return True
            if isinstance(wake, LocalFactsChanged) and not wake.anchors:
                return True
    return False


def _session_signature(session: urs.Session):
    state = session.state
    return (state.bindings, state.local_facts, state.deferred, state.tables)


def _evidence_fact(fact: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByFact", fact)


def _evidence_rule(rule: urs.Rule, subjudgments: tuple[urs.Judgment, ...] = ()) -> pm.Spec:
    return pm.Spec.of("std.logic.ByRule", rule.head, *subjudgments)


def _evidence_rule_head(rule_head: pm.Spec, subjudgments: tuple[urs.Judgment, ...] = ()) -> pm.Spec:
    return pm.Spec.of("std.logic.ByRule", rule_head, *subjudgments)


def _evidence_expand(goal: pm.Spec, subjudgments: tuple[urs.Judgment, ...] = ()) -> pm.Spec:
    return pm.Spec.of("std.logic.ByExpand", goal, *subjudgments)


def _evidence_builtin(goal: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByBuiltin", goal)


def _evidence_coinduction(goal: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByCoinduction", goal)


def _evidence_deferred(goal: pm.Spec, blocker) -> pm.Spec:
    return pm.Spec.of("std.logic.ByDeferred", goal, blocker)


def _evidence_negation(goal: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByNegation", goal)


def _deferred_goal(goal: pm.Spec, blocker, evidence: pm.Spec | None = None) -> urs.DeferredGoal:
    evidence = evidence or _evidence_deferred(goal, blocker)
    return DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence))


def _negation_judgment(goal: pm.Spec) -> urs.Judgment:
    rel = pm.Spec.of("std.logic.Not", goal)
    return Judgment(rel, _evidence_negation(goal))


def _search_operator(value: Any) -> SolverOperator | None:
    if isinstance(value, SolverOperator):
        return value
    if isinstance(value, pm.Spec):
        for item in value.args.content:
            found = _search_operator(item)
            if found is not None:
                return found
        return None
    if isinstance(value, tuple):
        for item in value:
            found = _search_operator(item)
            if found is not None:
                return found
    return None


def _coerce_bound_value(goal: CanonicalGoal, slot: int, value: Any) -> pm.Carrier:
    if isinstance(value, pm.Carrier):
        return value
    if isinstance(value, pm.Spec):
        return wrap_logic(value)
    return pm.LeafCarrier(goal.slots[slot].descriptor, value)


def _coerce_bound_value_for_carrier(slot: pm.Carrier, value: Any) -> pm.Carrier:
    if isinstance(value, pm.Carrier):
        return value
    if isinstance(value, pm.Spec):
        return wrap_logic(value)
    return pm.LeafCarrier(slot.descriptor, value)


def _remaining_rule_goals(
    body: tuple[_CompiledLiteral, ...],
    start: int,
    app_ctx: RuleAppCtx,
    uf: UnionFind,
) -> tuple[pm.Spec, ...]:
    goals: list[pm.Spec] = []
    for literal in body[start:]:
        carrier = uf.reify(instantiate_template(literal.goal, app_ctx))
        value = canonicalize(carrier, uf).key
        if isinstance(value, pm.Spec):
            goals.append(value)
    return tuple(goals)


def _derive_ground_facts(
    rule: urs.Rule,
    known: dict[str, set[pm.Spec]],
    plan,
    current_stratum: int,
) -> tuple[pm.Spec, ...]:
    rule_ctx = rule_context_for(rule)
    slot_by_placeholder: dict[pm.Placeholder, int] = {}
    head = compile_template(rule.head, rule_ctx, slot_by_placeholder)
    body = tuple(
        (compile_template(unwrap_negation(goal), rule_ctx, slot_by_placeholder), True)
        if is_negation(goal)
        else (compile_template(goal, rule_ctx, slot_by_placeholder), False)
        for goal in rule.body
    )

    app_ctx = RuleAppCtx(rule_ctx.template_key.head, rule_ctx, 1)
    answers: list[pm.Spec] = []
    uf = make_union_find()

    def solve_body(index: int) -> None:
        if index == len(body):
            grounded = uf.reify(instantiate_template(head, app_ctx))
            if _contains_runtime_vars(grounded):
                return
            value = grounded.fetch()
            if isinstance(value, pm.Spec):
                answers.append(value)
            return

        template, negated = body[index]
        target = uf.reify(instantiate_template(template, app_ctx))
        value = target.fetch()
        if not isinstance(value, pm.Spec):
            return
        anchor = str(value.anchor)

        if negated:
            if plan.has_negative_cycle(anchor):
                return
            if plan.stratum_of(anchor) >= current_stratum:
                return
            if _contains_runtime_vars(target):
                return
            if _matches_any_fact(target, known.get(anchor, ())):
                return
            solve_body(index + 1)
            return

        for fact in known.get(anchor, ()): 
            snap = uf.snapshot()
            if unify(target, wrap_logic(fact), subst=uf) is not None:
                solve_body(index + 1)
            uf.rollback(snap)

    solve_body(0)
    deduped = dict.fromkeys(answers)
    return tuple(deduped)


def _matches_any_fact(goal: pm.Carrier, facts: set[pm.Spec] | tuple[pm.Spec, ...]) -> bool:
    for fact in facts:
        uf = make_union_find()
        if unify(goal, wrap_logic(fact), subst=uf) is not None:
            return True
    return False


def _contains_runtime_vars(carrier: pm.Carrier) -> bool:
    from .subst import runtime_var_of

    for leaf in carrier.deep_iter():
        if runtime_var_of(leaf) is not None:
            return True
    return False


def _specs_from_carriers(carriers: tuple[pm.Carrier, ...], uf: UnionFind) -> tuple[pm.Spec, ...]:
    values: list[pm.Spec] = []
    for carrier in carriers:
        value = uf.reify(carrier).fetch()
        if not isinstance(value, pm.Spec):
            raise TypeError("Expected branch carrier to reify to Spec")
        values.append(value)
    return tuple(values)


QueryCore = _QueryCore
SessionSolveCore = _SessionSolveCore
EngineSolveCore = _EngineSolveCore
