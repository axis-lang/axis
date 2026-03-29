from __future__ import annotations

import unittest
from typing import cast

from pm import Spec, placeholder, wrap
from pm.chalk import (
    Ambiguous,
    ChalkSolver,
    Deferred,
    Floundered,
    KeyOfOperator,
    MixedCycle,
    NoSolution,
    RuleSet,
    Unique,
)
from pm.solver import Rule


ALICE = Spec.of("test.alice")
BOB = Spec.of("test.bob")
CAROL = Spec.of("test.carol")

INT = cast(Spec, wrap(int).fetch())


def fact(anchor: str, *args: object) -> Rule:
    return Rule(Spec.of(anchor, *args), ())


class TestChalkSolver(unittest.TestCase):
    def test_fact_unique(self):
        solver = ChalkSolver(RuleSet((fact("test.parent", ALICE, BOB),)))
        x = placeholder("X")
        result = solver.solve(Spec.of("test.parent", ALICE, x))

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[x], BOB)

    def test_answers_multiple_results_are_ambiguous(self):
        solver = ChalkSolver(RuleSet((fact("test.parent", ALICE, BOB), fact("test.parent", ALICE, CAROL))))
        q = placeholder("Q")

        result = solver.solve(Spec.of("test.parent", ALICE, q))
        self.assertIsInstance(result, Ambiguous)

    def test_recursive_without_base_is_no_solution(self):
        x = placeholder("X")
        solver = ChalkSolver(RuleSet((Rule(Spec.of("test.loop", x), (Spec.of("test.loop", x),)),)))

        result = solver.solve(Spec.of("test.loop", ALICE))
        self.assertIsInstance(result, NoSolution)

    def test_non_ground_negation_flounders(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                )
            )
        )

        q = placeholder("Q")
        result = solver.solve(Spec.of("test.safe", q))
        self.assertIsInstance(result, Floundered)

    def test_negative_fact_becomes_deferred_until_stratum_closed(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    fact("test.blocked", ALICE),
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                )
            )
        )

        result = solver.solve(Spec.of("test.safe", ALICE))
        self.assertIsInstance(result, Deferred)

    def test_mixed_cycle_reported_separately(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    Rule(Spec.of("test.co", x), (Spec.of("test.in", x),)),
                    Rule(Spec.of("test.in", x), (Spec.of("test.co", x),)),
                ),
                coinductive_anchors=frozenset(("test.co",)),
            )
        )

        result = solver.solve(Spec.of("test.co", ALICE))
        self.assertIsInstance(result, MixedCycle)

    def test_unhandled_operator_is_deferred(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    Rule(
                        Spec.of("test.inspect", x),
                        (Spec.of("test.requires", KeyOfOperator.of(x)),),
                    ),
                )
            )
        )
        result = solver.solve(Spec.of("test.inspect", KeyOfOperator.of(ALICE)))
        self.assertIsInstance(result, Deferred)

    @unittest.expectedFailure
    def test_keyof_deferred_until_structural_input_known(self):
        solver = ChalkSolver(RuleSet(()))
        q = placeholder("Q")
        result = solver.solve(Spec.of("std.rels.KeyOf", KeyOfOperator.of(q), placeholder("R")))
        self.assertIsInstance(result, Deferred)

    @unittest.expectedFailure
    def test_projection_deferred_until_receiver_known(self):
        solver = ChalkSolver(RuleSet(()))
        q = placeholder("Q")
        result = solver.solve(Spec.of("std.rels.Proj", q, Spec.of("Iterator"), "Item", placeholder("R")))
        self.assertIsInstance(result, Deferred)


if __name__ == "__main__":
    unittest.main()
