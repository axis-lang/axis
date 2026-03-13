import unittest
from typing import cast

import protomorph as morph
from protomorph import refs


class Thing(morph.Builtin):
    ANCHOR = "test.Thing"

    name: str
    value: int


class TestProtoMorphCore(unittest.TestCase):
    def test_literal_values_render_as_expected(self):
        self.assertEqual(repr(morph.val(42)), "42")
        self.assertEqual(repr(morph.val("hello")), "'hello'")
        self.assertEqual(repr(morph.val(True)), "true")
        self.assertEqual(repr(morph.val(None)), "none")

    def test_type_values_are_first_class(self):
        self.assertEqual(repr(morph.val(morph.INTEGER_TYPE)), "std.Integer")
        self.assertEqual(morph.val(morph.INTEGER_TYPE).wrap(42), morph.val(42))

    def test_anchor_uses_bootstrapped_anchor_type_instance(self):
        value = morph.anchor("std.Text")

        self.assertIs(value.type, refs.ANCHOR_TYPE_INSTANCE)
        self.assertEqual(value.data, ("std", "Text"))

    def test_structs_are_navigable(self):
        value = morph.val({"x": 1, "y": "hi"})

        self.assertEqual(repr(value), "(x=1, y='hi')")
        self.assertEqual(tuple(value.dir()), ("x", "y"))
        self.assertEqual(morph.get(value, "x"), morph.val(1))
        self.assertEqual(morph.get(value, "y"), morph.val("hi"))

    def test_type_of_returns_type_value(self):
        self.assertEqual(repr(morph.type_of(morph.val(42))), "std.Integer")

    def test_nominal_qualifier_lifts_dir_through_bridge(self):
        inner = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE, value=morph.INTEGER_TYPE))
        qualified = morph.nominal_qual("test.Future", underlying=inner)

        fields = qualified._dir()

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields.index.keys, ("name", "value"))
        self.assertEqual(repr(morph.val(fields.get("name"))), "test.Future std.Text")
        self.assertEqual(repr(morph.val(fields.get("value"))), "test.Future std.Integer")

    def test_encode_decode_are_structural_extensions(self):
        value = cast(morph.Const, morph.val({"x": 1, "y": "hi"}))
        self.assertEqual(morph.decode(morph.encode(value)), value)

    def test_bridge_combine_is_extension_point(self):
        with self.assertRaises(NotImplementedError):
            morph.DEFAULT_BRIDGE.combine(morph.INTEGER_TYPE, morph.INTEGER_TYPE, op="+")

    def test_bridge_base_installs_context_var(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        before = morph.BRIDGE.get()
        with bridge:
            self.assertIs(morph.BRIDGE.get(), bridge)
        self.assertIs(morph.BRIDGE.get(), before)

    def test_bridge_base_project_uses_structural_helpers(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        inner = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE))
        qualified = morph.nominal_qual("test.Future", underlying=inner)

        self.assertEqual(bridge.project(inner, "name"), morph.TEXT_TYPE)
        self.assertEqual(
            repr(morph.val(bridge.project(qualified, "name"))),
            "test.Future std.Text",
        )


if __name__ == "__main__":
    unittest.main()
