from __future__ import annotations

import unittest
from typing import Any
from typing import cast

from protobase import flux

import protomorph as pm
from protomorph import logic


class AssertionRealm(pm.Realm):
    assertions: frozenset[logic.Assertion] = frozenset()

    @flux.property
    def logic_assertions(self):
        return self.assertions


def reducible_assertion(goal: pm.Spec) -> logic.Assertion:
    return logic.Assertion(pm.wrap(logic.Reducible(pm.wrap(goal).descriptor)))


class TestLogicEngine(unittest.TestCase):
    def test_head_key_uses_anchor_for_spec_carriers(self):
        goal = pm.wrap(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")))
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))

        self.assertEqual(engine.head_key(goal).fetch(), pm.Anchor("test.parent"))

    def test_head_key_uses_descriptor_for_builtin_carriers(self):
        cycle = logic.Cycle.new(pm.wrap(pm.Anchor("test.left")), pm.wrap(pm.Anchor("test.right")))
        goal = pm.wrap(logic.CoinductiveCycle.new(pm.wrap(pm.Anchor("test.left")), pm.wrap(pm.Anchor("test.right"))))
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))

        self.assertEqual(engine.head_key(goal).fetch(), goal.descriptor)

    def test_logic_assertions_rejects_legacy_rule_like_objects(self):
        class LegacyRule:
            head: Any
            body: tuple[Any, ...]

            def __init__(self):
                self.head = pm.Spec.of("test.safe")
                self.body = (pm.Spec.of("test.blocked"),)

        realm = pm.OverlayRealm(base=pm.NATIVE_REALM, rules=cast(Any, (LegacyRule(),)))

        with self.assertRaises(TypeError):
            _ = realm.logic_assertions

    def test_engine_adapts_realm_rules_and_stratifies(self):
        x = pm.placeholder("X")
        realm = AssertionRealm(
            assertions=frozenset(
                (
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.banned", pm.Spec.of("test.alice"))),
                    ),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.blocked", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.banned", x))),),
                    ),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.safe", x)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.blocked", x)), False),),
                    ),
                )
            ),
        )
        engine = logic.Solver(realm)
        blocked_key = pm.wrap(pm.Anchor("test.blocked"))
        safe_key = pm.wrap(pm.Anchor("test.safe"))

        self.assertEqual(len(engine.assertions_for(blocked_key)), 1)
        self.assertEqual(engine.strata.stratum_of(safe_key), engine.strata.stratum_of(blocked_key) + 1)

    def test_engine_derives_positive_global_facts(self):
        x = pm.placeholder("X")
        y = pm.placeholder("Y")
        z = pm.placeholder("Z")
        realm = AssertionRealm(
            assertions=frozenset(
                (
                    logic.Assertion(pm.wrap(pm.Spec.of("test.edge", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")))),
                    logic.Assertion(pm.wrap(pm.Spec.of("test.edge", pm.Spec.of("test.bob"), pm.Spec.of("test.carol")))),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.path", x, y)),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.edge", x, y))),),
                    ),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.path", x, y)),
                        (
                            logic.Premise(pm.wrap(pm.Spec.of("test.edge", x, z))),
                            logic.Premise(pm.wrap(pm.Spec.of("test.path", z, y))),
                        ),
                    ),
                )
            ),
        )
        engine = logic.Solver(realm)
        path_key = pm.wrap(pm.Anchor("test.path"))

        derived = {repr(item.fetch()) for item in engine.facts_for(path_key)}
        self.assertIn(repr(pm.Spec.of("test.path", pm.Spec.of("test.alice"), pm.Spec.of("test.carol"))), derived)

    def test_solver_is_reducible_uses_reducible_fact(self):
        goal = pm.wrap(pm.Spec.of("test.ctrl.identity"))
        realm = AssertionRealm(assertions=frozenset((reducible_assertion(pm.Spec.of("test.ctrl.identity")),)))
        engine = logic.Solver(realm)

        self.assertTrue(engine.is_reducible(goal))
        self.assertFalse(logic.Solver(AssertionRealm()).is_reducible(goal))

    def test_engine_derives_ground_fact_through_reduced_premise(self):
        class ReducedRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.reduced"):
                    return pm.wrap(logic.Reduced(pm.wrap(pm.Spec.of("test.base"))))
                raise NotImplementedError("unsupported")

        realm = ReducedRealm(
            assertions=frozenset(
                (
                    reducible_assertion(pm.Spec.of("test.ctrl.reduced")),
                    logic.Assertion(pm.wrap(pm.Spec.of("test.base"))),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ready")),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.ctrl.reduced"))),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(pm.wrap(pm.Spec.of("test.ready")), engine.facts_for(pm.wrap(pm.Anchor("test.ready"))))

    def test_engine_derives_ground_fact_through_expand_premise(self):
        class ExpandRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.expand"):
                    return pm.wrap(logic.Expand((pm.wrap(pm.Spec.of("test.left")), pm.wrap(pm.Spec.of("test.right")))))
                raise NotImplementedError("unsupported")

        realm = ExpandRealm(
            assertions=frozenset(
                (
                    reducible_assertion(pm.Spec.of("test.ctrl.expand")),
                    logic.Assertion(pm.wrap(pm.Spec.of("test.left"))),
                    logic.Assertion(pm.wrap(pm.Spec.of("test.right"))),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ready")),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.ctrl.expand"))),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(pm.wrap(pm.Spec.of("test.ready")), engine.facts_for(pm.wrap(pm.Anchor("test.ready"))))

    def test_engine_derives_ground_fact_through_answers_premise(self):
        class AnswersRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.answer"):
                    return pm.wrap(logic.Answers((logic.Answer(carrier),)))
                raise NotImplementedError("unsupported")

        realm = AnswersRealm(
            assertions=frozenset(
                (
                    reducible_assertion(pm.Spec.of("test.ctrl.answer")),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ready")),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.ctrl.answer"))),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(pm.wrap(pm.Spec.of("test.ready")), engine.facts_for(pm.wrap(pm.Anchor("test.ready"))))

    def test_engine_does_not_derive_when_reducible_blocks(self):
        class BlockingRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                value = carrier.fetch()
                if isinstance(value, pm.Spec) and value.anchor == pm.Anchor("test.ctrl.wait"):
                    return pm.wrap(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        realm = BlockingRealm(
            assertions=frozenset(
                (
                    reducible_assertion(pm.Spec.of("test.ctrl.wait")),
                    logic.Assertion(
                        pm.wrap(pm.Spec.of("test.ready")),
                        (logic.Premise(pm.wrap(pm.Spec.of("test.ctrl.wait"))),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertNotIn(pm.wrap(pm.Spec.of("test.ready")), engine.facts_for(pm.wrap(pm.Anchor("test.ready"))))

    def test_solver_is_coinductive_uses_explicit_cycle_fact(self):
        left_key = pm.wrap(pm.Anchor("test.left"))
        mid_key = pm.wrap(pm.Anchor("test.mid"))
        right_key = pm.wrap(pm.Anchor("test.right"))
        left = pm.wrap(pm.Spec.of("test.left"))
        mid = pm.wrap(pm.Spec.of("test.mid"))
        right = pm.wrap(pm.Spec.of("test.right"))
        cycle = logic.Cycle.new(left, mid, right)
        inverse = logic.Cycle.new(left, right, mid)
        realm = AssertionRealm(
            assertions=frozenset(
                (
                    logic.Assertion(pm.wrap(logic.CoinductiveCycle.new(left_key, mid_key, right_key))),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertTrue(engine.is_coinductive(cycle))
        self.assertFalse(engine.is_coinductive(inverse))

    def test_solver_is_coinductive_falls_back_to_edge_facts(self):
        left_key = pm.wrap(pm.Anchor("test.left"))
        mid_key = pm.wrap(pm.Anchor("test.mid"))
        right_key = pm.wrap(pm.Anchor("test.right"))
        left = pm.wrap(pm.Spec.of("test.left"))
        mid = pm.wrap(pm.Spec.of("test.mid"))
        right = pm.wrap(pm.Spec.of("test.right"))
        cycle = logic.Cycle.new(left, mid, right)
        coinductive_edges = (
            logic.CoinductiveEdge(left_key, mid_key),
            logic.CoinductiveEdge(mid_key, right_key),
            logic.CoinductiveEdge(right_key, left_key),
        )
        partial_edges = coinductive_edges[:-1]
        realm = AssertionRealm(
            assertions=frozenset(
                tuple(
                    logic.Assertion(pm.wrap(edge))
                    for edge in coinductive_edges
                )
            )
        )
        partial = AssertionRealm(
            assertions=frozenset(
                tuple(
                    logic.Assertion(pm.wrap(edge))
                    for edge in partial_edges
                )
            )
        )

        self.assertTrue(logic.Solver(realm).is_coinductive(cycle))
        self.assertFalse(logic.Solver(partial).is_coinductive(cycle))
