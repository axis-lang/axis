"""Tests for structural traversal — deep_iter, deep_map, subst, deep_zip."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Tuple, Var, Placeholder
from protomorph.core.hosted import Float
from protomorph.core.traversal import deep_zip

from support import int_val, str_val, float_val, placeholder


# ── deep_iter ─────────────────────────────────────────────────────────────────


class TestDeepIter(unittest.TestCase):

    def test_scalar_yields_itself(self):
        v = int_val(5)
        self.assertEqual(list(v.deep_iter()), [v])

    def test_flat_tuple_yields_all_elements(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3))
        self.assertEqual(list(t.deep_iter()), [int_val(1), int_val(2), int_val(3)])

    def test_nested_tuple_yields_all_leaves(self):
        inner = Tuple.of(int_val(10), int_val(20))
        outer = Tuple.of(inner, int_val(30))
        leaves = list(outer.deep_iter())
        self.assertEqual(leaves, [int_val(10), int_val(20), int_val(30)])

    def test_empty_tuple_yields_nothing(self):
        leaves = list(Tuple.Empty.deep_iter())
        self.assertEqual(leaves, [])

    def test_custom_is_leaf_stops_descent(self):
        # Treat everything as a leaf — should yield just the root
        t = Tuple.of(int_val(1), int_val(2))
        leaves = list(t.deep_iter(is_leaf=lambda v: True))
        self.assertEqual(leaves, [t])

    def test_deeply_nested_leaves_in_order(self):
        t = Tuple.of(
            Tuple.of(int_val(1), int_val(2)),
            Tuple.of(int_val(3), Tuple.of(int_val(4), int_val(5))),
        )
        leaves = list(t.deep_iter())
        self.assertEqual(leaves, [int_val(i) for i in [1, 2, 3, 4, 5]])


# ── deep_map ──────────────────────────────────────────────────────────────────


class TestDeepMap(unittest.TestCase):

    def test_identity_map_returns_equal_content(self):
        # NOTE: deep_map always calls reconstruct on non-leaves, which may
        # normalise VaryingSchema → UniformSchema when all metas are equal.
        # The resulting Tuple is semantically identical but may have a
        # different schema wrapper — compare element-by-element.
        t = Tuple.of(int_val(1), int_val(2))
        result = t.deep_map(lambda v: v)
        self.assertEqual(result.arity, 2)
        self.assertIs(result[0], int_val(1))
        self.assertIs(result[1], int_val(2))

    def test_map_transforms_all_leaves(self):
        t = Tuple.of(int_val(1), int_val(2))
        result = t.deep_map(lambda v: Integer.wrap(v.__data__ * 10))
        self.assertIs(result[0], int_val(10))
        self.assertIs(result[1], int_val(20))

    def test_map_on_scalar_applies_directly(self):
        result = int_val(5).deep_map(lambda v: int_val(v.__data__ + 1))
        self.assertIs(result, int_val(6))

    def test_map_changes_type(self):
        t = Tuple.of(int_val(1), int_val(2))
        result = t.deep_map(lambda v: str_val(str(v.__data__)))
        self.assertIs(result[0], str_val("1"))
        self.assertIs(result[1], str_val("2"))

    def test_map_on_nested_tuple_reaches_deep_leaves(self):
        inner = Tuple.of(int_val(3), int_val(4))
        outer = Tuple.of(int_val(1), inner)
        result = outer.deep_map(lambda v: Integer.wrap(v.__data__ + 100))
        self.assertIs(result[0], int_val(101))
        self.assertIs(result[1][0], int_val(103))
        self.assertIs(result[1][1], int_val(104))


# ── subst ─────────────────────────────────────────────────────────────────────


class TestSubst(unittest.TestCase):

    def test_subst_replaces_placeholder(self):
        x = placeholder("x")
        result = x.subst({x: int_val(42)})
        self.assertIs(result, int_val(42))

    def test_subst_in_tuple(self):
        x = placeholder("x")
        t = Tuple.of(x, int_val(0))
        result = t.subst({x: int_val(99)})
        self.assertIs(result[0], int_val(99))
        self.assertIs(result[1], int_val(0))

    def test_subst_two_placeholders(self):
        x = placeholder("x")
        y = placeholder("y")
        t = Tuple.of(x, y, x)
        result = t.subst({x: int_val(1), y: str_val("a")})
        self.assertIs(result[0], int_val(1))
        self.assertIs(result[1], str_val("a"))
        self.assertIs(result[2], int_val(1))

    def test_subst_missing_key_leaves_placeholder(self):
        x = placeholder("x")
        y = placeholder("y")
        t = Tuple.of(x, y)
        result = t.subst({x: int_val(1)})
        self.assertIs(result[0], int_val(1))
        # y is not in the mapping, so it remains
        self.assertIs(result[1], y)

    def test_subst_no_mapping_preserves_content(self):
        # Same schema-normalisation caveat as deep_map: compare element-by-element.
        t = Tuple.of(int_val(1), int_val(2))
        result = t.subst({})
        self.assertIs(result[0], int_val(1))
        self.assertIs(result[1], int_val(2))

    def test_subst_nested_placeholder(self):
        x = placeholder("x")
        inner = Tuple.of(x, int_val(0))
        outer = Tuple.of(inner, str_val("tag"))
        result = outer.subst({x: int_val(7)})
        self.assertIs(result[0][0], int_val(7))
        self.assertIs(result[1], str_val("tag"))


# ── search ────────────────────────────────────────────────────────────────────


class TestSearch(unittest.TestCase):

    def test_search_finds_direct_child(self):
        v = int_val(5)
        t = Tuple.of(v, int_val(6))
        self.assertTrue(t.search(v))

    def test_search_finds_deep_descendant(self):
        leaf = int_val(99)
        t = Tuple.of(Tuple.of(Tuple.of(leaf)))
        self.assertTrue(t.search(leaf))

    def test_search_returns_false_when_absent(self):
        t = Tuple.of(int_val(1), int_val(2))
        self.assertFalse(t.search(int_val(3)))

    def test_search_scalar_finds_itself(self):
        v = int_val(7)
        self.assertTrue(v.search(v))


# ── deep_zip ──────────────────────────────────────────────────────────────────


class TestDeepZip(unittest.TestCase):

    def test_zip_two_scalars(self):
        pairs = list(deep_zip(int_val(1), int_val(2)))
        self.assertEqual(pairs, [(int_val(1), int_val(2))])

    def test_zip_two_flat_tuples(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(3), int_val(4))
        pairs = list(deep_zip(t1, t2))
        # Visits: (t1,t2) then (1,3) then (2,4)
        self.assertEqual(pairs[0], (t1, t2))
        self.assertIn((int_val(1), int_val(3)), pairs)
        self.assertIn((int_val(2), int_val(4)), pairs)

    def test_zip_skip_stops_descent(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(3), int_val(4))
        walker = deep_zip(t1, t2)
        first_left, first_right = next(walker)
        self.assertIs(first_left, t1)
        walker.skip()
        # After skip, no more pairs should come from this branch
        remaining = list(walker)
        self.assertEqual(remaining, [])

    def test_zip_mismatched_arity_stops(self):
        t1 = Tuple.of(int_val(1), int_val(2))
        t2 = Tuple.of(int_val(1), int_val(2), int_val(3))
        pairs = list(deep_zip(t1, t2))
        # First pair is (t1, t2), then arity mismatch → no descent
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (t1, t2))

    def test_zip_nested_tuples(self):
        inner1 = Tuple.of(int_val(1), int_val(2))
        inner2 = Tuple.of(int_val(3), int_val(4))
        outer1 = Tuple.of(inner1, int_val(5))
        outer2 = Tuple.of(inner2, int_val(6))
        pairs = list(deep_zip(outer1, outer2))
        self.assertIn((int_val(1), int_val(3)), pairs)
        self.assertIn((int_val(2), int_val(4)), pairs)
        self.assertIn((int_val(5), int_val(6)), pairs)


if __name__ == "__main__":
    unittest.main()
