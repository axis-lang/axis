from __future__ import annotations

import unittest

from pm import Spec, placeholder
from pm.reasoning import Rule
from pm.reasoning.stratify import build_dependency_graph, compute_sccs, compute_stratification


class TestReasoningStratify(unittest.TestCase):
    def test_dependency_graph_includes_body_only_anchor(self):
        x = placeholder("X")
        graph = build_dependency_graph((Rule(Spec.of("test.safe", x), (Spec.of("test.blocked", x),)),))

        self.assertIn("test.safe", graph.anchors)
        self.assertIn("test.blocked", graph.anchors)

    def test_cross_anchor_negative_cycle_marks_component(self):
        x = placeholder("X")
        rules = (
            Rule(Spec.of("test.a", x), (Spec.of("std.logic.Not", Spec.of("test.b", x)),)),
            Rule(Spec.of("test.b", x), (Spec.of("std.logic.Not", Spec.of("test.a", x)),)),
        )
        graph = build_dependency_graph(rules)
        sccs = compute_sccs(graph)
        plan = compute_stratification(graph, sccs)

        self.assertTrue(plan.has_negative_cycle("test.a"))
        self.assertTrue(plan.has_negative_cycle("test.b"))
        self.assertEqual(plan.component_of("test.a"), plan.component_of("test.b"))

    def test_negative_dependency_raises_stratum(self):
        x = placeholder("X")
        rules = (
            Rule(Spec.of("test.blocked", x), (Spec.of("test.banned", x),)),
            Rule(Spec.of("test.safe", x), (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),)),
        )
        graph = build_dependency_graph(rules)
        plan = compute_stratification(graph, compute_sccs(graph))

        self.assertEqual(plan.stratum_of("test.safe"), plan.stratum_of("test.blocked") + 1)


if __name__ == "__main__":
    unittest.main()
