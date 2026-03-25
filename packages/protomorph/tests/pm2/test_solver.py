from __future__ import annotations

import unittest
from typing import cast

from pm import (
    Placeholder, placeholder,
    LeafCarrier, Spec,
    Rule, Solver, Resolved, NewGoals, Failed,
    UnionFind, freshen_rule, wrap,
)


# ── helpers ───────────────────────────────────────────────────────

ALICE = Spec.of("test.alice")
BOB = Spec.of("test.bob")
CAROL = Spec.of("test.carol")

INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())
FLOAT = cast(Spec, wrap(float).fetch())
ANY = Spec.of("std.core.Any")


def is_var(carrier) -> bool:
    return isinstance(carrier.fetch(), Placeholder)


def fact(anchor: str, *args: object) -> Rule:
    """Convenience: a rule with empty body (a ground fact)."""
    return Rule(Spec.of(anchor, *args), ())


def _resolve_arg(solver: Solver, goal: Spec, offset: int):
    """Reify *goal* through the solver's subst and return arg at *offset*."""
    reified = solver.subst.reify(wrap(goal))
    return cast(Spec, reified.fetch()).args[offset].fetch()


# ── freshening ────────────────────────────────────────────────────


class TestFreshenRule(unittest.TestCase):
    def test_ground_rule_unchanged(self):
        r = fact("test.parent", ALICE, BOB)
        head, body = freshen_rule(r)
        self.assertIs(head, r.head)
        self.assertEqual(body, ())

    def test_variables_get_new_context(self):
        X, Y = placeholder("X"), placeholder("Y")
        r = Rule(
            Spec.of("test.rel", X, Y),
            (Spec.of("test.sub", X),),
        )
        head, body = freshen_rule(r)

        # Head vars should differ from originals
        head_carrier = wrap(head)
        head_vars = [
            leaf.fetch()
            for leaf in head_carrier.deep_iter()
            if isinstance(leaf.fetch(), Placeholder)
        ]
        self.assertTrue(all(v is not X and v is not Y for v in head_vars))

        # Body should use the SAME fresh vars as head
        body_carrier = wrap(body[0])
        body_vars = [
            leaf.fetch()
            for leaf in body_carrier.deep_iter()
            if isinstance(leaf.fetch(), Placeholder)
        ]
        self.assertEqual(len(body_vars), 1)
        x_head = next(v for v in head_vars if v.id == "X")
        x_body = body_vars[0]
        self.assertIs(x_head, x_body)

    def test_two_freshenings_are_independent(self):
        X = placeholder("X")
        r = Rule(Spec.of("test.rel", X), ())
        _, _ = freshen_rule(r)
        h1, _ = freshen_rule(r)
        h2, _ = freshen_rule(r)
        v1 = next(
            leaf.fetch()
            for leaf in wrap(h1).deep_iter()
            if isinstance(leaf.fetch(), Placeholder)
        )
        v2 = next(
            leaf.fetch()
            for leaf in wrap(h2).deep_iter()
            if isinstance(leaf.fetch(), Placeholder)
        )
        self.assertIsNot(v1, v2)


# ── step ──────────────────────────────────────────────────────────


class TestStep(unittest.TestCase):
    def test_fact_resolves(self):
        rules = [fact("test.parent", ALICE, BOB)]
        solver = Solver(rules, is_var)
        result = solver.step(Spec.of("test.parent", ALICE, BOB))
        self.assertIsInstance(result, Resolved)

    def test_no_match_fails(self):
        solver = Solver([], is_var)
        result = solver.step(Spec.of("test.unknown", ALICE))
        self.assertIsInstance(result, Failed)

    def test_var_in_goal_captures(self):
        rules = [fact("test.parent", ALICE, BOB)]
        solver = Solver(rules, is_var)
        X = placeholder("X")
        goal = Spec.of("test.parent", ALICE, X)
        result = solver.step(goal)
        self.assertIsInstance(result, Resolved)
        self.assertIs(_resolve_arg(solver, goal, 1), BOB)

    def test_chain_rule_returns_subgoals(self):
        X, Y, Z = placeholder("X"), placeholder("Y"), placeholder("Z")
        rules = [
            Rule(
                Spec.of("test.gp", X, Z),
                (Spec.of("test.parent", X, Y), Spec.of("test.parent", Y, Z)),
            )
        ]
        solver = Solver(rules, is_var)
        result = solver.step(Spec.of("test.gp", ALICE, placeholder("Q")))
        self.assertIsInstance(result, NewGoals)
        self.assertEqual(len(cast(NewGoals, result).goals), 2)


# ── solve ─────────────────────────────────────────────────────────


class TestSolve(unittest.TestCase):
    def test_single_fact(self):
        """parent(alice, bob). ?- parent(alice, X). → X = bob"""
        rules = [fact("test.parent", ALICE, BOB)]
        solver = Solver(rules, is_var)
        X = placeholder("X")
        goal = Spec.of("test.parent", ALICE, X)
        solver.add_goal(goal)
        self.assertTrue(solver.solve())
        self.assertIs(_resolve_arg(solver, goal, 1), BOB)

    def test_chain_derivation(self):
        """grandparent(X,Z) :- parent(X,Y), parent(Y,Z).
        parent(alice,bob). parent(bob,carol).
        ?- grandparent(alice, Q). → Q = carol
        """
        X, Y, Z = placeholder("X"), placeholder("Y"), placeholder("Z")
        rules = [
            fact("test.parent", ALICE, BOB),
            fact("test.parent", BOB, CAROL),
            Rule(
                Spec.of("test.gp", X, Z),
                (Spec.of("test.parent", X, Y), Spec.of("test.parent", Y, Z)),
            ),
        ]
        solver = Solver(rules, is_var)
        Q = placeholder("Q")
        goal = Spec.of("test.gp", ALICE, Q)
        solver.add_goal(goal)
        self.assertTrue(solver.solve())
        self.assertIs(_resolve_arg(solver, goal, 1), CAROL)

    def test_type_equality_reflexivity(self):
        """eq(T, T) :- . (reflexivity)
        ?- eq(Integer, X). → X = Integer
        """
        T = placeholder("T")
        rules = [Rule(Spec.of("std.rels.Eq", T, T), ())]
        solver = Solver(rules, is_var)
        X = placeholder("X")
        goal = Spec.of("std.rels.Eq", INT, X)
        solver.add_goal(goal)
        self.assertTrue(solver.solve())
        self.assertIs(_resolve_arg(solver, goal, 1), INT)

    def test_no_matching_rule_fails(self):
        solver = Solver([], is_var)
        solver.add_goal(Spec.of("test.nonexistent"))
        self.assertFalse(solver.solve())

    def test_multiple_goals(self):
        """Solve two goals that share a variable."""
        rules = [
            fact("test.parent", ALICE, BOB),
            fact("test.typeof", BOB, INT),
        ]
        solver = Solver(rules, is_var)
        X = placeholder("X")
        T = placeholder("T")
        g1 = Spec.of("test.parent", ALICE, X)
        g2 = Spec.of("test.typeof", X, T)
        solver.add_goal(g1)
        solver.add_goal(g2)
        self.assertTrue(solver.solve())
        self.assertIs(_resolve_arg(solver, g1, 1), BOB)
        self.assertIs(_resolve_arg(solver, g2, 1), INT)

    def test_shared_subst(self):
        """External UnionFind shared with the solver."""
        uf = UnionFind(is_var)
        rules = [fact("test.parent", ALICE, BOB)]
        solver = Solver(rules, is_var, subst=uf)
        X = placeholder("X")
        goal = Spec.of("test.parent", ALICE, X)
        solver.add_goal(goal)
        self.assertTrue(solver.solve())
        self.assertIs(_resolve_arg(solver, goal, 1), BOB)

    def test_iteration_limit(self):
        """Infinite loop is caught by max_iterations."""
        X = placeholder("X")
        rules = [
            Rule(Spec.of("test.loop", X), (Spec.of("test.loop", X),)),
        ]
        solver = Solver(rules, is_var, max_iterations=50)
        solver.add_goal(Spec.of("test.loop", ALICE))
        self.assertFalse(solver.solve())


if __name__ == "__main__":
    unittest.main()
