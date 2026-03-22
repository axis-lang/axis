"""Tests for Tuple — construction, access, mutation, schema transitions."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Spec, Tuple
from protomorph.core.hosted import Id, Float
from protomorph.core.schema import UniformSchema, VaryingSchema
from protomorph.core.index import Index, IndexKeyMeta, INDEX_GROUND
from protomorph.core.variant import Union

from support import int_val, str_val, float_val


# ── Helpers ──────────────────────────────────────────────────────────────────


def str_key(s: str):
    """Construct a key Val suitable for use with Id-indexed Tuples."""
    return Id.wrap(s)


def keyed_index(*names: str) -> Index:
    key_meta = IndexKeyMeta(INDEX_GROUND, Id)
    return Index(key_meta, tuple(names))


# ── Empty tuple ──────────────────────────────────────────────────────────────


class TestTupleEmpty(unittest.TestCase):

    def test_empty_has_arity_zero(self):
        self.assertEqual(Tuple.Empty.arity, 0)

    def test_empty_is_singleton(self):
        self.assertIs(Tuple.Empty, Tuple.empty())

    def test_empty_has_no_children(self):
        self.assertEqual(Tuple.Empty.children(), ())


# ── Positional construction ──────────────────────────────────────────────────


class TestTuplePositional(unittest.TestCase):

    def test_of_positional_arity(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3))
        self.assertEqual(t.arity, 3)

    def test_of_positional_at(self):
        t = Tuple.of(int_val(10), str_val("x"))
        self.assertIs(t[0], int_val(10))
        self.assertIs(t[1], str_val("x"))

    def test_of_positional_uses_varying_schema_for_mixed_metas(self):
        t = Tuple.of(int_val(1), str_val("a"))
        self.assertIsInstance(t.schema, VaryingSchema)

    def test_of_positional_uses_varying_schema_even_for_uniform_metas(self):
        # Tuple.of always uses varying_of under the hood
        t = Tuple.of(int_val(1), int_val(2))
        self.assertIsInstance(t.schema, VaryingSchema)

    def test_of_positional_iteration(self):
        vals = [int_val(1), int_val(2), int_val(3)]
        t = Tuple.of(*vals)
        self.assertEqual(list(t), vals)

    def test_of_positional_children(self):
        t = Tuple.of(int_val(7), str_val("z"))
        self.assertEqual(t.children(), (int_val(7), str_val("z")))


# ── Keyed (keyword) construction ─────────────────────────────────────────────


class TestTupleKeyed(unittest.TestCase):

    def test_of_keyword_arity(self):
        t = Tuple.of(x=int_val(1), y=int_val(2))
        self.assertEqual(t.arity, 2)

    def test_of_keyword_index_keys(self):
        t = Tuple.of(name=str_val("alice"), age=int_val(30))
        self.assertEqual(t.index.keys, ("name", "age"))

    def test_of_keyword_get(self):
        t = Tuple.of(x=int_val(10), y=int_val(20))
        self.assertIs(t.get(str_key("x")), int_val(10))
        self.assertIs(t.get(str_key("y")), int_val(20))

    def test_of_keyword_items(self):
        t = Tuple.of(a=int_val(1), b=int_val(2))
        items = dict(t.items())
        self.assertEqual(items[str_key("a")], int_val(1))
        self.assertEqual(items[str_key("b")], int_val(2))

    def test_of_keyword_to_dict(self):
        t = Tuple.of(x=int_val(5), y=int_val(6))
        d = t.to_dict()
        self.assertEqual(d[str_key("x")], int_val(5))

    def test_get_wrong_key_raises(self):
        t = Tuple.of(x=int_val(1))
        with self.assertRaises(KeyError):
            t.get(str_key("z"))

    def test_get_on_indexless_tuple_raises(self):
        t = Tuple.of(int_val(1), int_val(2))
        with self.assertRaises(KeyError):
            t.get(str_key("x"))


# ── uniform_of / varying_of ──────────────────────────────────────────────────


class TestTupleFactories(unittest.TestCase):

    def test_uniform_of_single_meta(self):
        t = Tuple.uniform_of([int_val(1), int_val(2), int_val(3)])
        self.assertIsInstance(t.schema, UniformSchema)
        self.assertIs(t.schema.__data__, Integer)

    def test_uniform_of_mixed_metas_wraps_in_union(self):
        t = Tuple.uniform_of([int_val(1), str_val("a")])
        self.assertIsInstance(t.schema, UniformSchema)
        self.assertIsInstance(t.schema.__data__, Union)

    def test_varying_of(self):
        t = Tuple.varying_of([int_val(1), str_val("b")])
        self.assertIsInstance(t.schema, VaryingSchema)
        self.assertIs(t[0], int_val(1))
        self.assertIs(t[1], str_val("b"))


# ── replace / replace_key ────────────────────────────────────────────────────


class TestTupleReplace(unittest.TestCase):

    def test_replace_at_offset_same_meta(self):
        t = Tuple.uniform_of([int_val(1), int_val(2)])
        t2 = t.replace(0, int_val(99))
        self.assertIs(t2[0], int_val(99))
        self.assertIs(t2[1], int_val(2))
        # Schema stays UniformSchema when meta doesn't change
        self.assertIsInstance(t2.schema, UniformSchema)

    def test_replace_at_offset_different_meta_converts_to_varying(self):
        t = Tuple.uniform_of([int_val(1), int_val(2)])
        t2 = t.replace(0, str_val("x"))
        self.assertIsInstance(t2.schema, VaryingSchema)
        self.assertIs(t2[0], str_val("x"))

    def test_replace_preserves_other_positions(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3))
        t2 = t.replace(1, int_val(42))
        self.assertIs(t2[0], int_val(1))
        self.assertIs(t2[1], int_val(42))
        self.assertIs(t2[2], int_val(3))

    def test_replace_key(self):
        t = Tuple.of(x=int_val(1), y=int_val(2))
        t2 = t.replace_key(str_key("x"), int_val(100))
        self.assertIs(t2.get(str_key("x")), int_val(100))
        self.assertIs(t2.get(str_key("y")), int_val(2))


# ── slice ────────────────────────────────────────────────────────────────────


class TestTupleSlice(unittest.TestCase):

    def test_slice_positional(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3))
        s = t.slice(1)
        self.assertEqual(s.arity, 2)
        self.assertIs(s[0], int_val(2))
        self.assertIs(s[1], int_val(3))

    def test_slice_with_stop(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3))
        s = t.slice(0, 2)
        self.assertEqual(s.arity, 2)
        self.assertIs(s[0], int_val(1))

    def test_slice_keyed_tuple_preserves_remaining_keys(self):
        t = Tuple.of(a=int_val(1), b=int_val(2), c=int_val(3))
        s = t.slice(1)
        self.assertEqual(s.index.keys, ("b", "c"))


# ── map ──────────────────────────────────────────────────────────────────────


class TestTupleMap(unittest.TestCase):

    def test_map_transforms_each_element(self):
        t = Tuple.of(int_val(1), int_val(2))
        t2 = t.map(lambda v: Integer.wrap(v.__data__ * 10))
        self.assertIs(t2[0], int_val(10))
        self.assertIs(t2[1], int_val(20))

    def test_map_changing_meta_produces_uniform_schema_of_new_type(self):
        # All elements change to the same meta (Text) → UniformSchema, not Varying.
        t = Tuple.uniform_of([int_val(1), int_val(2)])
        t2 = t.map(lambda v: str_val(str(v.__data__)))
        self.assertIsInstance(t2.schema, UniformSchema)
        self.assertIs(t2.schema.__data__, Text)


# ── reconstruct ──────────────────────────────────────────────────────────────


class TestTupleReconstruct(unittest.TestCase):

    def test_reconstruct_same_metas_gives_uniform_schema(self):
        t = Tuple.of(int_val(1), int_val(2))
        t2 = t.reconstruct((int_val(3), int_val(4)))
        self.assertIsInstance(t2.schema, UniformSchema)

    def test_reconstruct_mixed_metas_gives_varying_schema(self):
        t = Tuple.of(int_val(1), int_val(2))
        t2 = t.reconstruct((int_val(3), str_val("x")))
        self.assertIsInstance(t2.schema, VaryingSchema)


# ── nested tuples ────────────────────────────────────────────────────────────


class TestNestedTuples(unittest.TestCase):

    def test_tuple_of_tuples(self):
        inner_a = Tuple.of(int_val(1), int_val(2))
        inner_b = Tuple.of(str_val("x"), str_val("y"))
        outer = Tuple.of(inner_a, inner_b)
        self.assertEqual(outer.arity, 2)
        self.assertIs(outer[0], inner_a)
        self.assertIs(outer[1], inner_b)

    def test_deeply_nested_at_access(self):
        leaf = int_val(99)
        t1 = Tuple.of(leaf, int_val(0))
        t2 = Tuple.of(t1, int_val(0))
        t3 = Tuple.of(t2, int_val(0))
        self.assertIs(t3[0][0][0], leaf)

    def test_from_dict_round_trip(self):
        idx = keyed_index("x", "y")
        d = {str_key("x"): int_val(10), str_key("y"): int_val(20)}
        t = Tuple.from_dict(idx, d)
        self.assertEqual(t.to_dict(), d)


if __name__ == "__main__":
    unittest.main()
