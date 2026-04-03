from __future__ import annotations

import unittest

from protomorph import Spec, placeholder
from protomorph.reasoning import Engine, Rule, RuleSetDatabase, Unique


class TestReasoningEngine(unittest.TestCase):
    def test_engine_indexes_rules_and_facts_by_anchor(self):
        x = placeholder("X")
        y = placeholder("Y")
        rule = Rule(Spec.of("test.parent", x, y), ())
        fact = Spec.of("test.edge", Spec.of("test.alice"), Spec.of("test.bob"))
        db = RuleSetDatabase((rule,), (fact,))
        engine = Engine(db)

        self.assertEqual(engine.rules_for_anchor("test.parent"), (rule,))
        self.assertEqual(engine.facts_for_anchor("test.edge"), (fact,))
        self.assertEqual(engine.global_tables.rules_by_anchor["test.parent"], (rule,))
        self.assertEqual(engine.global_tables.facts_by_anchor["test.edge"], (fact,))

    def test_engine_builds_dependency_graph_and_strata(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        db = RuleSetDatabase(
            (
                Rule(Spec.of("test.path", x, y), (Spec.of("test.edge", x, y),)),
                Rule(
                    Spec.of("test.path", x, y),
                    (Spec.of("test.edge", x, z), Spec.of("test.path", z, y)),
                ),
                Rule(
                    Spec.of("test.safe", x),
                    (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                ),
            ),
            (
                Spec.of("test.edge", Spec.of("test.alice"), Spec.of("test.bob")),
                Spec.of("test.blocked", Spec.of("test.alice")),
            ),
        )
        engine = Engine(db)

        self.assertEqual(set(engine.dependency_graph.positive_of("test.path")), {"test.edge", "test.path"})
        self.assertEqual(engine.dependency_graph.negative_of("test.safe"), ("test.blocked",))
        self.assertEqual(engine.strata.stratum_of("test.safe"), engine.strata.stratum_of("test.blocked") + 1)
        self.assertFalse(engine.strata.has_negative_cycle("test.safe"))

    def test_engine_detects_positive_sccs(self):
        x = placeholder("X")
        db = RuleSetDatabase(
            (
                Rule(Spec.of("test.a", x), (Spec.of("test.b", x),)),
                Rule(Spec.of("test.b", x), (Spec.of("test.a", x),)),
            )
        )
        engine = Engine(db)

        component_id = engine.strata.component_of("test.a")
        self.assertEqual(component_id, engine.strata.component_of("test.b"))
        self.assertEqual(set(engine.sccs[component_id].anchors), {"test.a", "test.b"})

    def test_engine_detects_negative_cycles(self):
        x = placeholder("X")
        db = RuleSetDatabase(
            (
                Rule(Spec.of("test.loop", x), (Spec.of("std.logic.Not", Spec.of("test.loop", x)),)),
            )
        )
        engine = Engine(db)

        self.assertTrue(engine.strata.has_negative_cycle("test.loop"))

    def test_engine_global_tables_close_positive_recursion(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        db = RuleSetDatabase(
            rules=(
                Rule(Spec.of("test.path", x, y), (Spec.of("test.edge", x, y),)),
                Rule(
                    Spec.of("test.path", x, y),
                    (Spec.of("test.edge", x, z), Spec.of("test.path", z, y)),
                ),
            ),
            facts=(
                Spec.of("test.edge", Spec.of("test.alice"), Spec.of("test.bob")),
                Spec.of("test.edge", Spec.of("test.bob"), Spec.of("test.carol")),
            ),
        )
        engine = Engine(db)

        derived = {repr(item) for item in engine.global_tables.derived_facts_by_anchor["test.path"]}
        self.assertIn(repr(Spec.of("test.path", Spec.of("test.alice"), Spec.of("test.bob"))), derived)
        self.assertIn(repr(Spec.of("test.path", Spec.of("test.bob"), Spec.of("test.carol"))), derived)
        self.assertIn(repr(Spec.of("test.path", Spec.of("test.alice"), Spec.of("test.carol"))), derived)

        component_id = engine.strata.component_of("test.path")
        component_facts = {repr(item) for item in engine.global_tables.facts_by_component[component_id]}
        self.assertEqual(component_facts, derived)
        self.assertTrue(engine.global_tables.is_component_closed(component_id))
        self.assertEqual(engine.global_tables.facts_of_component(component_id), engine.global_tables.facts_by_component[component_id])
        self.assertEqual(
            engine.global_tables.derived_facts_of_component(component_id),
            engine.global_tables.derived_facts_by_component[component_id],
        )
        self.assertEqual(engine.facts_for_component(component_id), engine.global_tables.facts_by_component[component_id])
        self.assertEqual(engine.derived_facts_for_component(component_id), engine.global_tables.derived_facts_by_component[component_id])

    def test_engine_global_tables_close_lower_strata_for_negation(self):
        x = placeholder("X")
        db = RuleSetDatabase(
            rules=(
                Rule(Spec.of("test.blocked", x), (Spec.of("test.banned", x),)),
                Rule(
                    Spec.of("test.safe", x),
                    (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                ),
            ),
            facts=(Spec.of("test.banned", Spec.of("test.alice")),),
        )
        engine = Engine(db)

        self.assertIn(engine.strata.stratum_of("test.blocked"), engine.global_tables.closed_strata)
        blocked = {repr(item) for item in engine.global_tables.facts_by_anchor["test.blocked"]}
        self.assertIn(repr(Spec.of("test.blocked", Spec.of("test.alice"))), blocked)

    def test_engine_global_tables_do_not_derive_from_non_ground_negation(self):
        x = placeholder("X")
        db = RuleSetDatabase(
            rules=(
                Rule(
                    Spec.of("test.safe", Spec.of("test.alice")),
                    (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                ),
            )
        )
        engine = Engine(db)

        self.assertEqual(engine.global_tables.facts_by_anchor.get("test.safe", ()), ())

    def test_engine_global_tables_do_not_capture_contextual_answers(self):
        x = placeholder("X")
        y = placeholder("Y")
        db = RuleSetDatabase(
            rules=(Rule(Spec.of("test.path", x, y), (Spec.of("test.edge", x, y),)),)
        )
        engine = Engine(db)
        component_id = engine.strata.component_of("test.path")

        self.assertEqual(engine.global_tables.facts_by_anchor.get("test.path", ()), ())
        self.assertEqual(engine.global_tables.facts_by_component.get(component_id, ()), ())

        session = engine.session().with_local_facts(Spec.of("test.edge", Spec.of("test.alice"), Spec.of("test.bob")))
        result = session.query(Spec.of("test.path", Spec.of("test.alice"), Spec.of("test.bob"))).result.outcome

        self.assertEqual(engine.global_tables.facts_by_anchor.get("test.path", ()), ())
        self.assertEqual(engine.global_tables.facts_by_component.get(component_id, ()), ())
        self.assertIsInstance(result, Unique)


if __name__ == "__main__":
    unittest.main()
