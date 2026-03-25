from __future__ import annotations

import unittest
from typing import cast

from pm import Spec, placeholder, wrap
from pm.chalk import Ambiguous, ChalkSolver, NoSolution, RuleSet, Unique
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

    def test_chain_unique(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        solver = ChalkSolver(
            RuleSet(
                (
                    fact("test.parent", ALICE, BOB),
                    fact("test.parent", BOB, CAROL),
                    Rule(
                        Spec.of("test.gp", x, z),
                        (Spec.of("test.parent", x, y), Spec.of("test.parent", y, z)),
                    ),
                )
            )
        )

        q = placeholder("Q")
        result = solver.solve(Spec.of("test.gp", ALICE, q))

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], CAROL)

    def test_shared_query_variable(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    fact("test.parent", ALICE, BOB),
                    fact("test.typeof", BOB, INT),
                    Rule(
                        Spec.of("test.good", x),
                        (Spec.of("test.parent", ALICE, x), Spec.of("test.typeof", x, INT)),
                    ),
                )
            )
        )

        q = placeholder("Q")
        result = solver.solve(Spec.of("test.good", q))

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], BOB)

    def test_eq_reflexive_rule(self):
        t = placeholder("T")
        solver = ChalkSolver(RuleSet((Rule(Spec.of("std.rels.Eq", t, t), ()),)))

        x = placeholder("X")
        result = solver.solve(Spec.of("std.rels.Eq", INT, x))

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[x], INT)

    def test_recursive_base_case_is_ambiguous(self):
        x = placeholder("X")
        y = placeholder("Y")
        solver = ChalkSolver(
            RuleSet(
                (
                    fact("test.path", ALICE, BOB),
                    fact("test.edge", ALICE, BOB),
                    fact("test.edge", BOB, CAROL),
                    Rule(
                        Spec.of("test.path", x, y),
                        (Spec.of("test.edge", x, y),),
                    ),
                    Rule(
                        Spec.of("test.path", x, y),
                        (
                            Spec.of("test.edge", x, placeholder("M")),
                            Spec.of("test.path", placeholder("M"), y),
                        ),
                    ),
                )
            )
        )

        q = placeholder("Q")
        result = solver.solve(Spec.of("test.path", ALICE, q))

        self.assertIsInstance(result, Ambiguous)
        self.assertNotIn(q, cast(Ambiguous, result).subst)

    def test_recursive_without_base_is_no_solution(self):
        x = placeholder("X")
        solver = ChalkSolver(
            RuleSet(
                (
                    Rule(Spec.of("test.loop", x), (Spec.of("test.loop", x),)),
                )
            ),
            max_depth=32,
        )

        result = solver.solve(Spec.of("test.loop", ALICE))
        self.assertIsInstance(result, NoSolution)

    def test_rule_vars_do_not_alias_across_applications(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        solver = ChalkSolver(
            RuleSet(
                (
                    fact("test.edge", ALICE, BOB),
                    fact("test.edge", BOB, CAROL),
                    Rule(
                        Spec.of("test.link2", x, z),
                        (Spec.of("test.edge", x, y), Spec.of("test.edge", y, z)),
                    ),
                )
            )
        )

        q = placeholder("Q")
        result = solver.solve(Spec.of("test.link2", ALICE, q))

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], CAROL)


if __name__ == "__main__":
    unittest.main()
