from __future__ import annotations

import unittest
from typing import Any, cast
from pathlib import Path
import sys

import protomorph as morph
from protomorph import refs

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, DummyContext, DummyVarType, RuntimeArgsBox, Thing


class ApiHappyPathTests(unittest.TestCase):
    def test_anchor_path_route_returns_bootstrapped_anchor_value(self):
        value = morph.anchor("std.Text")

        self.assertIs(value.type, refs.ANCHOR_TYPE_INSTANCE)
        self.assertEqual(value.data, ("std", "Text"))
        self.assertEqual(value.path, "std.Text")

    def test_spec_ref_route_builds_specialized_ref_from_struct_const(self):
        spec_arg = cast(morph.Const | morph.Var, morph.val(morph.TEXT_TYPE))
        spec = morph.spec_ref("std.Map", morph.struct(K=spec_arg))

        self.assertEqual(spec.path, "std.Map")
        self.assertIsNotNone(spec.args)
        assert spec.args is not None
        self.assertEqual(repr(spec.args.get("K")), "std.Text")

    def test_struct_route_builds_struct_type_and_data_in_lockstep(self):
        value = morph.struct(morph.literal(1), name=morph.literal("x"))
        struct_type = cast(morph.StructType, value.type)

        self.assertEqual(repr(value), "(1, name='x')")
        self.assertEqual(struct_type.meta_attrs.index.keys, (None, "name"))
        self.assertEqual(value.data, (1, "x"))

    def test_literal_routes_cover_scalar_and_struct_literals(self):
        self.assertEqual(repr(morph.literal(42)), "42")
        self.assertEqual(repr(morph.literal("hello")), "'hello'")
        self.assertEqual(repr(morph.literal_struct(1, name="x")), "(1, name='x')")

    def test_union_routes_cover_flattening_and_active_variant_rendering(self):
        union_type = morph.union_type(morph.INTEGER_TYPE, morph.union_type(morph.TEXT_TYPE, morph.INTEGER_TYPE))
        value = morph.union(frozenset({morph.INTEGER_TYPE, morph.TEXT_TYPE}), morph.literal("x"))

        self.assertEqual(union_type.types, frozenset({morph.INTEGER_TYPE, morph.TEXT_TYPE}))
        self.assertEqual(repr(value), "'x'")

    def test_nominal_type_and_qualifier_routes_render_first_class_type_values(self):
        type_value = morph.val(morph.nominal_type("std.Integer"))
        qual_value = morph.val(morph.nominal_qual("test.Future", underlying=morph.TEXT_TYPE))

        self.assertEqual(repr(type_value), "std.Integer")
        self.assertEqual(repr(qual_value), "test.Future std.Text")

    def test_val_route_accepts_existing_values_types_literals_and_python_annotations(self):
        existing = morph.literal(7)

        self.assertIs(morph.val(existing), existing)
        self.assertEqual(repr(morph.val(morph.INTEGER_TYPE)), "std.Integer")
        self.assertEqual(repr(morph.val(True)), "true")
        self.assertEqual(repr(morph.val(list[int])), "std.List std.Integer")
        self.assertEqual(repr(morph.val(dict[str, str])), "std.Map[K=std.Text] std.Text")
        self.assertEqual(repr(morph.val(Any)), "std.Any")

    def test_val_route_accepts_struct_inputs_and_sequences(self):
        self.assertEqual(repr(morph.val({"x": 1, "y": "hi"})), "(x=1, y='hi')")
        self.assertEqual(repr(morph.val((1, "x"))), "(1, 'x')")
        self.assertEqual(repr(morph.val([1, "x"])), "(1, 'x')")

    def test_val_route_preserves_vars_in_specs_without_const_wrapper(self):
        ctx = DummyContext()
        type_var = morph.var(DummyVarType, ctx, "T")
        spec = cast(morph.Const, morph.val({"T": type_var}))
        type_ = morph.nominal_type("std.MyType", spec)

        self.assertEqual(repr(type_), "NominalType(std.MyType[T=$T])")
        self.assertEqual(repr(morph.val(type_)), "std.MyType[T=$T]")

    def test_type_of_native_type_dir_and_get_routes_stay_consistent(self):
        value = cast(morph.Const, morph.val({"x": 1, "y": "hi"}))
        fields = morph.dir(value)

        self.assertEqual(repr(morph.type_of(morph.val(42))), "std.Integer")
        self.assertEqual(morph.native_type(None), morph.EMPTY_TYPE)
        assert fields is not None
        self.assertEqual(tuple(fields.index.keys), ("x", "y"))
        self.assertEqual(morph.get(value, "x"), morph.val(1))
        self.assertEqual(morph.get(value, "y"), morph.val("hi"))

    def test_encode_decode_route_is_structural_for_plain_structs(self):
        value = cast(morph.Const, morph.val({"x": 1, "y": "hi"}))

        self.assertEqual(morph.decode(morph.encode(value)), value)

    def test_val_route_uses_builtin_type_builder_without_runtime_args(self):
        with morph.DEFAULT_NATIVE_BACKEND:
            value = morph.val(Thing(name="a", value=1))
            self.assertEqual(repr(value), "test.Thing(name='a', value=1)")

        self.assertEqual(repr(morph.val(Box._type(str))), "test.Box[T=std.Text]")

    def test_val_route_uses_builtin_runtime_args_when_orig_class_is_present(self):
        value = RuntimeArgsBox(value="x", runtime_orig_class_repr="str")

        with morph.DEFAULT_NATIVE_BACKEND:
            boxed = morph.val(value)

        self.assertEqual(repr(boxed), "test.RuntimeArgsBox[T=std.Text]")
