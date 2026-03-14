from __future__ import annotations

import unittest
from typing import Any, TypeVar, cast
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, EmptyThing, PairBox, RuntimeArgsBox, StrictThing, Thing


class NativeFrontendAndBackendTests(unittest.TestCase):
    def test_type_from_python_happy_paths_cover_scalars_containers_unions_and_builtins(self):
        self.assertEqual(repr(morph.val(morph.type_from_python(str))), "std.Text")
        self.assertEqual(repr(morph.val(morph.type_from_python(dict[str, str]))), "std.Map[K=std.Text] std.Text")
        self.assertEqual(repr(morph.val(morph.type_from_python(list[int]))), "std.List std.Integer")
        self.assertEqual(repr(morph.val(morph.type_from_python(tuple[int, ...]))), "std.List std.Integer")
        self.assertEqual(
            set(repr(morph.val(morph.type_from_python(int | str))).split(" | ")),
            {"std.Integer", "std.Text"},
        )
        self.assertEqual(repr(morph.val(morph.type_from_python(Box[str]))), "test.Box[T=std.Text]")
        self.assertEqual(repr(morph.val(morph.type_from_python(Any))), "std.Any")
        self.assertEqual(repr(morph.val(morph.type_from_python(object))), "std.Any")

    def test_type_from_python_route_tracks_typevars_for_builtin_templates(self):
        T = TypeVar("T")
        vars: set[morph.Var] = set()

        projected = morph.type_from_python(T, vars=vars)

        self.assertIsInstance(projected, morph.Var)
        self.assertEqual({var.data for var in vars}, {"T"})

    def test_build_builtin_type_happy_paths_cover_unparameterized_and_parameterized_builtins(self):
        self.assertEqual(repr(morph.val(Thing._type())), "test.Thing")
        self.assertEqual(repr(morph.val(Box._type(str))), "test.Box[T=std.Text]")
        self.assertEqual(repr(morph.val(PairBox._type(str, int))), "test.PairBox[K=std.Text, V=std.Integer]")

    def test_build_builtin_type_exception_paths_cover_arity_and_unprojectable_args(self):
        with self.assertRaises(TypeError):
            Thing._type(str)
        self.assertEqual(repr(morph.val(Box._type())), "test.Box")
        with self.assertRaises(TypeError):
            Box._type(str, int)
        with self.assertRaises(TypeError):
            Box._type(cast(type | morph.Type, 1))

    def test_runtime_type_arg_route_covers_missing_valid_and_invalid_orig_class_shapes(self):
        value = RuntimeArgsBox(value="x", runtime_orig_class_repr="str")
        invalid_origin = RuntimeArgsBox(value="x", runtime_orig_class_repr="list")
        invalid_payload = RuntimeArgsBox(value="x", runtime_orig_class_repr="bogus")

        self.assertIsNone(morph.builtin_runtime_type_args(RuntimeArgsBox(value="x")))
        self.assertEqual(morph.builtin_runtime_type_args(value), (str,))
        self.assertIsNone(morph.builtin_runtime_type_args(invalid_origin))
        self.assertIsNone(morph.builtin_runtime_type_args(invalid_payload))

    def test_registry_routes_cover_manual_registration_and_active_backend_selection(self):
        registry = morph.NativeRegistry()
        backend = morph.NativeBackend(registry=registry)

        morph.register_native_type(bytes, morph.TEXT_TYPE, registry=registry)
        morph.register_python_type(bytes, lambda: morph.TEXT_TYPE, registry=registry)
        morph.register_builtin(Thing, registry=registry)

        self.assertIs(registry.type_by_python[bytes], morph.TEXT_TYPE)
        with backend:
            self.assertIs(morph.type_from_python(bytes), morph.TEXT_TYPE)

    def test_registry_template_and_field_routes_cover_caching_and_specialization(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Box)

        template_a = registry.template_for(Box)
        template_b = registry.template_for(Box)
        self.assertIs(template_a, template_b)

        type_ = cast(morph.NominalType, Box._type(str))
        fields_a = registry.fields(type_)
        fields_b = registry.fields(type_)
        self.assertIs(fields_a, fields_b)
        assert fields_a is not None
        self.assertEqual(repr(morph.val(fields_a.get("value"))), "std.Text")

    def test_registry_construct_routes_cover_success_and_exceptional_paths(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Thing)
        registry.register_builtin(EmptyThing)
        registry.register_builtin(StrictThing)

        self.assertEqual(cast(Thing, registry.construct(cast(morph.NominalType, Thing._type()), ("x", 1))).value, 1)
        self.assertIsInstance(registry.construct(cast(morph.NominalType, EmptyThing._type()), ()), EmptyThing)
        with self.assertRaises(ValueError):
            registry.construct(morph.nominal_type("test.Unknown"), ())
        with self.assertRaises(ValueError):
            registry.construct(cast(morph.NominalType, Thing._type()), ("x",))
        with self.assertRaises(ValueError):
            registry.construct(cast(morph.NominalType, EmptyThing._type()), (1,))
        self.assertEqual(
            repr(registry.construct(cast(morph.NominalType, StrictThing._type()), (-1,))),
            "StrictThing(-1)",
        )

    def test_native_backend_route_exposes_fields_class_for_and_construct_through_registry(self):
        registry = morph.NativeRegistry()
        registry.register_builtin(Thing)
        backend = morph.NativeBackend(registry=registry)
        type_ = cast(morph.NominalType, Thing._type())
        fields = backend.fields(type_)

        assert fields is not None
        self.assertEqual(tuple(fields.index.keys), ("name", "value"))
        self.assertIs(backend.class_for(type_), Thing)
        self.assertEqual(cast(Thing, backend.construct(type_, ("x", 1))).name, "x")
