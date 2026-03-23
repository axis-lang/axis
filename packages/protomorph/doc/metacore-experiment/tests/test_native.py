"""Tests for native.py — meta_from_native, NativeType.Template, NativeHost."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Empty, Integer, Text, Tuple, Var, Placeholder, VaryingSchema
from protomorph.core.hosted import Float, Bool, Id, Spec, Qual, Hosted
from protomorph.core.native import (
    NativeHost,
    NativeProjectionError,
    NATIVE_HOST,
    meta_from_native,
)
from protomorph.core.variant import Union

from support import (
    int_val, str_val, float_val,
    Point, Color, Edge, Box, Marker,
)


# ── Spec name resolution ──────────────────────────────────────────────────────


class TestSpecName(unittest.TestCase):

    def test_explicit_spec_name_attribute(self):
        from protomorph.core.native import _spec_name
        self.assertEqual(_spec_name(Point), "test.core.Point")

    def test_fallback_to_module_qualname(self):
        from protomorph.core.native import _spec_name
        from protomorph.core.foundation import Builtin

        class Anonymous(Builtin):
            pass

        name = _spec_name(Anonymous)
        self.assertIn("Anonymous", name)
        self.assertIn(Anonymous.__module__, name)


# ── meta_from_native: scalars ─────────────────────────────────────────────────


class TestMetaFromNativeScalars(unittest.TestCase):

    def test_int_maps_to_integer(self):
        self.assertIs(meta_from_native(int), Integer)

    def test_str_maps_to_text(self):
        self.assertIs(meta_from_native(str), Text)

    def test_float_maps_to_float(self):
        self.assertIs(meta_from_native(float), Float)

    def test_bool_maps_to_bool(self):
        self.assertIs(meta_from_native(bool), Bool)

    def test_none_maps_to_omega(self):
        self.assertIs(meta_from_native(None), Empty)
        self.assertIs(meta_from_native(type(None)), Empty)

    def test_meta_passthrough(self):
        # If already a Meta, return it unchanged
        self.assertIs(meta_from_native(Integer), Integer)
        self.assertIs(meta_from_native(OMEGA), OMEGA)


# ── meta_from_native: unions ──────────────────────────────────────────────────


class TestMetaFromNativeUnions(unittest.TestCase):

    def test_union_two_types(self):
        m = meta_from_native(int | str)
        self.assertIsInstance(m, Union)
        self.assertEqual(m.variants, frozenset({Integer, Text}))

    def test_union_collapses_to_single_when_deduplicated(self):
        # int | int → just Integer
        m = meta_from_native(int | int)
        self.assertIs(m, Integer)

    def test_optional_int(self):
        # int | None -> Union(Integer, Empty)
        m = meta_from_native(int | None)
        self.assertIsInstance(m, Union)
        self.assertIn(Integer, m.variants)
        self.assertIn(Empty, m.variants)


# ── meta_from_native: containers → Qual ──────────────────────────────────────


class TestMetaFromNativeContainers(unittest.TestCase):

    def test_list_int_is_qual(self):
        m = meta_from_native(list[int])
        self.assertIsInstance(m, Qual)

    def test_list_int_underlying_is_integer(self):
        m = meta_from_native(list[int])
        self.assertIs(m.underlying, Integer)

    def test_list_qualifier_spec_is_list(self):
        m = meta_from_native(list[int])
        q = m.qualifiers[0]
        self.assertIsInstance(q, Spec)
        self.assertEqual(q.path, "std.qualifiers.List")

    def test_set_qualifier_spec_is_set(self):
        m = meta_from_native(set[str])
        q = m.qualifiers[0]
        self.assertEqual(q.path, "std.qualifiers.Set")

    def test_frozenset_qualifier_spec(self):
        m = meta_from_native(frozenset[int])
        q = m.qualifiers[0]
        self.assertEqual(q.path, "std.qualifiers.FrozenSet")

    def test_dict_qualifier_spec_is_dict(self):
        m = meta_from_native(dict[str, int])
        key = cast(Spec, m.qualifiers[0].args.get(Id.wrap("K")))
        q = m.qualifiers[0]
        self.assertIs(m.underlying, Integer)
        self.assertIs(key, Text)
        self.assertEqual(q.path, "std.qualifiers.Dict")

    def test_dict_qualifier_encodes_value_type_in_args(self):
        m = meta_from_native(dict[str, int])
        q = cast(Spec, m.qualifiers[0])
        self.assertEqual(q.args.arity, 1)
        self.assertIs(q.args.get(Id.wrap("K")), Text)

    def test_tuple_homogeneous_treated_as_list(self):
        m = meta_from_native(tuple[int, ...])
        q = m.qualifiers[0]
        self.assertEqual(q.path, "std.qualifiers.List")

    def test_tuple_heterogeneous_becomes_tuple_spec(self):
        m = meta_from_native(tuple[int, str])
        self.assertIsInstance(m, Spec)
        self.assertEqual(m.path, "std.core.Tuple")
        self.assertIs(m.args[0], Integer)
        self.assertIs(m.args[1], Text)

    def test_unknown_type_raises_projection_error(self):
        with self.assertRaises(NativeProjectionError):
            meta_from_native(object)

    def test_any_raises_projection_error(self):
        from typing import Any

        with self.assertRaises(NativeProjectionError):
            meta_from_native(Any)


# ── meta_from_native: Builtin types ──────────────────────────────────────────


class TestMetaFromNativeBuiltins(unittest.TestCase):

    def test_non_generic_builtin_produces_bare_spec(self):
        m = meta_from_native(Point)
        self.assertIsInstance(m, Spec)
        self.assertEqual(m.path, "test.core.Point")
        self.assertIs(m.args, Tuple.Empty)

    def test_generic_builtin_with_arg_produces_spec_with_args(self):
        m = meta_from_native(Box[int])
        self.assertIsInstance(m, Spec)
        self.assertEqual(m.path, "test.core.Box")
        self.assertEqual(m.args.arity, 1)

    def test_generic_builtin_arg_type_is_correct(self):
        m = meta_from_native(Box[int])
        self.assertIs(m.args[0], Integer)

    def test_generic_builtin_two_concrete_args(self):
        from protomorph.core.foundation import Builtin

        class Pair[A, B](Builtin):
            SPEC_NAME = "test.core.Pair"
            first: A
            second: B

        m = meta_from_native(Pair[int, str])
        self.assertEqual(m.path, "test.core.Pair")
        self.assertEqual(m.args.arity, 2)
        self.assertIs(m.args[0], Integer)
        self.assertIs(m.args[1], Text)


# ── NativeHost.type_by_spec_name ──────────────────────────────────────────────


class TestNativeHostRegistry(unittest.TestCase):

    def test_native_host_is_singleton_registry(self):
        self.assertIsInstance(NATIVE_HOST, NativeHost)

    def test_test_builtins_are_registered(self):
        registry = NATIVE_HOST.type_by_spec_name
        self.assertIn("test.core.Point", registry)
        self.assertIn("test.core.Edge", registry)
        self.assertIn("test.core.Box", registry)
        self.assertIn("test.core.Marker", registry)

    def test_template_carries_builtin_class(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Point"]
        self.assertIs(t.builtin_cls, Point)

    def test_template_fields_for_point(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Point"]
        self.assertIsInstance(t.fields, VaryingSchema)
        self.assertEqual(tuple(t.fields.names or ()), ("x", "y"))
        self.assertIs(t.fields.at(0), Integer)
        self.assertIs(t.fields.at(1), Integer)

    def test_template_fields_for_label(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Label"]
        self.assertEqual(tuple(t.fields.names or ()), ("text",))
        self.assertIs(t.fields.at(0), Text)

    def test_template_fields_for_edge(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Edge"]
        self.assertEqual(tuple(t.fields.names or ()), ("source", "target", "weight"))
        pt_spec = meta_from_native(Point)
        self.assertEqual(t.fields.at(0), pt_spec)
        self.assertIs(t.fields.at(2), Float)

    def test_marker_has_no_fields(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Marker"]
        self.assertEqual(t.fields.arity, 0)

    def test_box_template_has_one_param(self):
        t = NATIVE_HOST.type_by_spec_name["test.core.Box"]
        self.assertEqual(len(t.params), 1)
        self.assertIn("T", t.params)


# ── NativeHost.fields_for_spec ────────────────────────────────────────────────


class TestFieldsForSpec(unittest.TestCase):

    def test_fields_for_non_generic_spec(self):
        spec = meta_from_native(Point)
        fields = NATIVE_HOST.fields_for_spec(spec)
        self.assertIsInstance(fields, VaryingSchema)
        self.assertEqual(tuple(fields.names or ()), ("x", "y"))
        self.assertIs(fields.at(0), Integer)

    def test_fields_for_unknown_spec_returns_empty(self):
        from support import bare_spec
        unknown = bare_spec("test.core.Unknown")
        with self.assertRaises(NativeProjectionError):
            NATIVE_HOST.fields_for_spec(unknown)

    def test_fields_for_marker_returns_empty(self):
        spec = meta_from_native(Marker)
        fields = NATIVE_HOST.fields_for_spec(spec)
        self.assertEqual(fields.arity, 0)

    def test_fields_for_box_int_substitutes_T_with_integer(self):
        spec = meta_from_native(Box[int])
        fields = NATIVE_HOST.fields_for_spec(spec)
        self.assertEqual(tuple(fields.names or ()), ("value",))
        self.assertIs(fields.at(0), Integer)

    def test_fields_for_box_str_substitutes_T_with_text(self):
        spec = meta_from_native(Box[str])
        fields = NATIVE_HOST.fields_for_spec(spec)
        self.assertIs(fields.at(0), Text)


# ── NativeHost val_is_leaf / val_children / val_reconstruct ──────────────────


class TestNativeHostDecomposition(unittest.TestCase):

    def test_integer_val_is_leaf(self):
        self.assertTrue(NATIVE_HOST.val_is_leaf(Integer, 42))

    def test_text_val_is_leaf(self):
        self.assertTrue(NATIVE_HOST.val_is_leaf(Text, "hi"))

    def test_point_val_is_not_leaf(self):
        spec = meta_from_native(Point)
        self.assertFalse(NATIVE_HOST.val_is_leaf(spec, Point(x=1, y=2)))

    def test_marker_val_is_leaf(self):
        spec = meta_from_native(Marker)
        self.assertTrue(NATIVE_HOST.val_is_leaf(spec, Marker()))

    def test_point_children_are_x_and_y(self):
        spec = meta_from_native(Point)
        pt = Point(x=3, y=4)
        children = NATIVE_HOST.val_children(spec, pt)
        self.assertEqual(len(children), 2)
        self.assertIs(children[0], int_val(3))
        self.assertIs(children[1], int_val(4))

    def test_edge_children_include_nested_points(self):
        spec = meta_from_native(Edge)
        e = Edge(source=Point(x=0, y=0), target=Point(x=1, y=1), weight=1.5)
        children = NATIVE_HOST.val_children(spec, e)
        self.assertEqual(len(children), 3)
        # source and target are Hosted vals with Point spec
        pt_spec = meta_from_native(Point)
        self.assertIs(children[0].__meta__, pt_spec)
        self.assertIs(children[1].__meta__, pt_spec)
        self.assertIs(children[2], float_val(1.5))

    def test_val_reconstruct_produces_hosted(self):
        spec = meta_from_native(Point)
        children = (int_val(7), int_val(8))
        result = NATIVE_HOST.val_reconstruct(spec, children)
        self.assertIsInstance(result, Hosted)
        self.assertIsInstance(result.__data__, Point)
        self.assertEqual(result.__data__.x, 7)
        self.assertEqual(result.__data__.y, 8)

    def test_non_spec_meta_val_children_empty(self):
        self.assertEqual(NATIVE_HOST.val_children(OMEGA, None), ())

    def test_non_spec_meta_val_reconstruct_raises(self):
        with self.assertRaises(NotImplementedError):
            NATIVE_HOST.val_reconstruct(OMEGA, ())


# ── Full decomposition via Hosted.is_leaf / children ─────────────────────────


class TestHostedDecomposition(unittest.TestCase):
    """Verify the Hosted structural algebra delegates to NativeHost correctly."""

    def test_hosted_point_is_not_leaf(self):
        spec = meta_from_native(Point)
        hosted = spec.wrap(Point(x=1, y=2))
        self.assertFalse(hosted.is_leaf)

    def test_hosted_integer_is_leaf(self):
        self.assertTrue(int_val(5).is_leaf)

    def test_hosted_edge_children_are_two_points_and_weight(self):
        e_spec = meta_from_native(Edge)
        e = Edge(source=Point(x=0, y=0), target=Point(x=5, y=5), weight=2.0)
        hosted = e_spec.wrap(e)
        children = hosted.children()
        self.assertEqual(len(children), 3)

    def test_box_int_children_contain_integer_val(self):
        spec = meta_from_native(Box[int])
        hosted = spec.wrap(Box(value=42))
        children = hosted.children()
        self.assertEqual(len(children), 1)
        self.assertIs(children[0], int_val(42))


if __name__ == "__main__":
    unittest.main()
