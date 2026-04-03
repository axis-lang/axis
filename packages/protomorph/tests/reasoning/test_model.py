from __future__ import annotations

import unittest

from protomorph import Spec, placeholder
from protomorph.reasoning import NEGATION_ANCHOR, Rule, is_negation, unwrap_negation


class TestReasoningModel(unittest.TestCase):
    def test_rule_splits_positive_and_negative_goals(self):
        x = placeholder("X")
        y = placeholder("Y")
        positive = Spec.of("test.parent", x, y)
        negated_inner = Spec.of("test.blocked", x)
        negated = Spec.of(NEGATION_ANCHOR, negated_inner)

        rule = Rule(Spec.of("test.safe_parent", x, y), (positive, negated))

        self.assertEqual(rule.positive_goals, (positive,))
        self.assertEqual(rule.negative_goals, (negated_inner,))

    def test_negation_helpers_validate_shape(self):
        inner = Spec.of("test.blocked", Spec.of("test.alice"))
        negated = Spec.of(NEGATION_ANCHOR, inner)

        self.assertTrue(is_negation(negated))
        self.assertEqual(unwrap_negation(negated), inner)

        with self.assertRaises(ValueError):
            unwrap_negation(inner)


if __name__ == "__main__":
    unittest.main()
