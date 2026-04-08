from __future__ import annotations

import unittest
from typing import Any, cast

from protobase import flux, frozendict

import protomorph as pm
from protomorph import logic
from protomorph.logic import queryset as logic_queryset


REL_TYPES: dict[tuple[str, int], type[pm.Builtin]] = {}
REL_TYPES_BY_NAME: dict[str, set[type[pm.Builtin]]] = {}


def _rel_type(name: str, arity: int) -> type[pm.Builtin]:
    key = (name, arity)
    cls = REL_TYPES.get(key)
    if cls is not None:
        return cls

    annotations = {f"arg_{index}": pm.Val for index in range(arity)}
    cls_name = f"{name.title().replace('_', '').replace('-', '')}{arity}"
    cls = type(cls_name, (pm.Builtin,), {"__module__": __name__, "__annotations__": annotations})
    REL_TYPES[key] = cls
    REL_TYPES_BY_NAME.setdefault(name, set()).add(cls)
    return cls


class Unary(pm.Builtin):
    name: pm.Val
    value: pm.Val


def rel(name: Any, *args: Any) -> pm.Val:
    if not isinstance(name, str):
        raise TypeError(f"rel() expects a string predicate name, got {type(name).__name__}")
    cls = _rel_type(name, len(args))
    return pm.val(cls(*(pm.val(arg) for arg in args)))


def tup(*items: Any) -> pm.Val:
    return pm.val(*items)


def unary(name: Any, value: Any) -> pm.Val:
    return pm.val(Unary(pm.val(name), pm.val(value)))


def ctrl(name: str, *args: Any) -> pm.Val:
    if not args:
        return rel("ctrl", name)
    return rel("ctrl", tup(name, *args))


def is_rel_goal(carrier: pm.Val, name: str) -> bool:
    return type(carrier.fetch()) in REL_TYPES_BY_NAME.get(name, set())


def reducible_assertion(goal: pm.Val) -> logic.Assertion:
    return logic.Assertion(pm.val(logic.Reducible(goal.descriptor)))


class IdentityRealm(pm.Realm):
    facts: tuple[pm.Val, ...] = ()
    assertions: frozenset[logic.Assertion] = frozenset()

    @flux.property
    def logic_assertions(self):
        return frozenset(logic.Assertion(fact) for fact in self.facts) | self.assertions

    def eval(self, carrier, *, to):
        _ = to
        value = carrier.fetch()
        if is_rel_goal(carrier, "ctrl") and value.arg_0.fetch() == "identity":
            return pm.val(logic.Reduced(rel("fact", 1)))
        raise NotImplementedError("unsupported")


class TestLogicQuerySet(unittest.TestCase):
    def test_queryset_answers_from_local_facts(self):
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        session = engine.session().with_local_facts(rel("parent", 1, 2))
        who = pm.var("Who")
        goal = rel("parent", 1, who)

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), 2)

    def test_queryset_answers_from_local_varying_tuple_facts(self):
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        session = engine.session().with_local_facts(rel("pair", tup(1, 2)))
        who = pm.var("Who")
        goal = rel("pair", tup(1, who))

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), 2)

    def test_queryset_reduces_ctrl_goals(self):
        realm = IdentityRealm(
            facts=(rel("fact", 1),),
            assertions=frozenset((reducible_assertion(ctrl("identity")),)),
        )
        engine = logic.Solver(realm)
        goal = ctrl("identity")

        queryset = engine.session().queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)

    def test_eval_as_ctrl_adapts_errors_to_failed(self):
        class FailingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = (carrier, to)
                raise RuntimeError("boom")

        engine = logic.Solver(FailingRealm(assertions=frozenset((reducible_assertion(ctrl("identity")),))))
        ctrl_value = engine.eval_as_ctrl(ctrl("identity"))

        self.assertIsInstance(ctrl_value.fetch(), logic.Failed)

    def test_queryset_reduction_is_additive_with_normal_facts(self):
        class ChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if is_rel_goal(carrier, "ctrl") and isinstance(value.arg_0.fetch(), tuple):
                    payload = value.arg_0.fetch()
                    if len(payload) == 2 and payload[0] == "choice":
                        placeholder = cast(pm.Placeholder, payload[1].fetch())
                        return pm.val(
                            logic.Answers(
                                (
                                    logic.Answer(carrier, frozendict(((placeholder, pm.val(1)),))),
                                )
                            )
                        )
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = ChoiceRealm(assertions=frozenset((reducible_assertion(ctrl("choice", who)),)))
        solver = logic.Solver(realm)
        goal = ctrl("choice", who)
        queryset = solver.session().with_local_facts(ctrl("choice", 2)).queryset(goal).continue_()

        values = {answer.subst[who].fetch() for answer in queryset.query(goal).answers}
        self.assertEqual(values, {1, 2})

    def test_queryset_failed_reducible_does_not_hide_normal_proof(self):
        class FailedRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                if is_rel_goal(carrier, "ctrl"):
                    return pm.val(logic.Failed("no builtin answer"))
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = FailedRealm(assertions=frozenset((reducible_assertion(ctrl("choice", who)),)))
        solver = logic.Solver(realm)
        goal = ctrl("choice", who)
        queryset = solver.session().with_local_facts(ctrl("choice", 2)).queryset(goal).continue_()

        query = queryset.query(goal)
        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), 2)

    def test_queryset_blocked_reducible_does_not_hide_normal_proof(self):
        class BlockingChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                if is_rel_goal(carrier, "ctrl"):
                    return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = BlockingChoiceRealm(assertions=frozenset((reducible_assertion(ctrl("choice", who)),)))
        solver = logic.Solver(realm)
        goal = ctrl("choice", who)
        queryset = solver.session().with_local_facts(ctrl("choice", 2)).queryset(goal).continue_()

        query = queryset.query(goal)
        self.assertTrue(query.is_blocked)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), 2)

    def test_queryset_reduction_is_additive_with_assertions(self):
        class ChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if is_rel_goal(carrier, "ctrl") and isinstance(value.arg_0.fetch(), tuple):
                    payload = value.arg_0.fetch()
                    if len(payload) == 2 and payload[0] == "choice":
                        placeholder = cast(pm.Placeholder, payload[1].fetch())
                        return pm.val(
                            logic.Answers(
                                (
                                    logic.Answer(carrier, frozendict(((placeholder, pm.val(1)),))),
                                )
                            )
                        )
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        x = pm.var("X")
        realm = ChoiceRealm(
            assertions=frozenset(
                (
                    reducible_assertion(ctrl("choice", who)),
                    logic.Assertion(ctrl("choice", 2)),
                    logic.Assertion(
                        rel("result", x),
                        (logic.Premise(ctrl("choice", x)),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        goal = rel("result", who)
        queryset = solver.session().queryset(goal).continue_()

        values = {answer.subst[who].fetch() for answer in queryset.query(goal).answers}
        self.assertEqual(values, {1, 2})

    def test_queryset_solves_assertions_against_local_facts(self):
        x = pm.var("X")
        y = pm.var("Y")
        z = pm.var("Z")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        rel("grandparent", x, y),
                        (
                            logic.Premise(rel("parent", x, z)),
                            logic.Premise(rel("parent", z, y)),
                        ),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = rel("grandparent", 1, who)
        session = solver.session().with_local_facts(rel("parent", 1, 2), rel("parent", 2, 3))

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), 3)

    def test_queryset_creates_internal_tables_for_recursive_assertions(self):
        x = pm.var("X")
        y = pm.var("Y")
        z = pm.var("Z")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(rel("ancestor", x, y), (logic.Premise(rel("parent", x, y)),)),
                    logic.Assertion(
                        rel("ancestor", x, y),
                        (
                            logic.Premise(rel("parent", x, z)),
                            logic.Premise(rel("ancestor", z, y)),
                        ),
                    ),
                )
            )
        )
        solver = logic.Solver(realm=realm)
        who = pm.var("Who")
        goal = rel("ancestor", 1, who)
        session = solver.session().with_local_facts(rel("parent", 1, 2), rel("parent", 2, 3))

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        values = {answer.subst[who].fetch() for answer in query.answers}
        self.assertEqual(values, {2, 3})
        self.assertGreater(len(queryset.state.tables_by_key), len(queryset.state.roots))
        self.assertTrue(any(is_rel_goal(table.goal, "ancestor") for table in queryset.state.tables_by_key.values()))

    def test_pending_branch_is_owned_by_table(self):
        class BlockingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                if isinstance(carrier.fetch(), Unary) and carrier.fetch().name.fetch() == "wait":
                    return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        x = pm.var("X")
        realm = BlockingRealm(
            assertions=frozenset((logic.Assertion(rel("root", x), (logic.Premise(unary("wait", x)),)),))
        )
        solver = logic.Solver(BlockingRealm(assertions=realm.assertions | frozenset((reducible_assertion(unary("wait", x)),))))
        goal = rel("root", 1)

        queryset = solver.session().queryset(goal).continue_()
        table = queryset.table(goal)

        self.assertTrue(table.pending)
        branch = table.pending[0]
        self.assertEqual(branch.table_key, table.key)
        self.assertEqual(branch.blocked_goal.fetch(), Unary(pm.val("wait"), pm.val(1)))
        self.assertEqual(len(branch.active_frames), 1)
        self.assertEqual(branch.active_frames[0].table_key, table.key)

    def test_equivalent_roots_share_canonical_table(self):
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        session = engine.session().with_local_facts(rel("parent", 1, 2))
        who = pm.var("Who")
        child = pm.var("Child")
        goal_one = rel("parent", 1, who)
        goal_two = rel("parent", 1, child)

        queryset = session.queryset(goal_one, goal_two).continue_()
        root_one = next(root for root in queryset.state.roots if root.goal == goal_one)
        root_two = next(root for root in queryset.state.roots if root.goal == goal_two)

        self.assertEqual(repr(root_one.table_key), repr(root_two.table_key))

    def test_continue_retries_pending_branch(self):
        class FlippingRealm(IdentityRealm):
            should_block: bool = True

            def eval(self, carrier, *, to):
                _ = to
                if isinstance(carrier.fetch(), Unary) and carrier.fetch().name.fetch() == "wait":
                    if self.should_block:
                        return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                    return pm.val(logic.Reduced(rel("done", 1)))
                raise NotImplementedError("unsupported")

        x = pm.var("X")
        realm = FlippingRealm(assertions=frozenset((logic.Assertion(rel("root", x), (logic.Premise(unary("wait", x)),)),)))
        solver = logic.Solver(FlippingRealm(assertions=realm.assertions | frozenset((reducible_assertion(unary("wait", x)),)), should_block=True))
        goal = rel("root", 1)

        blocked = solver.session().queryset(goal).continue_()
        self.assertTrue(blocked.query(goal).is_blocked)

        resumed_solver = logic.Solver(FlippingRealm(assertions=realm.assertions | frozenset((reducible_assertion(unary("wait", x)),)), should_block=False))
        resumed = resumed_solver.session().continue_(blocked)

        self.assertTrue(resumed.query(goal).is_closed)

    def test_continue_wakes_negated_premise_when_subgoal_closes_without_answers(self):
        class BlockingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                if is_rel_goal(carrier, "wait"):
                    return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        assertion = logic.Assertion(rel("root"), (logic.Premise(rel("wait"), False),))
        solver = logic.Solver(BlockingRealm(assertions=frozenset((assertion, reducible_assertion(rel("wait"))))))
        goal = rel("root")

        blocked = solver.session().queryset(goal).continue_()
        self.assertTrue(blocked.query(goal).is_blocked)

        resumed_solver = logic.Solver(IdentityRealm(assertions=frozenset((assertion,))))
        resumed = resumed_solver.session().continue_(blocked)
        query = resumed.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)

    def test_continue_keeps_negated_premise_failed_when_subgoal_closes_with_answers(self):
        class BlockingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                if is_rel_goal(carrier, "wait"):
                    return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        assertion = logic.Assertion(rel("root"), (logic.Premise(rel("wait"), False),))
        solver = logic.Solver(BlockingRealm(assertions=frozenset((assertion, reducible_assertion(rel("wait"))))))
        goal = rel("root")

        blocked = solver.session().queryset(goal).continue_()
        self.assertTrue(blocked.query(goal).is_blocked)

        resumed_solver = logic.Solver(IdentityRealm(facts=(rel("wait"),), assertions=frozenset((assertion,))))
        resumed = resumed_solver.session().continue_(blocked)
        query = resumed.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 0)

    def test_continue_with_new_local_facts_retries_closed_tables(self):
        solver = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        who = pm.var("Who")
        goal = rel("parent", 1, who)

        initial = solver.session().queryset(goal).continue_()
        self.assertTrue(initial.query(goal).is_closed)
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(rel("parent", 1, 2)).continue_(initial)

        self.assertTrue(resumed.query(goal).is_closed)
        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), 2)
        self.assertGreater(resumed.state.binding_epoch, initial.state.binding_epoch)

    def test_continue_reopens_closed_positive_dependency_on_changed_local_fact(self):
        x = pm.var("X")
        realm = IdentityRealm(assertions=frozenset((logic.Assertion(rel("p", x), (logic.Premise(rel("q", x)),)),)))
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = rel("p", who)

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(rel("q", 1)).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), 1)

    def test_continue_reopens_closed_negative_dependency_on_changed_local_fact(self):
        x = pm.var("X")
        realm = IdentityRealm(assertions=frozenset((logic.Assertion(rel("safe", x), (logic.Premise(rel("blocked", x), False),)),)))
        solver = logic.Solver(realm)
        goal = rel("safe", 1)

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 1)

        resumed = solver.session().with_local_facts(rel("blocked", 1)).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 0)

    def test_promoted_answer_change_reopens_positive_dependents(self):
        x = pm.var("X")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(rel("q", x), (logic.Premise(rel("r", x)),)),
                    logic.Assertion(rel("p", x), (logic.Premise(rel("q", x)),)),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = rel("p", who)

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(rel("r", 1)).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), 1)

    def test_irrelevant_local_fact_change_does_not_reopen_unrelated_tables(self):
        x = pm.var("X")
        realm = IdentityRealm(assertions=frozenset((logic.Assertion(rel("p", x), (logic.Premise(rel("q", x)),)),)))
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = rel("p", who)

        initial = solver.session().queryset(goal).continue_()
        resumed = solver.session().with_local_facts(rel("z", 1)).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 0)

    def test_pending_table_retry_waits_for_new_table_state(self):
        key = rel("wait", 1)
        branch = logic.PendingBranch(table_key=key, blocked_goal=key, blocker=logic.PendingTable(key, key))

        self.assertFalse(logic_queryset._should_retry_branch(branch, {key: logic.QueryTable(key=key, goal=key, active=True, closed=False)}, {}, {}))
        self.assertTrue(logic_queryset._should_retry_branch(branch, {key: logic.QueryTable(key=key, goal=key, active=False, closed=True)}, {}, {}))

    def test_pending_negation_retry_waits_for_table_to_close(self):
        key = rel("negated", 1)
        branch = logic.PendingBranch(table_key=key, blocked_goal=key, blocker=logic.PendingNegation(key, key, key))

        self.assertFalse(logic_queryset._should_retry_branch(branch, {key: logic.QueryTable(key=key, goal=key, active=True, closed=False)}, {}, {}))
        self.assertTrue(logic_queryset._should_retry_branch(branch, {key: logic.QueryTable(key=key, goal=key, active=False, closed=True)}, {}, {}))

    def test_insufficient_bindings_retry_waits_for_relevant_binding_key(self):
        goal = rel("wait", pm.var("X"))
        relevant = pm.val(pm.Anchor("test.binds"))
        other = pm.val(pm.Anchor("test.other"))
        branch = logic.PendingBranch(
            table_key=goal,
            blocked_goal=goal,
            blocker=logic.InsufficientBindings(
                goal=goal,
                subject=goal,
                expected_bindings=frozenset((logic.ExpectedBinding(subject=goal, role="table", detail=relevant),)),
            ),
            binding_epoch=2,
        )

        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {relevant: 2}))
        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {other: 3}))
        self.assertTrue(logic_queryset._should_retry_branch(branch, {}, {}, {relevant: 3}))

    def test_insufficient_bindings_without_dependency_key_stays_asleep(self):
        goal = rel("wait", pm.var("X"))
        branch = logic.PendingBranch(
            table_key=goal,
            blocked_goal=goal,
            blocker=logic.InsufficientBindings(
                goal=goal,
                subject=goal,
                expected_bindings=frozenset((logic.ExpectedBinding(subject=goal, role="binding"),)),
            ),
            binding_epoch=2,
        )

        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {pm.val(pm.Anchor("test.binds")): 3}))

    def test_positive_cycle_without_coinduction_is_no_solution_with_cycle_cause(self):
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset((logic.Assertion(rel("loop", x), (logic.Premise(rel("loop", x)),)),)),
        )
        goal = rel("loop", 1)

        result = solver.session().queryset(goal).continue_().query(goal).result

        self.assertIsInstance(result, logic.NoSolution)
        result = cast(logic.NoSolution, result)
        self.assertIsInstance(result.cause, logic.Cycle)
        cycle = cast(logic.Cycle, result.cause)
        self.assertFalse(cycle.is_negative)

    def test_positive_cycle_with_coinduction_succeeds(self):
        loop_key = pm.val(rel("loop", 1).descriptor)
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset(
                (
                    logic.Assertion(pm.val(logic.CoinductiveCycle.new(loop_key))),
                    logic.Assertion(rel("loop", x), (logic.Premise(rel("loop", x)),)),
                )
            ),
        )
        goal = rel("loop", 1)

        query = solver.session().queryset(goal).continue_().query(goal)

        self.assertIsInstance(query.result, logic.Unique)
        self.assertEqual(len(query.answers), 1)

    def test_negative_cycle_is_no_solution_with_negative_cycle_cause(self):
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset((logic.Assertion(rel("loop", x), (logic.Premise(rel("loop", x), False),)),)),
        )
        goal = rel("loop", 1)

        result = solver.session().queryset(goal).continue_().query(goal).result

        self.assertIsInstance(result, logic.NoSolution)
        result = cast(logic.NoSolution, result)
        self.assertIsInstance(result.cause, logic.Cycle)
        cycle = cast(logic.Cycle, result.cause)
        self.assertTrue(cycle.is_negative)
