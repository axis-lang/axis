from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import cast

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, EmptyThing, PairBox, RuntimeArgsBox, StrictThing, Thing, UnsupportedQualifier


class LayoutAndNativeTests(unittest.TestCase):
    def test_native_registry_routes_cover_template_layout_and_construct(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Thing)
        registry.register_builtin(EmptyThing)

        layout = registry.layout(cast(morph.NominalType, Thing._type()))
        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), ("name", "value"))
        self.assertIs(layout.builtin_cls, Thing)
        self.assertEqual(cast(Thing, registry.construct(cast(morph.NominalType, Thing._type()), ("x", 1))).value, 1)
        self.assertIsInstance(registry.construct(cast(morph.NominalType, EmptyThing._type()), ()), EmptyThing)

    def test_native_backend_routes_cover_layout_projection_and_materialization(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Thing)
        backend = morph.NativeBackend(registry=registry)
        type_ = cast(morph.NominalType, Thing._type())

        layout = backend.layout(type_)
        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), ("name", "value"))
        self.assertEqual(cast(Thing, backend.construct(type_, ("x", 1))).name, "x")

    def test_type_from_python_routes_cover_scalars_containers_unions_and_builtins(self):
        self.assertEqual(repr(morph.val(morph.type_(dict[str, str]))), "std.Map[K=std.Text] std.Text")
        self.assertEqual(repr(morph.val(morph.type_(tuple[int, ...]))), "std.List std.Integer")
        self.assertEqual(set(repr(morph.val(int | str)).split(" | ")), {"std.Integer", "std.Text"})
        self.assertEqual(repr(morph.val(morph.type_(Box[str]))), "test.Box[T=std.Text]")
        self.assertEqual(repr(morph.val(PairBox._type(str, int))), "test.PairBox[K=std.Text, V=std.Integer]")

    def test_native_backend_exposes_atomic_layouts_for_scalar_nominals(self):
        with morph.DEFAULT_NATIVE_BACKEND:
            layout = morph.TEXT_TYPE.layout()

        self.assertIsInstance(layout, morph.AtomicLayout)
        assert isinstance(layout, morph.AtomicLayout)
        self.assertEqual(layout.valid_types, frozenset({str}))

    def test_runtime_orig_class_route_extracts_native_type_arguments(self):
        self.assertEqual(
            morph.builtin_runtime_type_args(RuntimeArgsBox(value="x", runtime_orig_class_repr="str")),
            (str,),
        )
        self.assertIsNone(morph.builtin_runtime_type_args(RuntimeArgsBox(value="x", runtime_orig_class_repr="list")))

    def test_qualifier_layout_route_lifts_structural_fields(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        bridge = Bridge()
        qualified = morph.nominal_type("test.Future").qualify(morph.struct_type(name=str))

        layout = bridge.layout(qualified)
        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(repr(morph.val(layout.fields.get("name"))), "test.Future std.Text")

    def test_bridge_rejects_unsupported_qualifier_lift(self):
        class Bridge(morph.SemanticBridgeBase):
            pass

        with self.assertRaises(NotImplementedError):
            Bridge().lift(UnsupportedQualifier(underlying=morph.TEXT_TYPE), morph.INTEGER_TYPE)

    def test_registry_construct_currently_preserves_surprising_builtin_invariants(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(StrictThing)

        self.assertEqual(repr(registry.construct(cast(morph.NominalType, StrictThing._type()), (-1,))), "StrictThing(-1)")


if __name__ == "__main__":
    unittest.main()
