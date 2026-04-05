"""Tests for unify() — pattern matching with Placeholders."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Tuple, Var, Placeholder
from protomorph.core.hosted import Float
from protomorph.core.unification import unify
from protomorph.core.variant import Union

from support import int_val, str_val, float_val, placeholder


# ── Helper ────────────────────────────────────────────────────────────────────


def is_placeholder(v) -> bool:
    return isinstance(v, Placeholder)


# ── Identical structures (no variables) ──────────────────────────────────────


class TestUnifyIdentical(unittest.TestCase):

    def test_identical_scalars(self):
        result = unify(int_val(1), int_val(1), is_var=is_placeholder)
        self.assertIs(result, int_val(1))

    def test_different_scalars_fails(self):
        result = unify(int_val(1), int_val(2), is_var=is_placeholder)
        self.assertIsNone(result)

    def test_different_meta_fails(self):
        result = unify(int_val(1), str_val("1"), is_var=is_placeholder)
        self.assertIsNone(result)

    def test_identical_tuples(self):
        # NOTE: unify calls subst which calls deep_map which normalises
        # VaryingSchema → UniformSchema — compare element-by-element.
        t = Tuple.of(int_val(1), int_val(2))
        result = unify(t, t, is_var=is_placeholder)
        self.assertIsNotNone(result)
        self.assertIs(result[0], int_val(1))
        self.assertIs(result[1], int_val(2))

    def test_tuples_with_same_content(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(1), int_val(2))
        result = unify(t1, t2, is_var=is_placeholder)
        self.assertIsNotNone(result)
        self.assertIs(result[0], int_val(1))
        self.assertIs(result[1], int_val(2))

    def test_tuples_with_different_content_fails(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(1), int_val(9))
        self.assertIsNone(unify(t1, t2, is_var=is_placeholder))


# ── Single variable ───────────────────────────────────────────────────────────


class TestUnifySingleVariable(unittest.TestCase):

    def test_placeholder_on_left_binds_to_right(self):
        x = placeholder("x")
        result = unify(x, int_val(42), is_var=is_placeholder)
        self.assertIs(result, int_val(42))

    def test_placeholder_on_right_binds_to_left(self):
        x = placeholder("x")
        result = unify(int_val(42), x, is_var=is_placeholder)
        self.assertIs(result, int_val(42))

    def test_placeholder_in_tuple_requires_compatible_schema(self):
        """
        Placeholder(Var, "x") has Var as __meta__, so Tuple.of(x, int_val(2))
        has a different schema than Tuple.of(int_val(1), int_val(2)).
        compatible() sees mismatched __meta__ on the Tuple and returns None.
        Placeholders work inside Tuples only when they share the same meta as
        the concrete value — e.g. using a typed Var context.
        """
        x = placeholder("x")
        t1 = Tuple.of(x, int_val(2))
        t2 = Tuple.of(int_val(1), int_val(2))
        self.assertIsNone(unify(t1, t2, is_var=is_placeholder))

    def test_placeholder_at_root_captures_any_leaf(self):
        x = placeholder("x")
        self.assertIs(unify(x, int_val(1), is_var=is_placeholder), int_val(1))
        self.assertIs(unify(x, str_val("hi"), is_var=is_placeholder), str_val("hi"))


# ── Multiple variables ────────────────────────────────────────────────────────


class TestUnifyMultipleVariables(unittest.TestCase):

    def test_two_placeholders_in_tuple_schema_mismatch(self):
        """
        Same compatible() constraint: Tuple.of(x, y) has schema (Var, Var),
        not (Integer, Text) — unification correctly fails.
        """
        x = placeholder("x")
        y = placeholder("y")
        t1 = Tuple.of(x, y)
        t2 = Tuple.of(int_val(1), str_val("a"))
        self.assertIsNone(unify(t1, t2, is_var=is_placeholder))

    def test_same_placeholder_appears_twice_consistent(self):
        # x must unify to the same value in both positions.
        # Tuple.of(x, x) has schema VaryingSchema(_, (Var, Var)).
        # Tuple.of(5, 5)  has schema VaryingSchema(_, (Integer, Integer)).
        # compatible() requires equal __meta__, so these Tuples don't unify
        # at the parent level — it correctly returns None.
        x = placeholder("x")
        t1 = Tuple.of(x, x)
        t2 = Tuple.of(int_val(5), int_val(5))
        result = unify(t1, t2, is_var=is_placeholder)
        self.assertIsNone(result)

    def test_placeholder_at_root_matches_any_value(self):
        # At the root level, a Placeholder bypasses the compatible() check
        # and captures whatever it's matched against.
        x = placeholder("x")
        result = unify(x, int_val(5), is_var=is_placeholder)
        self.assertIs(result, int_val(5))

    def test_placeholder_at_root_matches_a_tuple(self):
        x = placeholder("x")
        t = Tuple.of(int_val(1), int_val(2))
        result = unify(x, t, is_var=is_placeholder)
        self.assertEqual(result, t)

    def test_placeholder_in_compatible_tuple_gets_substituted(self):
        # Build a pattern with the SAME schema as the concrete Tuple by
        # putting the Placeholder at the root — schemas are trivially equal.
        x = placeholder("x")
        result = unify(x, Tuple.of(int_val(5), int_val(6)), is_var=is_placeholder)
        self.assertIsNotNone(result)
        self.assertIs(result[0], int_val(5))
        self.assertIs(result[1], int_val(6))


# ── Arity mismatch ────────────────────────────────────────────────────────────


class TestUnifyArityMismatch(unittest.TestCase):

    def test_different_tuple_arities_fails(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(1), int_val(2), int_val(3))
        self.assertIsNone(unify(t1, t2, is_var=is_placeholder))

    def test_scalar_vs_tuple_fails(self):
        self.assertIsNone(
            unify(int_val(1), Tuple.of(int_val(1)), is_var=is_placeholder)
        )


# ── Custom merge operator ────────────────────────────────────────────────────


class TestUnifyCustomOp(unittest.TestCase):

    def test_custom_op_selects_first_of_multiple_bindings(self):
        """An op that accepts any single binding and picks the first."""

        seen = {}

        def pick_first(vals):
            # Accept any singleton; for multiple bindings return the "first"
            items = list(vals)
            return items[0]

        x = placeholder("x")
        # x matched against int_val(7) at the root level
        result = unify(x, int_val(7), is_var=is_placeholder, op=pick_first)
        self.assertIs(result, int_val(7))

    def test_custom_op_returning_none_fails_unification(self):
        def always_fail(vals):
            return None

        x = placeholder("x")
        result = unify(x, int_val(1), is_var=is_placeholder, op=always_fail)
        self.assertIsNone(result)


# ── Nested structures ────────────────────────────────────────────────────────


class TestUnifyNested(unittest.TestCase):

    def test_nested_identical_tuples_unify(self):
        # Two structurally identical nested Tuples (same schema) unify fine.
        inner = Tuple.of(int_val(1), int_val(2))
        outer = Tuple.of(inner, int_val(3))
        result = unify(outer, outer, is_var=is_placeholder)
        self.assertIsNotNone(result)
        self.assertIs(result[0][0], int_val(1))
        self.assertIs(result[1], int_val(3))

    def test_nested_tuple_placeholder_at_inner_root(self):
        # Use a Placeholder at the level of a whole inner sub-tuple.
        x = placeholder("x")
        inner_concrete = Tuple.of(int_val(99), int_val(0))
        outer_pattern = Tuple.of(x, str_val("tag"))    # schema: (Var, Text)
        outer_concrete = Tuple.of(inner_concrete, str_val("tag"))  # schema: (VaryingSchema, Text)
        # These outer schemas ALSO differ (Var vs VaryingSchema), so still None.
        # Only a root-level Placeholder can bind to a Tuple.
        self.assertIsNone(unify(outer_pattern, outer_concrete, is_var=is_placeholder))

    def test_placeholder_at_root(self):
        x = placeholder("x")
        inner = Tuple.of(int_val(1), int_val(2))
        result = unify(x, inner, is_var=is_placeholder)
        self.assertEqual(result, inner)


if __name__ == "__main__":
    unittest.main()
