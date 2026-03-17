from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import cast

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, DummyContext, DummyVarType, RuntimeArgsBox, Thing


class CoreApiTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

    def test_val_route_covers_literals_types_python_annotations_and_specs(self):
        ctx = DummyContext()
        type_var = morph.var(DummyVarType, ctx, "T")
        specialized = morph.nominal_type("std.MyType", morph.spec(T=type_var))

        self.assertEqual(repr(morph.val(42)), "42")
        self.assertEqual(repr(morph.val(morph.INTEGER_TYPE)), "std.core.Integer")
        self.assertEqual(repr(morph.val(list[int])), "std.qualifiers.List std.core.Integer")
        self.assertEqual(repr(morph.val(specialized)), "std.MyType[T=$T]")

    def test_struct_and_struct_type_routes_cover_value_and_schema_construction(self):
        value = morph.struct(morph.literal(1), name=morph.literal("x"))
        alias_value = morph.struct_value(morph.literal(2), name=morph.literal("y"))
        pair = morph.struct_type(int, int).construct(1, 2)
        named = morph.struct_type(name=str, value=int).construct(name="a", value=1)

        self.assertEqual(repr(value), "(1, name='x')")
        self.assertEqual(repr(alias_value), "(2, name='y')")
        self.assertEqual(repr(pair), "(1, 2)")
        self.assertEqual(pair.encode(), (1, 2))
        self.assertEqual(repr(named), "(name='a', value=1)")

        named_metaspec = morph.struct_type(name=str, value=int)._metaspec()
        self.assertIsNotNone(named_metaspec)
        assert named_metaspec is not None
        self.assertEqual(repr(named_metaspec), "(name=std.types.NominalType, value=std.types.NominalType)")
        self.assertEqual(
            tuple(cast(morph.StructType, named_metaspec.__type__).meta_attrs.index.keys),
            ("name", "value"),
        )

    def test_spec_and_union_value_routes_cover_new_public_api_aliases(self):
        boxed = morph.nominal_type("test.Box", morph.spec(T=str))
        value = morph.union_value(int, str, active="x")
        fact = morph.Fact(boxed.spec_ref.__type__, boxed.spec_ref.__data__)

        self.assertEqual(repr(morph.val(boxed)), "test.Box[T=std.core.Text]")
        self.assertEqual(repr(value), "'x'")
        self.assertEqual(fact, boxed.spec_ref)

    def test_as_type_and_struct_shape_routes_cover_symbolic_term_views(self):
        spec = morph.spec_ref("test.Box", morph.spec(T=str))
        type_value = morph.val(morph.INTEGER_TYPE)
        spec_args = spec.args
        assert spec_args is not None

        self.assertIs(type_value.data, morph.INTEGER_TYPE)
        self.assertEqual(type_value.as_type(), morph.INTEGER_TYPE)
        self.assertEqual(morph.anchor("std.core.Text").as_type(), morph.TEXT_TYPE)
        self.assertEqual(spec.as_type(), morph.nominal_type("test.Box", morph.spec(T=str)))
        self.assertIsNone(morph.literal(1).as_type())
        self.assertEqual(spec.struct_shape, spec_args.shape)
        self.assertEqual(morph.struct_type(name=str, value=int).struct_shape, morph.Struct.new(name=morph.TEXT_TYPE, value=morph.INTEGER_TYPE).shape)

    def test_subst_route_substitutes_symbolic_values_through_specs(self):
        ctx = DummyContext()
        type_var = morph.var(DummyVarType, ctx, "T")
        spec = morph.spec_ref("test.Box", morph.spec(T=type_var))

        resolved = spec.subst(lambda var: morph.val(morph.TEXT_TYPE) if var == type_var else None)

        self.assertEqual(resolved, morph.spec_ref("test.Box", morph.spec(T=str)))
        self.assertEqual(resolved.as_type(), morph.nominal_type("test.Box", morph.spec(T=str)))

    def test_type_route_covers_type_projection_and_nominal_qualify(self):
        self.assertEqual(morph.type_(int), morph.INTEGER_TYPE)
        self.assertEqual(repr(morph.nominal_type("std.qualifiers.List").qualify(int)), "NominalQualifier(NominalType(std.core.Integer), std.qualifiers.List)")

    def test_nominal_decode_and_construct_routes_materialize_with_native_layout(self):
        with morph.NATIVE_BACKEND:
            type_ = cast(morph.NominalType, Thing._type())
            decoded = type_.decode(("x", 1))
            constructed = type_.construct(name="x", value=1)
            self.assertEqual(constructed.encode(), ("x", 1))

        self.assertIsInstance(decoded.data, Thing)
        self.assertEqual(cast(Thing, decoded.data).name, "x")
        self.assertIsInstance(constructed.data, Thing)

    def test_construct_route_normalizes_nested_structures_recursively(self):
        nested_type = morph.struct_type(
            a=morph.struct_type(int, int),
            b=morph.struct_type(left=int, right=int),
        )

        value = nested_type.construct(a=[1, 2], b={"left": 3, "right": 4})

        self.assertEqual(value.encode(), ((1, 2), (3, 4)))
        self.assertEqual(repr(value), "(a=(1, 2), b=(left=3, right=4))")

    def test_encode_and_type_decode_routes_round_trip_structural_values(self):
        value = morph.struct_type(name=str, value=int).construct(name="x", value=1)

        self.assertEqual(value.type.decode(value.encode()), value)
        self.assertEqual(value.encode(), ("x", 1))

    def test_runtime_generic_builtin_values_use_native_type_builder(self):
        with morph.NATIVE_BACKEND:
            value = morph.val(RuntimeArgsBox(value="x", runtime_orig_class_repr="str"))

        rendered = repr(value)
        self.assertIn("test.RuntimeArgsBox[T=std.core.Text](value='x'", rendered)
        self.assertIn("runtime_orig_class_repr=Const(type=", rendered)
        self.assertIn("data='str'))", rendered)
        self.assertEqual(repr(morph.val(Box._type(str))), "test.Box[T=std.core.Text]")

    def test_layout_and_projection_routes_expose_structural_information(self):
        with morph.NATIVE_BACKEND:
            type_ = cast(morph.NominalType, Thing._type())
            layout = type_.layout()
            projected = type_._get(Thing(name="x", value=1), "name")

        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), ("name", "value"))
        self.assertEqual(repr(projected), "'x'")


if __name__ == "__main__":
    unittest.main()
