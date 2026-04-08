from __future__ import annotations

import unittest
from typing import Any, cast

from protobase import flux

import protomorph as pm
from protomorph import logic


class Link(pm.Builtin):
    left: pm.Val
    right: pm.Val


class Triple(pm.Builtin):
    head: pm.Val
    left: pm.Val
    right: pm.Val


class AssertionRealm(pm.Realm):
    assertions: frozenset[logic.Assertion] = frozenset()

    @flux.property
    def logic_assertions(self):
        return self.assertions


def t(*items: Any) -> pm.Val:
    return pm.val(*items)


def link(left: Any, right: Any) -> pm.Val:
    return pm.val(Link(pm.val(left), pm.val(right)))


def triple(head: Any, left: Any, right: Any) -> pm.Val:
    return pm.val(Triple(pm.val(head), pm.val(left), pm.val(right)))


def reducible_assertion(goal: pm.Val) -> logic.Assertion:
    return logic.Assertion(pm.val(logic.Reducible(goal.descriptor)))


class TestLogicEngine(unittest.TestCase):
    def test_head_key_uses_descriptor_for_general_values(self):
        goal = t("edge", 1, 2)
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))

        self.assertEqual(engine.head_key(goal).fetch(), goal.descriptor)

    def test_head_key_keeps_spec_specific_anchor_behavior(self):
        goal = pm.val(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")))
        engine = logic.Solver(pm.OverlayRealm(base=pm.NATIVE_REALM))

        self.assertEqual(engine.head_key(goal).fetch(), pm.Anchor("test.parent"))

    def test_logic_assertions_rejects_legacy_rule_like_objects(self):
        class LegacyRule:
            head: Any
            body: tuple[Any, ...]

            def __init__(self):
                self.head = ("safe", 1)
                self.body = (("blocked", 1),)

        realm = pm.OverlayRealm(base=pm.NATIVE_REALM, rules=cast(Any, (LegacyRule(),)))

        with self.assertRaises(TypeError):
            _ = realm.logic_assertions

    def test_engine_groups_assertions_by_descriptor_key_for_general_values(self):
        x = pm.var("X")
        realm = AssertionRealm(
            assertions=frozenset(
                (
                    logic.Assertion(link("banned", 1)),
                    logic.Assertion(
                        link("blocked", x),
                        (logic.Premise(link("banned", x)),),
                    ),
                    logic.Assertion(
                        link("safe", x),
                        (logic.Premise(link("blocked", x), False),),
                    ),
                )
            ),
        )
        engine = logic.Solver(realm)
        blocked_key = pm.val(link("blocked", x).descriptor)
        safe_key = pm.val(link("safe", x).descriptor)

        self.assertEqual(len(engine.assertions_for(blocked_key)), 1)
        self.assertEqual(engine.strata.stratum_of(safe_key), engine.strata.stratum_of(blocked_key) + 1)

    def test_engine_derives_positive_global_facts_for_general_values(self):
        x = pm.var("X")
        y = pm.var("Y")
        z = pm.var("Z")
        realm = AssertionRealm(
            assertions=frozenset(
                (
                    logic.Assertion(link(1, 2)),
                    logic.Assertion(link(2, 3)),
                    logic.Assertion(
                        triple("path", x, y),
                        (logic.Premise(link(x, y)),),
                    ),
                    logic.Assertion(
                        triple("path", x, y),
                        (
                            logic.Premise(link(x, z)),
                            logic.Premise(triple("path", z, y)),
                        ),
                    ),
                )
            ),
        )
        engine = logic.Solver(realm)
        path_key = pm.val(triple("path", 1, 2).descriptor)

        derived = {item.fetch() for item in engine.facts_for(path_key)}
        self.assertIn(Triple(pm.val("path"), pm.val(1), pm.val(3)), derived)

    def test_solver_is_reducible_uses_reducible_fact_for_general_values(self):
        goal = t("ctrl", "identity")
        realm = AssertionRealm(assertions=frozenset((reducible_assertion(t("ctrl", "identity")),)))
        engine = logic.Solver(realm)

        self.assertTrue(engine.is_reducible(goal))
        self.assertFalse(logic.Solver(AssertionRealm()).is_reducible(goal))

    def test_engine_derives_ground_fact_through_reduced_premise(self):
        class ReducedRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                if carrier.fetch() == ("ctrl", "reduced"):
                    return pm.val(logic.Reduced(t("base")))
                raise NotImplementedError("unsupported")

        realm = ReducedRealm(
            assertions=frozenset(
                (
                    reducible_assertion(t("ctrl", "reduced")),
                    logic.Assertion(t("base")),
                    logic.Assertion(
                        t("ready"),
                        (logic.Premise(t("ctrl", "reduced")),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(t("ready"), engine.facts_for(pm.val(t("ready").descriptor)))

    def test_engine_derives_ground_fact_through_expand_premise(self):
        class ExpandRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                if carrier.fetch() == ("ctrl", "expand"):
                    return pm.val(logic.Expand((t("left"), t("right"))))
                raise NotImplementedError("unsupported")

        realm = ExpandRealm(
            assertions=frozenset(
                (
                    reducible_assertion(t("ctrl", "expand")),
                    logic.Assertion(t("left")),
                    logic.Assertion(t("right")),
                    logic.Assertion(
                        t("ready"),
                        (logic.Premise(t("ctrl", "expand")),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(t("ready"), engine.facts_for(pm.val(t("ready").descriptor)))

    def test_engine_derives_ground_fact_through_answers_premise(self):
        class AnswersRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                if carrier.fetch() == ("ctrl", "answer"):
                    return pm.val(logic.Answers((logic.Answer(carrier),)))
                raise NotImplementedError("unsupported")

        realm = AnswersRealm(
            assertions=frozenset(
                (
                    reducible_assertion(t("ctrl", "answer")),
                    logic.Assertion(
                        t("ready"),
                        (logic.Premise(t("ctrl", "answer")),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertIn(t("ready"), engine.facts_for(pm.val(t("ready").descriptor)))

    def test_engine_does_not_derive_when_reducible_blocks(self):
        class BlockingRealm(AssertionRealm):
            def eval(self, carrier, *, to):
                _ = to
                if carrier.fetch() == ("ctrl", "wait"):
                    return pm.val(logic.Blocked(logic.PendingReduction(carrier, carrier)))
                raise NotImplementedError("unsupported")

        realm = BlockingRealm(
            assertions=frozenset(
                (
                    reducible_assertion(t("ctrl", "wait")),
                    logic.Assertion(
                        t("ready"),
                        (logic.Premise(t("ctrl", "wait")),),
                    ),
                )
            )
        )
        engine = logic.Solver(realm)

        self.assertNotIn(t("ready"), engine.facts_for(pm.val(t("ready").descriptor)))

    def test_solver_is_coinductive_uses_explicit_cycle_fact(self):
        left = t("loop", 1)
        mid = t("loop", 2)
        right = t("loop", 3)
        left_key = pm.val(left.descriptor)
        mid_key = pm.val(mid.descriptor)
        right_key = pm.val(right.descriptor)
        cycle = logic.Cycle.new(left, mid, right)
        inverse = logic.Cycle.new(left, right, mid)
        realm = AssertionRealm(
            assertions=frozenset((logic.Assertion(pm.val(logic.CoinductiveCycle.new(left_key, mid_key, right_key))),))
        )
        engine = logic.Solver(realm)

        self.assertTrue(engine.is_coinductive(cycle))
        self.assertFalse(engine.is_coinductive(inverse))

    def test_solver_is_coinductive_falls_back_to_edge_facts(self):
        left = link("left", 1)
        mid = link("mid", 2)
        right = link("right", 3)
        left_key = pm.val(left.descriptor)
        mid_key = pm.val(mid.descriptor)
        right_key = pm.val(right.descriptor)
        cycle = logic.Cycle.new(left, mid, right)
        coinductive_edges = (
            logic.CoinductiveEdge(left_key, mid_key),
            logic.CoinductiveEdge(mid_key, right_key),
            logic.CoinductiveEdge(right_key, left_key),
        )
        partial_edges = coinductive_edges[:-1]
        realm = AssertionRealm(assertions=frozenset(tuple(logic.Assertion(pm.val(edge)) for edge in coinductive_edges)))
        partial = AssertionRealm(assertions=frozenset(tuple(logic.Assertion(pm.val(edge)) for edge in partial_edges)))

        self.assertTrue(logic.Solver(realm).is_coinductive(cycle))
        self.assertFalse(logic.Solver(partial).is_coinductive(cycle))
