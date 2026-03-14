from __future__ import annotations

import unittest

import protomorph as morph


class StructAndMapTests(unittest.TestCase):
    def test_map_route_covers_new_len_iter_get_has_and_apply(self):
        mapping = morph.Map.new((("x", 1), ("y", 2)))

        self.assertEqual(len(mapping), 2)
        self.assertEqual(tuple(mapping), (1, 2))
        self.assertEqual(mapping.get("x"), 1)
        self.assertEqual(mapping.get("missing", default=9), 9)
        self.assertEqual(mapping.get("missing", fallback=lambda: 10), 10)
        self.assertTrue(mapping.has("x"))
        self.assertEqual(mapping.apply(lambda value: value + 1).get("y"), 3)

    def test_map_exception_route_propagates_missing_keys_without_fallback(self):
        mapping = morph.Map.new((("x", 1),))

        with self.assertRaises(KeyError):
            mapping.get("missing")

    def test_struct_shape_and_index_routes_cover_empty_full_sparse_and_lookup(self):
        empty_shape = morph.Struct.Shape(arity=0, keys=frozenset())
        full_index = morph.Struct.Index(("x", "y"))
        sparse_index = morph.Struct.Index((None, "y"))

        self.assertTrue(empty_shape.is_empty)
        self.assertTrue(full_index.is_full)
        self.assertTrue(sparse_index.is_sparse)
        self.assertEqual(full_index.get("x"), 0)
        self.assertEqual(set(full_index.shape), {"x", "y"})

    def test_struct_route_covers_construction_iteration_repr_get_and_map(self):
        struct = morph.Struct.new(1, name="x")

        self.assertEqual(repr(struct), "(1, name='x')")
        self.assertEqual(tuple(struct), (1, "x"))
        self.assertEqual(len(struct), 2)
        self.assertEqual(struct.get("name"), "x")
        self.assertEqual(struct.get("missing", default="fallback"), "fallback")
        self.assertEqual(struct.get("missing", fallback=lambda: "callable"), "callable")
        self.assertEqual(repr(struct.map(repr)), "('1', name=\"'x'\")")

    def test_struct_route_covers_from_iter_from_keys_contains_and_indexing(self):
        struct_from_iter = morph.Struct.from_iter(((None, 1), ("name", "x")))
        struct_from_keys = morph.Struct.from_keys(("x", "y"), (1, 2))

        self.assertIn("x", struct_from_iter)
        self.assertEqual(struct_from_iter[0], 1)
        self.assertEqual(struct_from_keys.get("y"), 2)

    def test_struct_exception_routes_reject_missing_keys_and_expose_duplicate_index_collapse(self):
        struct = morph.Struct.new(name="x")
        duplicate_index = morph.Struct.Index(("x", "x"))

        with self.assertRaises(KeyError):
            struct.get("missing")
        self.assertEqual(duplicate_index.get("x"), 1)
