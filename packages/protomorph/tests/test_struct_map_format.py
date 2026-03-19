from __future__ import annotations

import unittest
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Thing


class StructMapFormatTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

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
        self.assertEqual(index.named_count, 2)
        self.assertEqual(index.positional_count, 1)
        self.assertEqual(index.named_keys, ("x", "y"))
        self.assertEqual(index.named_offsets, (1, 2))
        self.assertTrue(index.is_sparse)
        self.assertTrue(index.is_mixed)
        self.assertFalse(index.is_named_only)
        self.assertFalse(index.is_positional_only)
        self.assertEqual(index.get("x"), 1)
        self.assertEqual(index.offset_of("x"), 1)
        self.assertTrue(index.has("y"))
        self.assertTrue(index.contains_key("y"))
        self.assertEqual(tuple(index), (None, "x", "y"))
        self.assertEqual(index[2], "y")
        self.assertEqual(tuple(index[:2]), (None, "x"))
        self.assertEqual(tuple(index.prefix(1)), (None,))
        self.assertEqual(tuple(index.middle(1, 3)), ("x", "y"))
        self.assertEqual(tuple(index.suffix(2)), ("x", "y"))
        self.assertEqual(index.split_at(1), (morph.Struct.Index((None,)), morph.Struct.Index(("x", "y"))))
        self.assertEqual(
            index.split_variadic(1, 1),
            (
                morph.Struct.Index((None,)),
                morph.Struct.Index(("x",)),
                morph.Struct.Index(("y",)),
            ),
        )
        self.assertEqual(index.take_offsets((0, 2)), morph.Struct.Index((None, "y")))
        self.assertEqual(index.drop_offsets((1,)), morph.Struct.Index((None, "y")))
        self.assertTrue(morph.Struct.Shape.from_index(index).matches(index))

    def test_struct_routes_cover_construction_iteration_get_and_map(self):
        struct = morph.Struct.new(1, name="x")
        struct_from_iter = morph.Struct.from_iter(((None, 1), ("name", "x")))
        struct_from_keys = morph.Struct.from_keys((None, "name"), (1, "x"))

        self.assertEqual(struct.arity, 2)
        self.assertEqual(set(struct.shape), {"name"})
        self.assertEqual(tuple(struct), (1, "x"))
        self.assertEqual(len(struct), 2)
        self.assertEqual(repr(struct), "(1, name='x')")
        self.assertEqual(struct.keys, (None, "name"))
        self.assertEqual(struct.named_keys, ("name",))
        self.assertEqual(struct.positional_count, 1)
        self.assertEqual(struct.named_count, 1)
        self.assertTrue(struct.is_mixed)
        self.assertIn("x", struct)
        self.assertEqual(struct[0], 1)
        self.assertEqual(struct.get("name"), "x")
        self.assertEqual(struct.get("missing", default="fallback"), "fallback")
        self.assertEqual(struct.get("missing", fallback=lambda: "callable"), "callable")
        self.assertEqual(repr(struct.map(str)), "('1', name='x')")
        self.assertEqual(struct_from_iter, struct_from_keys)
        self.assertEqual(struct.entries, ((None, 1), ("name", "x")))
        self.assertEqual(struct.positional_values, (1,))
        self.assertEqual(struct.named_items(), (("name", "x"),))
        self.assertEqual(struct.named_dict(), {"name": "x"})
        self.assertEqual(struct[:1], morph.Struct.from_keys((None,), (1,)))
        self.assertEqual(struct.prefix(1), morph.Struct.from_keys((None,), (1,)))
        self.assertEqual(struct.middle(1), morph.Struct.from_keys(("name",), ("x",)))
        self.assertEqual(struct.suffix(1), morph.Struct.from_keys(("name",), ("x",)))
        self.assertEqual(
            struct.split_at(1),
            (
                morph.Struct.from_keys((None,), (1,)),
                morph.Struct.from_keys(("name",), ("x",)),
            ),
        )
        self.assertEqual(
            struct.split_variadic(1, 1),
            (
                morph.Struct.from_keys((None,), (1,)),
                morph.Struct.from_keys((), ()),
                morph.Struct.from_keys(("name",), ("x",)),
            ),
        )
        self.assertEqual(struct.take_offsets((1,)), morph.Struct.from_keys(("name",), ("x",)))
        self.assertEqual(struct.drop_offsets((0,)), morph.Struct.from_keys(("name",), ("x",)))
        self.assertEqual(struct.filter_entries(lambda key, _: key is not None), morph.Struct.from_keys(("name",), ("x",)))
        self.assertEqual(struct.with_index(morph.Struct.Index(("value", "name"))), morph.Struct.from_keys(("value", "name"), (1, "x")))

    def test_struct_const_conversion_helpers_roundtrip(self):
        struct = morph.Struct.new(morph.literal(1), name=morph.literal("x"))
        const = struct.as_const()

        self.assertEqual(morph.Struct.from_const(const), struct)

    def test_struct_from_iter_consumes_generators_safely(self):
        struct = morph.Struct.from_iter((entry for entry in ((None, 1), ("name", "x"))))

        self.assertEqual(struct, morph.Struct.from_keys((None, "name"), (1, "x")))

    def test_format_routes_cover_specs_types_values_and_runtime_materialized_nominals(self):
        union_value = morph.union_value(int, str, active="x")
        struct_value = morph.struct_type(name=str, value=int).construct(name="a", value=1)

        with morph.NATIVE_BACKEND:
            nominal_value = morph.val(Thing(name="a", value=1))

        self.assertEqual(repr(morph.anchor("std.core.Text")), "std.core.Text")
        self.assertEqual(repr(morph.spec()), "()")
        self.assertEqual(repr(morph.spec(T=str)), "(T=std.core.Text)")
        self.assertEqual(repr(morph.TEXT_TYPE), "NominalType(std.core.Text)")
        self.assertEqual(repr(struct_value), "(name='a', value=1)")
        self.assertEqual(repr(union_value), "'x'")
        self.assertEqual(repr(nominal_value), "test.Thing(name='a', value=1)")


if __name__ == "__main__":
    unittest.main()
