from __future__ import annotations

import unittest
from typing import cast

from protobase import flux, frozendict

import protomorph as pm
from protomorph import logic
from protomorph.logic import queryset as logic_queryset


class IdentityRealm(pm.Realm):
    facts: tuple[pm.Spec, ...] = ()
    assertions: frozenset[logic.Assertion] = frozenset()

    @flux.property
    def logic_assertions(self):
        return frozenset(logic.Assertion(pm.wrap(fact)) for fact in self.facts) | self.assertions

    @flux.property
    def anchors(self) -> frozenset[pm.Anchor]:
        return frozenset(fact.anchor for fact in self.facts)

    def facts_by_anchor(self, anchor: pm.Anchor) -> tuple[pm.Spec, ...]:
        return tuple(fact for fact in self.facts if fact.anchor == anchor)

    def rules_for_anchor(self, anchor: pm.Anchor):
        _ = anchor
        return ()

    def eval(self, carrier, *, to):
        _ = to
        value = carrier.fetch()
        if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.identity"):
            return pm.wrap(logic.Reduced(pm.wrap(pm.Spec.of("test.fact", pm.Spec.of("test.alice")))))
        raise NotImplementedError("unsupported")


def reducible_assertion(goal: pm.Spec) -> logic.Assertion:
    return logic.Assertion(pm.wrap(logic.Reducible(pm.wrap(goal).descriptor)))


class TestLogicQuerySet(unittest.TestCase):
    def test_queryset_answers_from_local_facts(self):
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        session = engine.session().with_local_facts(pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob"))))
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), who))

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), pm.Spec.of("test.bob"))

    def test_queryset_reduces_ctrl_goals(self):
        realm = IdentityRealm(
            facts=(pm.Spec.of("test.fact", pm.Spec.of("test.alice")),),
            assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.identity")),)),
        )
        engine = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.ctrl.identity"))

        queryset = engine.session().queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)

    def test_eval_as_ctrl_adapts_errors_to_failed(self):
        class FailingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = (carrier, to)
                raise RuntimeError("boom")

        engine = logic.Solver(
            FailingRealm(assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.identity")),)))
        )
        ctrl = engine.eval_as_ctrl(pm.wrap(pm.Spec.of("test.ctrl.identity")))

        self.assertIsInstance(ctrl.fetch(), logic.Failed)

    def test_queryset_reduction_is_additive_with_normal_facts(self):
        class ChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.choice"):
                    placeholder = value.args.content[0]
                    if not isinstance(placeholder, pm.Placeholder):
                        raise NotImplementedError("unsupported")
                    return pm.wrap(
                        logic.Answers(
                            (
                                logic.Answer(
                                    carrier,
                                    frozendict(((placeholder, pm.wrap(pm.Spec.of("test.alice"))),)),
                                ),
                            )
                        )
                    )
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = ChoiceRealm(assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.choice", who)),)))
        solver = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.ctrl.choice", who))
        queryset = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.ctrl.choice", pm.Spec.of("test.bob")))).queryset(goal).continue_()

        values = {answer.subst[who].fetch() for answer in queryset.query(goal).answers}
        self.assertEqual(values, {pm.Spec.of("test.alice"), pm.Spec.of("test.bob")})

    def test_queryset_failed_reducible_does_not_hide_normal_proof(self):
        class FailedRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.choice"):
                    return pm.wrap(logic.Failed("no builtin answer"))
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = FailedRealm(assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.choice", who)),)))
        solver = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.ctrl.choice", who))
        queryset = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.ctrl.choice", pm.Spec.of("test.bob")))).queryset(goal).continue_()

        query = queryset.query(goal)
        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), pm.Spec.of("test.bob"))

    def test_queryset_blocked_reducible_does_not_hide_normal_proof(self):
        class BlockingChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.choice"):
                    return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        realm = BlockingChoiceRealm(assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.choice", who)),)))
        solver = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.ctrl.choice", who))
        queryset = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.ctrl.choice", pm.Spec.of("test.bob")))).queryset(goal).continue_()

        query = queryset.query(goal)
        self.assertTrue(query.is_blocked)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), pm.Spec.of("test.bob"))

    def test_queryset_reduction_is_additive_with_assertions(self):
        class ChoiceRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.choice"):
                    placeholder = value.args.content[0]
                    if not isinstance(placeholder, pm.Placeholder):
                        raise NotImplementedError("unsupported")
                    return pm.wrap(
                        logic.Answers(
                            (
                                logic.Answer(
                                    carrier,
                                    frozendict(((placeholder, pm.wrap(pm.Spec.of("test.alice"))),)),
                                ),
                            )
                        )
                    )
                raise NotImplementedError("unsupported")

        who = pm.var("Who")
        x = pm.var("X")
        realm = ChoiceRealm(
            assertions=frozenset(
                (
                    reducible_assertion(pm.Spec.of("test.ctrl.choice", who)),
                    logic.Assertion(pm.wrap(pm.Spec.of("test.ctrl.choice", pm.Spec.of("test.bob")))),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.result", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.ctrl.choice", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.result", who))
        queryset = solver.session().queryset(goal).continue_()

        values = {answer.subst[who].fetch() for answer in queryset.query(goal).answers}
        self.assertEqual(values, {pm.Spec.of("test.alice"), pm.Spec.of("test.bob")})

    def test_queryset_solves_assertions_against_local_facts(self):
        x = pm.var("X")
        y = pm.var("Y")
        z = pm.var("Z")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.grandparent", x, y)),
                        (
                            logic.Premise(pm.wrap(pm.Spec.of("test.parent", x, z))),
                            logic.Premise(pm.wrap(pm.Spec.of("test.parent", z, y))),
                        ),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.grandparent", pm.Spec.of("test.alice"), who))
        session = solver.session().with_local_facts(
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob"))),
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.bob"), pm.Spec.of("test.carol"))),
        )

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 1)
        self.assertEqual(query.answers[0].subst[who].fetch(), pm.Spec.of("test.carol"))

    def test_queryset_creates_internal_tables_for_recursive_assertions(self):
        x = pm.var("X")
        y = pm.var("Y")
        z = pm.var("Z")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ancestor", x, y)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.parent", x, y))),),
                    ),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ancestor", x, y)),
                        (
                            logic.Premise(pm.wrap(pm.Spec.of("test.parent", x, z))),
                            logic.Premise(pm.wrap(pm.Spec.of("test.ancestor", z, y))),
                        ),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.ancestor", pm.Spec.of("test.alice"), who))
        session = solver.session().with_local_facts(
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob"))),
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.bob"), pm.Spec.of("test.carol"))),
        )

        queryset = session.queryset(goal).continue_()
        query = queryset.query(goal)

        values = {answer.subst[who].fetch() for answer in query.answers}
        self.assertEqual(values, {pm.Spec.of("test.bob"), pm.Spec.of("test.carol")})
        self.assertGreater(len(queryset.state.tables_by_key), len(queryset.state.roots))
        self.assertTrue(
            any(
                isinstance(table.goal.fetch(), pm.Spec)
                and table.goal.fetch().anchor == pm.Anchor("test.ancestor")
                and pm.Spec.of("test.bob") in table.goal.fetch().args.content
                for table in queryset.state.tables_by_key.values()
            )
        )

    def test_pending_branch_is_owned_by_table(self):
        class BlockingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.wait"):
                    return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        x = pm.var("X")
        realm = BlockingRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.root", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.wait", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(
            BlockingRealm(
                assertions=realm.assertions | frozenset((reducible_assertion(pm.Spec.of("test.wait", x)),)),
            )
        )
        goal = pm.wrap(pm.Spec.of("test.root", pm.Spec.of("test.alice")))

        queryset = solver.session().queryset(goal).continue_()
        table = queryset.table(goal)

        self.assertTrue(table.pending)
        branch = table.pending[0]
        self.assertEqual(branch.table_key, table.key)
        self.assertEqual(repr(branch.blocked_goal.fetch()), repr(pm.Spec.of("test.wait", pm.Spec.of("test.alice"))))
        self.assertEqual(len(branch.active_frames), 1)
        self.assertEqual(branch.active_frames[0].table_key, table.key)

    def test_equivalent_roots_share_canonical_table(self):
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        session = engine.session().with_local_facts(
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")))
        )
        who = pm.var("Who")
        child = pm.var("Child")
        goal_one = pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), who))
        goal_two = pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), child))

        queryset = session.queryset(goal_one, goal_two).continue_()
        root_one = next(root for root in queryset.state.roots if root.goal == goal_one)
        root_two = next(root for root in queryset.state.roots if root.goal == goal_two)

        self.assertEqual(repr(root_one.table_key), repr(root_two.table_key))

    def test_continue_retries_pending_branch(self):
        class FlippingRealm(IdentityRealm):
            should_block: bool = True

            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.wait"):
                    if self.should_block:
                        return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                    return pm.wrap(logic.Reduced(pm.wrap(pm.Spec.of("test.done", pm.Spec.of("test.alice")))))
                raise NotImplementedError("unsupported")

        x = pm.var("X")
        realm = FlippingRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.root", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.wait", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(
            FlippingRealm(
                assertions=realm.assertions | frozenset((reducible_assertion(pm.Spec.of("test.wait", x)),)),
                should_block=realm.should_block,
            )
        )
        goal = pm.wrap(pm.Spec.of("test.root", pm.Spec.of("test.alice")))

        blocked = solver.session().queryset(goal).continue_()
        self.assertTrue(blocked.query(goal).is_blocked)

        resumed_solver = logic.Solver(
            FlippingRealm(
                assertions=realm.assertions | frozenset((reducible_assertion(pm.Spec.of("test.wait", x)),)),
                should_block=False,
            )
        )
        resumed = resumed_solver.session().continue_(blocked)

        self.assertTrue(resumed.query(goal).is_closed)

    def test_continue_wakes_negated_premise_when_subgoal_closes_without_answers(self):
        class BlockingRealm(IdentityRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.wait"):
                    return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        assertion = logic.Assertion(
            pm.wrap(pm.Spec.of("test.root")),
            (logic.Premise(pm.wrap(pm.Spec.of("test.wait")), False),),
        )
        solver = logic.Solver(
            BlockingRealm(
                assertions=frozenset((assertion, reducible_assertion(pm.Spec.of("test.wait")))),
            ),
        )
        goal = pm.wrap(pm.Spec.of("test.root"))

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
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.wait"):
                    return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        assertion = logic.Assertion(
            pm.wrap(pm.Spec.of("test.root")),
            (logic.Premise(pm.wrap(pm.Spec.of("test.wait")), False),),
        )
        solver = logic.Solver(
            BlockingRealm(
                assertions=frozenset((assertion, reducible_assertion(pm.Spec.of("test.wait")))),
            ),
        )
        goal = pm.wrap(pm.Spec.of("test.root"))

        blocked = solver.session().queryset(goal).continue_()
        self.assertTrue(blocked.query(goal).is_blocked)

        resumed_solver = logic.Solver(
            IdentityRealm(
                facts=(pm.Spec.of("test.wait"),),
                assertions=frozenset((assertion,)),
            )
        )
        resumed = resumed_solver.session().continue_(blocked)
        query = resumed.query(goal)

        self.assertTrue(query.is_closed)
        self.assertEqual(len(query.answers), 0)

    def test_continue_with_new_local_facts_retries_closed_tables(self):
        solver = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), who))

        initial = solver.session().queryset(goal).continue_()
        self.assertTrue(initial.query(goal).is_closed)
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(
            pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")))
        ).continue_(initial)

        self.assertTrue(resumed.query(goal).is_closed)
        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), pm.Spec.of("test.bob"))
        self.assertGreater(resumed.state.binding_epoch, initial.state.binding_epoch)

    def test_continue_reopens_closed_positive_dependency_on_changed_local_fact(self):
        x = pm.var("X")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.p", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.q", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.p", who))

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.q", pm.Spec.of("test.alice")))).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), pm.Spec.of("test.alice"))

    def test_continue_reopens_closed_negative_dependency_on_changed_local_fact(self):
        x = pm.var("X")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.safe", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.blocked", x)), False),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        goal = pm.wrap(pm.Spec.of("test.safe", pm.Spec.of("test.alice")))

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 1)

        resumed = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.blocked", pm.Spec.of("test.alice")))).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 0)

    def test_promoted_answer_change_reopens_positive_dependents(self):
        x = pm.var("X")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.q", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.r", x))),),
                    ),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.p", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.q", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.p", who))

        initial = solver.session().queryset(goal).continue_()
        self.assertEqual(len(initial.query(goal).answers), 0)

        resumed = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.r", pm.Spec.of("test.alice")))).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 1)
        self.assertEqual(resumed.query(goal).answers[0].subst[who].fetch(), pm.Spec.of("test.alice"))

    def test_irrelevant_local_fact_change_does_not_reopen_unrelated_tables(self):
        x = pm.var("X")
        realm = IdentityRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.p", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.q", x))),),
                    ),
                )
            )
        )
        solver = logic.Solver(realm)
        who = pm.var("Who")
        goal = pm.wrap(pm.Spec.of("test.p", who))

        initial = solver.session().queryset(goal).continue_()
        resumed = solver.session().with_local_facts(pm.wrap(pm.Spec.of("test.z", pm.Spec.of("test.alice")))).continue_(initial)

        self.assertEqual(len(resumed.query(goal).answers), 0)

    def test_pending_table_retry_waits_for_new_table_state(self):
        key = pm.wrap(pm.Spec.of("test.wait", pm.Spec.of("test.alice")))
        branch = logic.PendingBranch(
            table_key=key,
            blocked_goal=key,
            blocker=logic.PendingTable(key, key),
        )

        self.assertFalse(
            logic_queryset._should_retry_branch(
                branch,
                {key: logic.QueryTable(key=key, goal=key, active=True, closed=False)},
                {},
                {},
            )
        )
        self.assertTrue(
            logic_queryset._should_retry_branch(
                branch,
                {key: logic.QueryTable(key=key, goal=key, active=False, closed=True)},
                {},
                {},
            )
        )

    def test_pending_negation_retry_waits_for_table_to_close(self):
        key = pm.wrap(pm.Spec.of("test.negated", pm.Spec.of("test.alice")))
        branch = logic.PendingBranch(
            table_key=key,
            blocked_goal=key,
            blocker=logic.PendingNegation(key, key, key),
        )

        self.assertFalse(
            logic_queryset._should_retry_branch(
                branch,
                {key: logic.QueryTable(key=key, goal=key, active=True, closed=False)},
                {},
                {},
            )
        )
        self.assertTrue(
            logic_queryset._should_retry_branch(
                branch,
                {key: logic.QueryTable(key=key, goal=key, active=False, closed=True)},
                {},
                {},
            )
        )

    def test_insufficient_bindings_retry_waits_for_relevant_binding_key(self):
        goal = pm.wrap(pm.Spec.of("test.wait", pm.var("X")))
        relevant = pm.wrap(pm.Anchor("test.binds"))
        other = pm.wrap(pm.Anchor("test.other"))
        branch = logic.PendingBranch(
            table_key=goal,
            blocked_goal=goal,
            blocker=logic.InsufficientBindings(
                goal=goal,
                subject=goal,
                expected_bindings=frozenset(
                    (logic.ExpectedBinding(subject=goal, role="table", detail=relevant),)
                ),
            ),
            binding_epoch=2,
        )

        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {relevant: 2}))
        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {other: 3}))
        self.assertTrue(logic_queryset._should_retry_branch(branch, {}, {}, {relevant: 3}))

    def test_insufficient_bindings_without_dependency_key_stays_asleep(self):
        goal = pm.wrap(pm.Spec.of("test.wait", pm.var("X")))
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

        self.assertFalse(logic_queryset._should_retry_branch(branch, {}, {}, {pm.wrap(pm.Anchor("test.binds")): 3}))

    def test_positive_cycle_without_coinduction_is_no_solution_with_cycle_cause(self):
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.loop", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.loop", x))),),
                    ),
                )
            ),
        )
        goal = pm.wrap(pm.Spec.of("test.loop", pm.Spec.of("test.alice")))

        result = solver.session().queryset(goal).continue_().query(goal).result

        self.assertIsInstance(result, logic.NoSolution)
        result = cast(logic.NoSolution, result)
        self.assertIsInstance(result.cause, logic.Cycle)
        cycle = cast(logic.Cycle, result.cause)
        self.assertFalse(cycle.is_negative)

    def test_positive_cycle_with_coinduction_succeeds(self):
        left = pm.wrap(pm.Anchor("test.loop"))
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset(
                (
                    logic.Assertion(pm.wrap(logic.CoinductiveCycle.new(left))),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.loop", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.loop", x))),),
                    ),
                )
            ),
        )
        goal = pm.wrap(pm.Spec.of("test.loop", pm.Spec.of("test.alice")))

        query = solver.session().queryset(goal).continue_().query(goal)

        self.assertIsInstance(query.result, logic.Unique)
        self.assertEqual(len(query.answers), 1)

    def test_negative_cycle_is_no_solution_with_negative_cycle_cause(self):
        x = pm.var("X")
        solver = logic.Solver(
            pm.OverlayRealm(base=pm.NATIVE_REALM),
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.loop", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.loop", x)), False),),
                    ),
                )
            ),
        )
        goal = pm.wrap(pm.Spec.of("test.loop", pm.Spec.of("test.alice")))

        result = solver.session().queryset(goal).continue_().query(goal).result

        self.assertIsInstance(result, logic.NoSolution)
        result = cast(logic.NoSolution, result)
        self.assertIsInstance(result.cause, logic.Cycle)
        cycle = cast(logic.Cycle, result.cause)
        self.assertTrue(cycle.is_negative)
