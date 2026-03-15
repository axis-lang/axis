from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import TypeVar, cast

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, DummyContext, FancyBox, PairBox, RuntimeArgsBox, Thing


class NativeSpecializationTests(unittest.TestCase):
    def test_type_from_python_routes_cover_typevars_and_unregistered_types(self):
        T = TypeVar("T")
        vars: set[morph.Var] = set()

        projected = morph.type_from_python(T, ctx=DummyContext(), vars=vars)

        self.assertIsInstance(projected, morph.Var)
        self.assertEqual({var.data for var in vars}, {"T"})
        self.assertEqual(morph.type_from_python(object), morph.ANY_TYPE)

    def test_native_registry_layout_currently_leaves_nested_builtin_typevars_unspecialized(self):
        registry = morph.NativeRegistry()
        registry.register_native_type(str, morph.TEXT_TYPE)
        registry.register_native_type(int, morph.INTEGER_TYPE)
        registry.register_builtin(FancyBox)

        layout = registry.layout(cast(morph.NominalType, FancyBox._type(str)))

        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(repr(morph.val(layout.fields.get("pair"))), "test.PairBox[K=$T, V=std.Integer]")
        self.assertEqual(repr(morph.val(layout.fields.get("box"))), "test.Box[T=$T]")

    def test_build_builtin_type_routes_cover_defaults_and_invalid_parameter_shapes(self):
        self.assertEqual(repr(morph.val(Box._type())), "test.Box")

        class WeirdBuiltin(morph.Builtin):
            ANCHOR = "test.WeirdBuiltin"

        WeirdBuiltin.__parameters__ = (object(),)  # type: ignore[attr-defined]
        with self.assertRaises(TypeError):
            morph.build_builtin_type(WeirdBuiltin, str)

    def test_runtime_type_args_and_union_transform_cover_additional_branches(self):
        self.assertEqual(morph.builtin_runtime_type_args(RuntimeArgsBox(value="x", runtime_orig_class_repr="str")), (str,))
        self.assertEqual(repr(morph.val(morph.type_from_python(tuple[str, ...]))), "std.List std.Text")
        self.assertEqual(repr(morph.val(morph.type_from_python(list[str]))), "std.List std.Text")

    def test_native_registry_construct_rejects_unknown_or_bad_arity_layouts(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Thing)

        with self.assertRaises(ValueError):
            registry.construct(morph.nominal_type("test.Unknown"), ())
        with self.assertRaises(ValueError):
            registry.construct(cast(morph.NominalType, Thing._type()), ("x",))

    def test_native_backend_context_switches_active_registry_for_type_projection(self):
        registry = morph.NativeRegistry()
        registry.register_native_type(bytes, morph.TEXT_TYPE)
        backend = morph.NativeBackend(registry=registry)

        with backend:
            self.assertEqual(morph.type_from_python(bytes), morph.TEXT_TYPE)


if __name__ == "__main__":
    unittest.main()
