from __future__ import annotations

import unittest
from protobase import Missing
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType, Thing


class BaseAndFormatTests(unittest.TestCase):
    def test_val_wrap_route_uses_meta_type_values_to_construct_plain_consts(self):
        type_value = morph.val(morph.INTEGER_TYPE)

        self.assertEqual(type_value.wrap(42), morph.val(42))

    def test_val_wrap_route_rejects_non_meta_type_values(self):
        with self.assertRaises(TypeError):
            morph.val(42).wrap(100)

    def test_val_attrs_len_dir_and_get_route_materializes_struct_views(self):
        value = morph.val({"x": 1, "y": "hi"})
        attrs = value.attrs

        self.assertIsNotNone(attrs)
        assert attrs is not None
        self.assertEqual(repr(attrs), "(x=1, y='hi')")
        self.assertTrue(value.has_attrs)
        self.assertEqual(len(value), 2)
        self.assertEqual(tuple(value.dir()), ("x", "y"))
        self.assertEqual(value["x"], morph.val(1))
        self.assertEqual(value.get("missing", default=morph.val(0)), morph.val(0))
        with self.assertRaises(KeyError):
            value.get("missing", default=Missing)

    def test_builtin_anchor_path_route_prefers_anchor_constant_then_module_name(self):
        class LocalBuiltin(morph.Builtin):
            value: int

        self.assertEqual(Thing._anchor_path(), "test.Thing")
        self.assertIn("LocalBuiltin", LocalBuiltin._anchor_path())

    def test_format_route_covers_err_var_anchor_nominal_and_union_values(self):
        err = morph.Err(morph.ErrType(), "boom")
        anchor = morph.anchor("std.Text")
        var = morph.var(DummyVarType, DummyContext(), "T")
        union = morph.union(frozenset({morph.INTEGER_TYPE, morph.TEXT_TYPE}), morph.literal(7))

        self.assertEqual(repr(err), "Err('boom')")
        self.assertEqual(repr(anchor), "std.Text")
        self.assertEqual(repr(var), "$T")
        self.assertEqual(repr(union), "7")

    def test_format_route_covers_nominal_values_with_materialized_attrs(self):
        with morph.DEFAULT_NATIVE_BACKEND:
            value = morph.val(Thing(name="a", value=1))
            self.assertEqual(repr(value), "test.Thing(name='a', value=1)")
