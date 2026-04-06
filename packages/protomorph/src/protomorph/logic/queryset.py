from __future__ import annotations

from typing import TYPE_CHECKING

from protobase import Consed, frozendict

import protomorph as pm

from .canonical import (
    CanonicalGoal,
    StoredAnswer,
    apply_stored_answer,
    canonicalize_goal,
    extract_branch_subst,
    extract_stored_subst,
    ground_goal,
    instantiate_goal_slots,
    is_logic_var,
    ordered_placeholders,
)
from .model import (
    ActiveFrame,
    Assertion,
    Answer,
    Answers,
    Blocked,
    CoinductiveEdge,
    CoinductiveCycle,
    Cycle,
    CycleIssue,
    Edge,
    ExpectedBinding,
    Failed,
    Goal,
    GoalOutcome,
    InductiveCycleIssue,
    InsufficientBindings,
    Judgment,
    Key,
    NegativeCycleIssue,
    PendingReduction,
    PendingNegation,
    PendingBranch,
    PendingTable,
    QueryRoot,
    QuerySetState,
    QueryTable,
    Reduced,
    Expand,
    TableKey,
    TableDependencies,
)

if TYPE_CHECKING:
    from .query import Query
    from .session import Session
else:
    Query = pm.Builtin
    Session = pm.Builtin


class QuerySet(Consed):
    session: Session
    state: QuerySetState = QuerySetState()

    def add(self, *goals: pm.Carrier | pm.Datum) -> QuerySet:
        roots = list(self.state.roots)
        tables = dict(self.state.tables_by_key)
        open_keys = list(self.state.open_keys)
        dirty_keys = list(self.state.dirty_keys)
        seen_root_goals = {root.goal for root in roots}

        for goal in goals:
            carrier = goal if isinstance(goal, pm.Carrier) else pm.wrap(goal)
            canonical = canonicalize_goal(carrier)
            if carrier not in seen_root_goals:
                roots.append(QueryRoot(carrier, canonical.key, ordered_placeholders(carrier)))
                seen_root_goals.add(carrier)
            key = canonical.key
            if key not in tables:
                tables[key] = QueryTable(key, canonical.goal)
            if key not in open_keys:
                open_keys.append(key)
            if key not in dirty_keys:
                dirty_keys.append(key)

        return QuerySet(
            self.session,
            QuerySetState(
                roots=tuple(roots),
                tables_by_key=frozendict(tables.items()),
                tables_by_positive_key=self.state.tables_by_positive_key,
                tables_by_negative_key=self.state.tables_by_negative_key,
                tables_by_binding_key=self.state.tables_by_binding_key,
                open_keys=tuple(open_keys),
                dirty_keys=tuple(dirty_keys),
                promoted_answers_by_key=self.state.promoted_answers_by_key,
                epoch=self.state.epoch + 1,
                binding_epoch=self.state.binding_epoch,
                binding_epochs_by_key=self.state.binding_epochs_by_key,
                promoted_epoch=self.state.promoted_epoch,
            ),
        )

    def query(self, goal: pm.Carrier | pm.Datum) -> Query:
        from .query import Query

        carrier = goal if isinstance(goal, pm.Carrier) else pm.wrap(goal)
        queryset = self if any(root.goal == carrier for root in self.state.roots) else self.add(carrier)
        return Query(queryset, carrier)

    def table(self, goal: pm.Carrier | pm.Datum) -> QueryTable:
        carrier = goal if isinstance(goal, pm.Carrier) else pm.wrap(goal)
        for root in self.state.roots:
            if root.goal == carrier:
                canonical = canonicalize_goal(carrier)
                return self.state.tables_by_key.get(root.table_key, QueryTable(root.table_key, canonical.goal))
        canonical = canonicalize_goal(carrier)
        return self.state.tables_by_key.get(canonical.key, QueryTable(canonical.key, canonical.goal))

    def continue_(self) -> QuerySet:
        tables = dict(self.state.tables_by_key)
        promoted = {key: set(values) for key, values in self.state.promoted_answers_by_key.items()}
        binding_epochs = dict(self.state.binding_epochs_by_key)
        binding_epoch = self.state.binding_epoch
        dirty_keys = set(self.state.dirty_keys)
        _drop_promoted_answers_for_tables(self, tables, promoted, dirty_keys)
        _reset_dirty_tables(tables, dirty_keys)
        positive_index = self.state.tables_by_positive_key
        negative_index = self.state.tables_by_negative_key
        binding_index = self.state.tables_by_binding_key
        changed = True

        while changed:
            changed = False
            binding_keys: set[Key] = set()
            for key in _retry_table_keys(tables, promoted, binding_epochs, dirty_keys):
                current = tables[key]
                solved = _solve_table(self, current, tables, promoted, binding_epoch)
                if current is None or _table_signature(current) != _table_signature(solved):
                    tables[key] = solved
                    changed = True
                dirty_keys.discard(key)
                if current is None or current.answers != solved.answers:
                    binding_keys.add(self.session.solver.head_key(solved.goal))

            next_promoted = _promoted_answers(self, tables)
            promoted_keys = _changed_promoted_keys(promoted, next_promoted)
            if promoted_keys:
                promoted = next_promoted
                changed = True
                binding_keys.update(promoted_keys)
                promoted_dependents = _dependent_tables_for_keys(positive_index, negative_index, promoted_keys)
                dirty_keys.update(promoted_dependents)
                _drop_promoted_answers_for_tables(self, tables, promoted, promoted_dependents)
                _reset_dirty_tables(tables, promoted_dependents)

            if binding_keys:
                binding_epoch += 1
                for key in binding_keys:
                    binding_epochs[key] = binding_epoch

            if changed:
                positive_index, negative_index, binding_index = _build_dependency_indexes(tables)

        open_keys = tuple(key for key, table in tables.items() if table.active)
        return QuerySet(
            self.session,
            QuerySetState(
                roots=self.state.roots,
                tables_by_key=frozendict(tables.items()),
                tables_by_positive_key=positive_index,
                tables_by_negative_key=negative_index,
                tables_by_binding_key=binding_index,
                open_keys=open_keys,
                dirty_keys=(),
                promoted_answers_by_key=frozendict(
                    (key, frozenset(values))
                    for key, values in promoted.items()
                ),
                epoch=self.state.epoch + 1,
                binding_epoch=binding_epoch,
                binding_epochs_by_key=frozendict(binding_epochs.items()),
                promoted_epoch=self.state.promoted_epoch + 1,
            ),
        )


def _ensure_table(
    queryset: QuerySet,
    tables: dict[Goal, QueryTable],
    goal: Goal,
) -> tuple[CanonicalGoal, QueryTable, bool]:
    canonical = canonicalize_goal(goal)
    table = tables.get(canonical.key)
    if table is not None:
        return canonical, table, False
    table = QueryTable(key=canonical.key, goal=canonical.goal, status="open", active=True, closed=False)
    tables[canonical.key] = table
    return canonical, table, True


def _solve_table(
    queryset: QuerySet,
    table: QueryTable,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
) -> QueryTable:
    canonical = canonicalize_goal(table.goal)
    answers = list(table.answers)
    failures = list(table.failures)
    pending: list[PendingBranch] = []
    cycle_issue = table.cycle_issue
    dependencies = table.dependencies

    if table.pending:
        for branch in table.pending:
            resumed = _resume_pending_branch(queryset, canonical, branch, tables, promoted, binding_epoch)
            if resumed is None:
                failures.append(Judgment(branch.blocked_goal, pm.wrap(Failed("invalid pending branch state")), branch.subjudgments))
                continue
            child_answers, child_pending, child_failures, child_cycle, child_dependencies = resumed
            answers.extend(child_answers)
            pending.extend(child_pending)
            failures.extend(child_failures)
            cycle_issue = cycle_issue or child_cycle
            dependencies = _merge_table_dependencies(dependencies, child_dependencies)
    else:
        uf = pm.UnionFind(_is_logic_var)
        child_answers, child_pending, child_failures, child_cycle, child_dependencies = _solve_goals(
            queryset,
            canonical,
            canonical,
            (table.goal,),
            uf,
            tables,
            promoted,
            binding_epoch,
            (),
        )
        answers.extend(child_answers)
        pending.extend(child_pending)
        failures.extend(child_failures)
        cycle_issue = cycle_issue or child_cycle
        dependencies = _merge_table_dependencies(dependencies, child_dependencies)

    deduped_answers = _dedupe_answers(answers)
    deduped_pending = _dedupe_pending(pending)
    deduped_failures = _dedupe_judgments(failures)
    status = "cycle" if cycle_issue is not None else "blocked" if deduped_pending else "closed"
    return QueryTable(
        key=table.key,
        goal=table.goal,
        answers=deduped_answers,
        failures=deduped_failures,
        pending=deduped_pending,
        cycle_issue=cycle_issue,
        dependencies=dependencies,
        status=status,
        active=bool(deduped_pending),
        closed=not deduped_pending,
    )


def _resume_pending_branch(
    queryset: QuerySet,
    owner: CanonicalGoal,
    branch: PendingBranch,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
 ) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies] | None:
    uf = pm.UnionFind(_is_logic_var)
    if not apply_stored_answer(uf, owner, StoredAnswer(branch.subst)):
        return None
    if branch.assertion is not None:
        return _resume_assertion_branch(queryset, owner, branch, uf, tables, promoted, binding_epoch)
    goals = tuple(uf.reify(goal) for goal in (branch.blocked_goal, *branch.remaining_goals))
    return _solve_goals(queryset, owner, owner, goals, uf, tables, promoted, binding_epoch, branch.active_frames)


def _empty_goal_outcome() -> GoalOutcome:
    return GoalOutcome()


def _empty_table_dependencies() -> TableDependencies:
    return TableDependencies()


def _merge_table_dependencies(a: TableDependencies, b: TableDependencies) -> TableDependencies:
    return TableDependencies(
        positive_keys=a.positive_keys | b.positive_keys,
        negative_keys=a.negative_keys | b.negative_keys,
        binding_keys=a.binding_keys | b.binding_keys,
    )


def _goal_outcome_with_positive_dependency(outcome: GoalOutcome, key: Key) -> GoalOutcome:
    return GoalOutcome(
        matched=outcome.matched,
        answers_by_subst=outcome.answers_by_subst,
        pending=outcome.pending,
        failures=outcome.failures,
        cycle_issue=outcome.cycle_issue,
        dependencies=_merge_table_dependencies(outcome.dependencies, TableDependencies(positive_keys=frozenset((key,)))),
    )


def _goal_outcome_with_negative_dependency(outcome: GoalOutcome, key: Key) -> GoalOutcome:
    return GoalOutcome(
        matched=outcome.matched,
        answers_by_subst=outcome.answers_by_subst,
        pending=outcome.pending,
        failures=outcome.failures,
        cycle_issue=outcome.cycle_issue,
        dependencies=_merge_table_dependencies(outcome.dependencies, TableDependencies(negative_keys=frozenset((key,)))),
    )


def _goal_outcome_with_binding_dependencies(outcome: GoalOutcome, keys: frozenset[Key]) -> GoalOutcome:
    return GoalOutcome(
        matched=outcome.matched,
        answers_by_subst=outcome.answers_by_subst,
        pending=outcome.pending,
        failures=outcome.failures,
        cycle_issue=outcome.cycle_issue,
        dependencies=_merge_table_dependencies(outcome.dependencies, TableDependencies(binding_keys=keys)),
    )


def _goal_outcome_from_parts(
    *,
    matched: bool = False,
    answers: tuple[StoredAnswer, ...] = (),
    pending: tuple[PendingBranch, ...] = (),
    failures: tuple[Judgment, ...] = (),
    cycle_issue: CycleIssue | None = None,
    dependencies: TableDependencies | None = None,
 ) -> GoalOutcome:
    return GoalOutcome(
        matched=matched,
        answers_by_subst=frozendict((answer.subst, answer) for answer in answers),
        pending=frozenset(pending),
        failures=frozenset(failures),
        cycle_issue=cycle_issue,
        dependencies=dependencies or TableDependencies(),
    )


def _goal_outcome_from_solve_result(
    matched: bool,
    answers: list[StoredAnswer],
    pending: list[PendingBranch],
    failures: list[Judgment],
    cycle_issue: CycleIssue | None,
    dependencies: TableDependencies | None = None,
) -> GoalOutcome:
    return _goal_outcome_from_parts(
        matched=matched,
        answers=tuple(answers),
        pending=tuple(pending),
        failures=tuple(failures),
        cycle_issue=cycle_issue,
        dependencies=dependencies,
    )


def _merge_goal_outcome(base: GoalOutcome, extra: GoalOutcome) -> GoalOutcome:
    answers_by_subst = dict(base.answers_by_subst)
    answers_by_subst.update(extra.answers_by_subst)
    return GoalOutcome(
        matched=base.matched or extra.matched,
        answers_by_subst=frozendict(answers_by_subst.items()),
        pending=base.pending | extra.pending,
        failures=base.failures | extra.failures,
        cycle_issue=base.cycle_issue or extra.cycle_issue,
        dependencies=_merge_table_dependencies(base.dependencies, extra.dependencies),
    )


def _unpack_goal_outcome(
    outcome: GoalOutcome,
) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies]:
    return list(outcome.answers_by_subst.values()), list(outcome.pending), list(outcome.failures), outcome.cycle_issue, outcome.dependencies


def _reducible_goal_outcome(
    queryset: QuerySet,
    owner: CanonicalGoal,
    root_goal: CanonicalGoal,
    current: Goal,
    remaining: tuple[Goal, ...],
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
    stack: tuple[ActiveFrame, ...],
    current_table_key: TableKey,
) -> GoalOutcome:
    ctrl_carrier = queryset.session.solver.eval_as_ctrl(current)
    ctrl = ctrl_carrier.fetch()
    next_stack = (*stack, ActiveFrame(current_table_key, False))
    if isinstance(ctrl, Reduced):
        return _goal_outcome_from_solve_result(True, *_solve_goals(queryset, owner, root_goal, (ctrl.value, *remaining), uf, tables, promoted, binding_epoch, next_stack))
    if isinstance(ctrl, Expand):
        return _goal_outcome_from_solve_result(True, *_solve_goals(queryset, owner, root_goal, (*ctrl.goals, *remaining), uf, tables, promoted, binding_epoch, next_stack))
    if isinstance(ctrl, Answers):
        outcome = _goal_outcome_from_parts(matched=True)
        for answer in ctrl.items:
            snap = uf.snapshot()
            stored = _stored_answer_from_public(owner, current, answer)
            if stored is None or not apply_stored_answer(uf, owner, stored):
                uf.rollback(snap)
                continue
            child_answers, child_pending, child_failures, child_cycle, child_dependencies = _solve_goals(
                queryset,
                owner,
                root_goal,
                remaining,
                uf,
                tables,
                promoted,
                binding_epoch,
                next_stack,
            )
            failures = list(child_failures)
            if answer.judgment is not None:
                failures = [answer.judgment, *failures]
            outcome = _merge_goal_outcome(
                outcome,
                _goal_outcome_from_solve_result(True, child_answers, child_pending, failures, child_cycle, child_dependencies),
            )
            uf.rollback(snap)
        return outcome
    if isinstance(ctrl, Blocked):
        blocker = ctrl.blocker
        if isinstance(blocker, PendingReduction | PendingTable | PendingNegation | InsufficientBindings):
            blocked_goal = uf.reify(blocker.goal)
        else:
            blocked_goal = current
        return _goal_outcome_from_parts(
            matched=True,
            pending=(
                PendingBranch(
                    table_key=owner.key,
                    blocked_goal=blocked_goal,
                    blocker=blocker,
                    remaining_goals=remaining,
                    subst=extract_branch_subst(owner, uf),
                    binding_epoch=binding_epoch,
                    active_frames=stack,
                ),
            ),
        )
    if isinstance(ctrl, Failed):
        return _goal_outcome_from_parts(
            matched=True,
            failures=(Judgment(current, ctrl_carrier),),
        )
    return _empty_goal_outcome()


def _solve_table_goal(
    queryset: QuerySet,
    owner: CanonicalGoal,
    root_goal: CanonicalGoal,
    subgoal: Goal,
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
    stack: tuple[ActiveFrame, ...],
    *,
    blocked_is_negated: bool = False,
) -> tuple[CanonicalGoal, tuple[StoredAnswer, ...], tuple[PendingBranch, ...], tuple[Judgment, ...], CycleIssue | None, TableDependencies]:
    canonical = canonicalize_goal(subgoal, uf)
    cycle = _active_cycle(stack, canonical.key, closing_negated=blocked_is_negated)
    if cycle is not None:
        if cycle.is_negative:
            return canonical, (), (), (), NegativeCycleIssue(cycle, _cycle_judgment(subgoal, cycle, True)), TableDependencies()
        if queryset.session.solver.is_coinductive(cycle):
            answer = StoredAnswer((), pm.wrap(_coinductive_cycle(cycle)), _coinduction_judgment(subgoal, cycle))
            return canonical, (answer,), (), (), None, TableDependencies()
        return canonical, (), (), (), InductiveCycleIssue(cycle, _cycle_judgment(subgoal, cycle, False)), TableDependencies()

    table = tables.get(canonical.key)
    if table is None:
        table = QueryTable(key=canonical.key, goal=canonical.goal)
    solved = _solve_table(queryset, table, tables, promoted, binding_epoch)
    tables[canonical.key] = solved
    return canonical, solved.answers, solved.pending, solved.failures, solved.cycle_issue, solved.dependencies


def _resume_assertion_branch(
    queryset: QuerySet,
    owner: CanonicalGoal,
    branch: PendingBranch,
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies] | None:
    assertion = branch.assertion
    if assertion is None or branch.premise_index >= len(assertion.premises):
        return None
    return _solve_assertion_state(
        queryset,
        owner,
        owner,
        assertion,
        branch.premise_index,
        branch.remaining_goals,
        uf,
        tables,
        promoted,
        binding_epoch,
        branch.active_frames,
        branch.subjudgments,
    )


def _solve_goals(
    queryset: QuerySet,
    owner: CanonicalGoal,
    root_goal: CanonicalGoal,
    goals: tuple[Goal, ...],
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
    stack: tuple[ActiveFrame, ...],
) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies]:
    if not goals:
        answer = StoredAnswer(extract_stored_subst(root_goal, uf), judgment=Judgment(root_goal.key))
        return [answer], [], [], None, TableDependencies()

    current = uf.reify(goals[0])
    remaining = goals[1:]
    current_table_key = canonicalize_goal(current, uf).key

    cycle = _active_cycle(stack, current_table_key)
    if cycle is not None:
        if cycle.is_negative:
            issue = NegativeCycleIssue(cycle, _cycle_judgment(current, cycle, True))
            return [], [], [], issue, TableDependencies()
        if queryset.session.solver.is_coinductive(cycle):
            answer = StoredAnswer(
                extract_stored_subst(root_goal, uf),
                evidence=pm.wrap(_coinductive_cycle(cycle)),
                judgment=_coinduction_judgment(current, cycle),
            )
            return [answer], [], [], None, TableDependencies()
            
        issue = InductiveCycleIssue(cycle, _cycle_judgment(current, cycle, False))
        return [], [], [], issue, TableDependencies()

    outcome = _empty_goal_outcome()
    outcome = _goal_outcome_with_positive_dependency(outcome, queryset.session.solver.head_key(current))
    next_stack = (*stack, ActiveFrame(current_table_key, False))

    for fact in _candidate_facts(queryset, current, promoted):
        snap = uf.snapshot()
        if pm.unify(current, fact, subst=uf) is not None:
            child_answers, child_pending, child_failures, child_cycle, child_dependencies = _solve_goals(
                queryset,
                owner,
                root_goal,
                remaining,
                uf,
                tables,
                promoted,
                binding_epoch,
                next_stack,
            )
            outcome = _merge_goal_outcome(
                outcome,
                _goal_outcome_from_solve_result(True, child_answers, child_pending, child_failures, child_cycle, child_dependencies),
            )
        uf.rollback(snap)

    if queryset.session.solver.is_reducible(current):
        outcome = _merge_goal_outcome(
            outcome,
            _reducible_goal_outcome(
                queryset,
                owner,
                root_goal,
                current,
                remaining,
                uf,
                tables,
                promoted,
                binding_epoch,
                stack,
                current_table_key,
            ),
        )
        if outcome.cycle_issue is not None:
            return _unpack_goal_outcome(outcome)

    for assertion in queryset.session.solver.assertions_for(queryset.session.solver.head_key(current)):
        if assertion.is_fact:
            continue
        snap = uf.snapshot()
        if pm.unify(current, assertion.fact, subst=uf) is None:
            uf.rollback(snap)
            continue
        child_answers, child_pending, child_failures, child_cycle, child_dependencies = _solve_assertion(
            queryset,
            owner,
            root_goal,
            remaining,
            assertion,
            uf,
            tables,
            promoted,
            binding_epoch,
            next_stack,
        )
        outcome = _merge_goal_outcome(
            outcome,
            _goal_outcome_from_solve_result(True, child_answers, child_pending, child_failures, child_cycle, child_dependencies),
        )
        uf.rollback(snap)

    if outcome.matched:
        return _unpack_goal_outcome(outcome)

    return [], [], [Judgment(current, pm.wrap(Failed("no matching proof")))], None, TableDependencies()


def _solve_assertion(
    queryset: QuerySet,
    owner: CanonicalGoal,
    root_goal: CanonicalGoal,
    remaining: tuple[Goal, ...],
    assertion: Assertion,
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
    stack: tuple[ActiveFrame, ...],
) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies]:
    return _solve_assertion_state(
        queryset,
        owner,
        root_goal,
        assertion,
        0,
        remaining,
        uf,
        tables,
        promoted,
        binding_epoch,
        stack,
        (),
    )


def _solve_assertion_state(
    queryset: QuerySet,
    owner: CanonicalGoal,
    root_goal: CanonicalGoal,
    assertion: Assertion,
    premise_index: int,
    remaining: tuple[Goal, ...],
    uf: pm.UnionFind,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epoch: int,
    stack: tuple[ActiveFrame, ...],
    initial_subjudgments: tuple[Judgment, ...],
) -> tuple[list[StoredAnswer], list[PendingBranch], list[Judgment], CycleIssue | None, TableDependencies]:
    answers: list[StoredAnswer] = []
    pending: list[PendingBranch] = []
    failures: list[Judgment] = []
    cycle_issue: CycleIssue | None = None
    dependencies = TableDependencies()

    def solve_premise(index: int, subjudgments: tuple[Judgment, ...]) -> None:
        nonlocal cycle_issue, dependencies
        if index == len(assertion.premises):
            child_answers, child_pending, child_failures, child_cycle, child_dependencies = _solve_goals(
                queryset,
                owner,
                root_goal,
                remaining,
                uf,
                tables,
                promoted,
                binding_epoch,
                stack,
            )
            answers.extend(child_answers)
            pending.extend(child_pending)
            failures.extend(child_failures)
            cycle_issue = cycle_issue or child_cycle
            dependencies = _merge_table_dependencies(dependencies, child_dependencies)
            return

        premise = assertion.premises[index]
        subgoal = uf.reify(premise.goal)
        canonical, table_answers, table_pending, table_failures, table_cycle, table_dependencies = _solve_table_goal(
            queryset,
            owner,
            root_goal,
            subgoal,
            uf,
            tables,
            promoted,
            binding_epoch,
            stack,
            blocked_is_negated=not premise.affirmative,
        )
        dep_key = queryset.session.solver.head_key(subgoal)

        if not premise.affirmative:
            dependencies = _merge_table_dependencies(dependencies, TableDependencies(negative_keys=frozenset((dep_key,))))
            if _contains_logic_vars(subgoal):
                pending.append(
                    PendingBranch(
                        table_key=owner.key,
                        blocked_goal=subgoal,
                        blocker=InsufficientBindings(
                            goal=subgoal,
                            subject=subgoal,
                            expected_bindings=_expected_bindings(queryset, assertion, index, uf, subgoal),
                            reason_hint="negation requires sufficiently bound goal",
                        ),
                        remaining_goals=_remaining_goals(assertion, index, uf, remaining),
                        assertion=assertion,
                        premise_index=index,
                        subst=extract_branch_subst(owner, uf),
                        subjudgments=subjudgments,
                        binding_epoch=binding_epoch,
                        active_frames=stack,
                        blocked_is_negated=True,
                    )
                )
                dependencies = _merge_table_dependencies(
                    dependencies,
                    TableDependencies(binding_keys=_binding_dependency_keys(_expected_bindings(queryset, assertion, index, uf, subgoal))),
                )
                return
            if table_cycle is not None:
                cycle_issue = cycle_issue or table_cycle
                dependencies = _merge_table_dependencies(dependencies, table_dependencies)
                return
            if table_pending:
                pending.append(
                    PendingBranch(
                        table_key=owner.key,
                        blocked_goal=subgoal,
                        blocker=PendingNegation(subgoal, subgoal, canonical.key),
                        remaining_goals=_remaining_goals(assertion, index, uf, remaining),
                        assertion=assertion,
                        premise_index=index,
                        subst=extract_branch_subst(owner, uf),
                        subjudgments=subjudgments,
                        binding_epoch=binding_epoch,
                        active_frames=stack,
                        blocked_is_negated=True,
                    )
                )
                dependencies = _merge_table_dependencies(dependencies, table_dependencies)
                return
            if table_answers:
                failures.append(Judgment(subgoal, pm.wrap(Failed("negated goal succeeded")), subjudgments))
                dependencies = _merge_table_dependencies(dependencies, table_dependencies)
                return
            solve_premise(index + 1, (*subjudgments, Judgment(subgoal)))
            return

        dependencies = _merge_table_dependencies(dependencies, TableDependencies(positive_keys=frozenset((dep_key,))))
        if table_cycle is not None:
            cycle_issue = cycle_issue or table_cycle
            dependencies = _merge_table_dependencies(dependencies, table_dependencies)
            return

        if table_answers:
            for answer in table_answers:
                snap = uf.snapshot()
                if apply_stored_answer(uf, canonical, answer):
                    judgment = answer.judgment or Judgment(subgoal, answer.evidence)
                    solve_premise(index + 1, (*subjudgments, judgment))
                uf.rollback(snap)
        if table_pending:
            pending.append(
                PendingBranch(
                    table_key=owner.key,
                    blocked_goal=subgoal,
                    blocker=PendingTable(subgoal, canonical.key),
                    remaining_goals=_remaining_goals(assertion, index, uf, remaining),
                    assertion=assertion,
                    premise_index=index,
                    subst=extract_branch_subst(owner, uf),
                    subjudgments=subjudgments,
                    binding_epoch=binding_epoch,
                    active_frames=stack,
                )
            )
            dependencies = _merge_table_dependencies(dependencies, table_dependencies)
            return
        if not table_answers:
            if table_failures:
                failures.extend(table_failures)
            else:
                failures.append(Judgment(subgoal, pm.wrap(Failed("no matching proof")), subjudgments))

    solve_premise(premise_index, initial_subjudgments)
    return answers, pending, failures, cycle_issue, dependencies


def _active_cycle(
    stack: tuple[ActiveFrame, ...],
    current_key: TableKey,
    *,
    closing_negated: bool = False,
) -> Cycle[TableKey] | None:
    try:
        index = next(offset for offset, item in enumerate(stack) if item.table_key == current_key)
    except StopIteration:
        return None
    frames = (*stack[index:], ActiveFrame(current_key, closing_negated))
    edges = tuple(
        Edge(
            left.table_key,
            right.table_key,
            not right.via_negation,
        )
        for left, right in zip(frames, frames[1:])
    )
    return Cycle.of(*edges)


def _cycle_judgment(goal: Goal, cycle: Cycle[TableKey], negative: bool) -> Judgment:
    evidence = pm.wrap(NegativeCycleIssue(cycle)) if negative else pm.wrap(InductiveCycleIssue(cycle))
    return Judgment(goal, evidence)


def _coinduction_judgment(goal: Goal, cycle: Cycle[TableKey]) -> Judgment:
    evidence = pm.wrap(_coinductive_cycle(cycle))
    return Judgment(goal, evidence)


def _coinductive_cycle(cycle: Cycle[TableKey]) -> CoinductiveCycle:
    return CoinductiveCycle.of(*(CoinductiveEdge(edge.from_, edge.to) for edge in cycle.edges if edge.affirmative))


def _candidate_facts(queryset: QuerySet, current: Goal, promoted: dict[Key, set[Goal]]) -> frozenset[Goal]:
    key = queryset.session.solver.head_key(current)
    global_facts = queryset.session.solver.facts_for(key)
    promoted_facts = frozenset(promoted.get(key, set()))
    local_facts = frozenset(
        fact
        for fact in queryset.session.local_facts
        if queryset.session.solver.head_key(fact) == key
    )
    return global_facts | promoted_facts | local_facts


def _promoted_answers(queryset: QuerySet, tables: dict[Goal, QueryTable]) -> dict[Key, set[Goal]]:
    promoted: dict[Key, set[Goal]] = {}
    for table in tables.values():
        if not table.closed:
            continue
        for answer in table.answers:
            grounded = ground_goal(table.goal, answer)
            if grounded is None:
                continue
            promoted.setdefault(queryset.session.solver.head_key(grounded), set()).add(grounded)
    return promoted


def _promoted_snapshot(values: dict[Key, set[Goal]]) -> tuple[tuple[Key, frozenset[Goal]], ...]:
    return tuple(
        (key, frozenset(items))
        for key, items in sorted(values.items(), key=lambda item: repr(item[0]))
    )


def _changed_promoted_keys(
    current: dict[Key, set[Goal]],
    updated: dict[Key, set[Goal]],
) -> frozenset[Key]:
    changed: set[Key] = set()
    for key in set(current) | set(updated):
        if current.get(key, set()) != updated.get(key, set()):
            changed.add(key)
    return frozenset(changed)


def _is_logic_var(carrier: pm.Carrier) -> bool:
    return is_logic_var(carrier)


def _contains_logic_vars(carrier: pm.Carrier) -> bool:
    for leaf in carrier.deep_iter():
        if _is_logic_var(leaf):
            return True
    return False


def _expected_bindings(
    queryset: QuerySet,
    assertion: Assertion,
    premise_index: int,
    uf: pm.UnionFind,
    goal: Goal,
) -> frozenset[ExpectedBinding]:
    goal_vars = _logic_vars(goal)
    expected: set[ExpectedBinding] = set()

    for premise in assertion.premises[:premise_index]:
        if not premise.affirmative:
            continue
        subject = uf.reify(premise.goal)
        if not goal_vars & _logic_vars(subject):
            continue
        expected.add(
            ExpectedBinding(
                subject=subject,
                role="table",
                detail=queryset.session.solver.head_key(subject),
            )
        )

    if expected:
        return frozenset(expected)

    for leaf in goal_vars:
        expected.add(ExpectedBinding(subject=leaf, role="binding"))
    return frozenset(expected)


def _logic_vars(goal: Goal) -> frozenset[Goal]:
    return frozenset(leaf for leaf in goal.deep_iter() if _is_logic_var(leaf))


def _remaining_goals(
    assertion: Assertion,
    premise_index: int,
    uf: pm.UnionFind,
    trailing_goals: tuple[Goal, ...],
) -> tuple[Goal, ...]:
    next_premises = tuple(uf.reify(premise.goal) for premise in assertion.premises[premise_index + 1 :])
    return (*next_premises, *trailing_goals)


def _dedupe_answers(items: list[StoredAnswer]) -> tuple[StoredAnswer, ...]:
    deduped: dict[tuple[tuple[int, Goal], ...], StoredAnswer] = {}
    for item in items:
        key = item.subst
        deduped[key] = item
    return tuple(deduped.values())


def _dedupe_pending(items: list[PendingBranch]) -> tuple[PendingBranch, ...]:
    deduped: dict[
        tuple[
            pm.Carrier,
            pm.Carrier,
            tuple[pm.Carrier, ...],
            object,
            int,
            tuple[tuple[int, Goal], ...],
            tuple[ActiveFrame, ...],
            bool,
        ],
        PendingBranch,
    ] = {}
    for item in items:
        deduped[
            (
                item.table_key,
                item.blocked_goal,
                item.remaining_goals,
                item.assertion,
                item.premise_index,
                item.subst,
                item.active_frames,
                item.blocked_is_negated,
            )
        ] = item
    return tuple(deduped.values())


def _dedupe_judgments(items: list[Judgment]) -> tuple[Judgment, ...]:
    deduped: dict[Judgment, None] = {}
    for item in items:
        deduped[item] = None
    return tuple(deduped)


def _table_signature(table: QueryTable) -> tuple[object, ...]:
    cycle_signature = None
    if table.cycle_issue is not None:
        cycle_signature = (type(table.cycle_issue), table.cycle_issue.cycle)
    return (
        table.key,
        table.status,
        table.active,
        table.closed,
        table.answers,
        table.failures,
        table.pending,
        table.dependencies,
        cycle_signature,
    )


def _reset_dirty_tables(
    tables: dict[TableKey, QueryTable],
    dirty_keys: set[TableKey] | frozenset[TableKey],
) -> None:
    for key in dirty_keys:
        table = tables.get(key)
        if table is None:
            continue
        tables[key] = QueryTable(key=table.key, goal=table.goal)


def _drop_promoted_answers_for_tables(
    queryset: QuerySet,
    tables: dict[TableKey, QueryTable],
    promoted: dict[Key, set[Goal]],
    dirty_keys: set[TableKey] | frozenset[TableKey],
) -> None:
    for key in dirty_keys:
        table = tables.get(key)
        if table is None:
            continue
        for answer in table.answers:
            grounded = ground_goal(table.goal, answer)
            if grounded is None:
                continue
            promoted_key = queryset.session.solver.head_key(grounded)
            promoted_values = promoted.get(promoted_key)
            if promoted_values is None or grounded not in promoted_values:
                continue
            updated_values = set(promoted_values)
            updated_values.discard(grounded)
            if updated_values:
                promoted[promoted_key] = updated_values
            else:
                promoted.pop(promoted_key, None)


def _build_dependency_indexes(
    tables: dict[TableKey, QueryTable],
) -> tuple[
    frozendict[Key, tuple[TableKey, ...]],
    frozendict[Key, tuple[TableKey, ...]],
    frozendict[Key, tuple[TableKey, ...]],
]:
    positive: dict[Key, set[TableKey]] = {}
    negative: dict[Key, set[TableKey]] = {}
    binding: dict[Key, set[TableKey]] = {}
    for table_key, table in tables.items():
        for key in table.dependencies.positive_keys:
            positive.setdefault(key, set()).add(table_key)
        for key in table.dependencies.negative_keys:
            negative.setdefault(key, set()).add(table_key)
        for key in table.dependencies.binding_keys:
            binding.setdefault(key, set()).add(table_key)
    return (
        frozendict((key, tuple(sorted(values, key=repr))) for key, values in sorted(positive.items(), key=lambda item: repr(item[0]))),
        frozendict((key, tuple(sorted(values, key=repr))) for key, values in sorted(negative.items(), key=lambda item: repr(item[0]))),
        frozendict((key, tuple(sorted(values, key=repr))) for key, values in sorted(binding.items(), key=lambda item: repr(item[0]))),
    )


def _dependent_tables_for_keys(
    positive_index: dict[Key, tuple[TableKey, ...]] | frozendict[Key, tuple[TableKey, ...]],
    negative_index: dict[Key, tuple[TableKey, ...]] | frozendict[Key, tuple[TableKey, ...]],
    keys: frozenset[Key],
) -> frozenset[TableKey]:
    dependents: set[TableKey] = set()
    for key in keys:
        dependents.update(positive_index.get(key, ()))
        dependents.update(negative_index.get(key, ()))
    return frozenset(dependents)


def _retry_table_keys(
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epochs: dict[Key, int],
    dirty_keys: set[TableKey],
) -> tuple[Goal, ...]:
    candidates: list[Goal] = []
    for key, table in tables.items():
        if key in dirty_keys:
            candidates.append(key)
            continue
        if _should_retry_table(table, tables, promoted, binding_epochs):
            candidates.append(key)
    return tuple(candidates)


def _should_retry_table(
    table: QueryTable,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epochs: dict[Key, int],
) -> bool:
    if table.active and not table.pending:
        return False
    if not table.pending:
        return not table.closed
    return any(_should_retry_branch(branch, tables, promoted, binding_epochs) for branch in table.pending)


def _should_retry_branch(
    branch: PendingBranch,
    tables: dict[Goal, QueryTable],
    promoted: dict[Key, set[Goal]],
    binding_epochs: dict[Key, int],
) -> bool:
    blocker = branch.blocker
    if isinstance(blocker, PendingReduction):
        return True
    if isinstance(blocker, InsufficientBindings):
        keys = _binding_dependency_keys(blocker.expected_bindings)
        return bool(keys) and any(binding_epochs.get(key, 0) > branch.binding_epoch for key in keys)
    if isinstance(blocker, PendingTable):
        table = tables.get(blocker.key)
        return table is None or table.closed or bool(table.answers)
    if isinstance(blocker, PendingNegation):
        table = tables.get(blocker.key)
        return table is None or table.closed
    _ = promoted
    return True


def _binding_dependency_keys(expected: frozenset[ExpectedBinding]) -> frozenset[Key]:
    keys: set[Key] = set()
    for binding in expected:
        if binding.detail is None:
            continue
        keys.add(binding.detail)
    return frozenset(keys)


def _stored_answer_from_public(
    owner: CanonicalGoal,
    current: Goal,
    answer: Answer,
) -> StoredAnswer | None:
    if answer.subst:
        slot_map = _placeholder_slot_map(current, owner)
        items: list[tuple[int, Goal]] = []
        for placeholder, value in answer.subst.items():
            slot = slot_map.get(placeholder)
            if slot is None:
                return None
            items.append((slot, value))
        return StoredAnswer(tuple(sorted(items, key=lambda item: item[0])), answer.evidence, answer.judgment)

    canonical = canonicalize_goal(current)
    if canonical.key != owner.key:
        return None
    return StoredAnswer((), answer.evidence, answer.judgment)


def _placeholder_slot_map(current: Goal, owner: CanonicalGoal) -> dict[pm.Placeholder, int]:
    current_canonical = canonicalize_goal(current)
    slot_map: dict[pm.Placeholder, int] = {}
    for index, slot in enumerate(current_canonical.slots):
        value = slot.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        if index >= len(owner.slots):
            continue
        slot_map[value] = index
    return slot_map
