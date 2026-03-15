from __future__ import annotations

import unittest
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Thing


class StructMapFormatTests(unittest.TestCase):
    def test_map_routes_cover_keys_len_iter_get_has_and_apply(self):
        mapping = morph.Map.new((("x", 1), ("y", 2)))

        self.assertEqual(tuple(mapping.keys), ("x", "y"))
        self.assertEqual(len(mapping), 2)
        self.assertEqual(tuple(mapping), (1, 2))
        self.assertEqual(mapping.get("x"), 1)
        self.assertEqual(mapping.get("missing", default=9), 9)
        self.assertEqual(mapping.get("missing", fallback=lambda: 10), 10)
        self.assertTrue(mapping.has("y"))
        self.assertEqual(tuple(mapping.apply(lambda value: value + 1)), (2, 3))

    def test_struct_shape_and_index_routes_cover_flags_iteration_and_lookup(self):
        empty_shape = morph.Struct.Shape(arity=0, keys=frozenset())
        sparse_shape = morph.Struct.Shape(arity=3, keys=frozenset({"x"}))
        index = morph.Struct.Index((None, "x", "y"))

        self.assertTrue(empty_shape.is_empty)
        self.assertTrue(sparse_shape.is_sparse)
        self.assertEqual(repr(empty_shape), "Shape[0] _ = ()")
        self.assertEqual(repr(index), "Index[3] _ = (_, 'x', 'y')")
        self.assertEqual(index.arity, 3)
        self.assertTrue(index.is_sparse)
        self.assertEqual(index.get("x"), 1)
        self.assertTrue(index.has("y"))
        self.assertEqual(tuple(index), (None, "x", "y"))
        self.assertEqual(index[2], "y")

    def test_struct_routes_cover_construction_iteration_get_and_map(self):
        struct = morph.Struct.new(1, name="x")
        struct_from_iter = morph.Struct.from_iter(((None, 1), ("name", "x")))
        struct_from_keys = morph.Struct.from_keys((None, "name"), (1, "x"))

        self.assertEqual(struct.arity, 2)
        self.assertEqual(set(struct.shape), {"name"})
        self.assertEqual(tuple(struct), (1, "x"))
        self.assertEqual(len(struct), 2)
        self.assertEqual(repr(struct), "(1, name='x')")
        self.assertIn("x", struct)
        self.assertEqual(struct[0], 1)
        self.assertEqual(struct.get("name"), "x")
        self.assertEqual(struct.get("missing", default="fallback"), "fallback")
        self.assertEqual(struct.get("missing", fallback=lambda: "callable"), "callable")
        self.assertEqual(repr(struct.map(str)), "('1', name='x')")
        self.assertEqual(struct_from_iter, struct_from_keys)

    def test_format_routes_cover_specs_types_values_and_runtime_materialized_nominals(self):
        union_value = morph.union_value(int, str, active="x")
        struct_value = morph.struct_type(name=str, value=int).construct(name="a", value=1)

        with morph.DEFAULT_NATIVE_BACKEND:
            nominal_value = morph.val(Thing(name="a", value=1))

        self.assertEqual(repr(morph.anchor("std.Text")), "std.Text")
        self.assertEqual(repr(morph.spec(T=str)), "(T=std.Text)")
        self.assertEqual(repr(morph.TEXT_TYPE), "NominalType(std.Text)")
        self.assertEqual(repr(struct_value), "(name='a', value=1)")
        self.assertEqual(repr(union_value), "'x'")
        self.assertEqual(repr(nominal_value), "test.Thing(name='a', value=1)")


if __name__ == "__main__":
    unittest.main()
