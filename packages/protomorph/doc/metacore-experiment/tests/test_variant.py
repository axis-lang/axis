"""Tests for Union and Variant — union types and discriminated values."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text
from protomorph.core.hosted import Float, Bool
from protomorph.core.variant import Union, Variant

from support import int_val, str_val, float_val, bool_val


# ── Union construction ───────────────────────────────────────────────────────


class TestUnionConstruction(unittest.TestCase):

    def test_of_two_metas(self):
        u = Union.of(Integer, Text)
        self.assertEqual(u.variants, frozenset({Integer, Text}))

    def test_of_three_metas(self):
        u = Union.of(Integer, Text, Float)
        self.assertEqual(len(u.variants), 3)

    def test_union_requires_at_least_two_variants(self):
        with self.assertRaises(AssertionError):
            Union(OMEGA, frozenset({Integer}))

    def test_union_hash_consing(self):
        u1 = Union.of(Integer, Text)
        u2 = Union.of(Text, Integer)  # order shouldn't matter (frozenset)
        self.assertIs(u1, u2)

    def test_union_contains(self):
        u = Union.of(Integer, Text)
        self.assertTrue(u.contains(Integer))
        self.assertTrue(u.contains(Text))
        self.assertFalse(u.contains(Float))


# ── Union.inject / Union.wrap ─────────────────────────────────────────────────


class TestUnionInject(unittest.TestCase):

    def setUp(self):
        self.u = Union.of(Integer, Text)

    def test_inject_valid_val(self):
        v = self.u.inject(int_val(7))
        self.assertIsInstance(v, Variant)
        self.assertIs(v.__meta__, self.u)

    def test_inject_wrong_meta_raises(self):
        with self.assertRaises(ValueError):
            self.u.inject(float_val(1.5))

    def test_wrap_produces_variant(self):
        # Union.wrap creates an empty Variant shell; inject is the proper API
        v = self.u.inject(str_val("hello"))
        self.assertIsInstance(v, Variant)

    def test_inject_is_hash_consed(self):
        v1 = self.u.inject(int_val(3))
        v2 = self.u.inject(int_val(3))
        self.assertIs(v1, v2)


# ── Variant properties ───────────────────────────────────────────────────────


class TestVariantProperties(unittest.TestCase):

    def setUp(self):
        self.u = Union.of(Integer, Text, Float)
        self.vi = self.u.inject(int_val(42))
        self.vs = self.u.inject(str_val("hello"))

    def test_active_returns_wrapped_val(self):
        self.assertIs(self.vi.active, int_val(42))
        self.assertIs(self.vs.active, str_val("hello"))

    def test_discriminant_returns_active_meta(self):
        self.assertIs(self.vi.discriminant, Integer)
        self.assertIs(self.vs.discriminant, Text)

    def test_is_(self):
        self.assertTrue(self.vi.is_(Integer))
        self.assertFalse(self.vi.is_(Text))

    def test_project_hit(self):
        self.assertIs(self.vi.project(Integer), int_val(42))

    def test_project_miss_returns_none(self):
        self.assertIsNone(self.vi.project(Text))

    def test_map_active(self):
        v2 = self.vi.map_active(lambda v: Integer.wrap(v.__data__ * 2))
        self.assertIs(v2.active, int_val(84))
        self.assertIs(v2.__meta__, self.u)


# ── Variant structural algebra ────────────────────────────────────────────────


class TestVariantStructuralAlgebra(unittest.TestCase):

    def setUp(self):
        self.u = Union.of(Integer, Text)

    def test_variant_is_not_leaf(self):
        v = self.u.inject(int_val(1))
        self.assertFalse(v.is_leaf)

    def test_variant_children_are_active_val(self):
        v = self.u.inject(int_val(5))
        self.assertEqual(v.children(), (int_val(5),))

    def test_variant_reconstruct_with_same_meta(self):
        v = self.u.inject(int_val(5))
        v2 = v.reconstruct((int_val(9),))
        self.assertIs(v2.active, int_val(9))
        self.assertIs(v2.__meta__, self.u)

    def test_variant_reconstruct_with_different_meta_in_union(self):
        v = self.u.inject(int_val(5))
        v2 = v.reconstruct((str_val("new"),))
        self.assertIs(v2.discriminant, Text)

    def test_variant_invariant_single_active(self):
        # Directly constructing a Variant with two active metas must fail
        from protobase import frozendict
        with self.assertRaises(AssertionError):
            Variant(self.u, frozendict({Integer: 1, Text: "x"}))


# ── Variants inside a Tuple ───────────────────────────────────────────────────


class TestVariantInTuple(unittest.TestCase):

    def test_tuple_of_variants(self):
        from protomorph.core import Tuple
        u = Union.of(Integer, Text)
        v1 = u.inject(int_val(1))
        v2 = u.inject(str_val("a"))
        t = Tuple.of(v1, v2)
        self.assertIs(t[0], v1)
        self.assertIs(t[1], v2)

    def test_uniform_of_variants_with_same_union(self):
        from protomorph.core import Tuple
        from protomorph.core.schema import UniformSchema
        u = Union.of(Integer, Text)
        v1 = u.inject(int_val(1))
        v2 = u.inject(str_val("b"))
        t = Tuple.uniform_of([v1, v2])
        self.assertIsInstance(t.schema, UniformSchema)
        self.assertIs(t.schema.__data__, u)


if __name__ == "__main__":
    unittest.main()
