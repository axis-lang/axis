from __future__ import annotations

import unittest
from typing import cast
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Thing


class TypesAndQualifiersTests(unittest.TestCase):
    def test_type_route_covers_wrap_encode_decode_dir_and_get_for_struct_types(self):
        struct_type = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE, value=morph.INTEGER_TYPE))
        wrapped = struct_type._wrap(("x", 1))
        fields = struct_type._dir()

        self.assertEqual(repr(wrapped), "(name='x', value=1)")
        self.assertEqual(struct_type._decode(("x", 1)), ("x", 1))
        assert fields is not None
        self.assertEqual(tuple(fields.index.keys), ("name", "value"))
        self.assertEqual(repr(struct_type._get(("x", 1), "name")), "'x'")
        self.assertEqual(repr(struct_type._get(("x", 1), 1)), "1")

    def test_type_exception_route_rejects_invalid_get_and_decode_shapes(self):
        struct_type = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE))

        with self.assertRaises(TypeError):
            struct_type._get(("x",), cast(str | int, 1.5))
        with self.assertRaises(TypeError):
            struct_type._get(1, "name")
        with self.assertRaises(TypeError):
            struct_type._decode("x")
        with self.assertRaises(ValueError):
            struct_type._decode(())

    def test_type_meta_route_covers_type_of_types_and_struct_meta_specs(self):
        struct_type = morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE))

        self.assertEqual(repr(morph.val(struct_type._metatype())), "dom.Struct.Type[dom.Nominal.Type]")
        self.assertIsNone(morph.INTEGER_TYPE._metaspec())

    def test_type_class_route_rejects_host_specific_args_in_core_type_classes(self):
        with self.assertRaises(TypeError):
            morph.StructType._type(morph.TEXT_TYPE)

    def test_nominal_type_route_covers_fields_encode_decode_and_native_construct(self):
        with morph.DEFAULT_NATIVE_BACKEND:
            type_ = Thing._type()
            fields = type_._dir()
            encoded = type_._encode(Thing(name="x", value=1))
            decoded = type_._decode(("x", 1))

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(tuple(fields.index.keys), ("name", "value"))
        self.assertEqual(encoded, ("x", 1))
        decoded_thing = cast(Thing, decoded)
        self.assertIsInstance(decoded_thing, Thing)
        self.assertEqual(decoded_thing.value, 1)

    def test_nominal_type_exception_route_covers_opaque_and_bad_payload_paths(self):
        opaque = morph.nominal_type("test.Opaque")
        with self.assertRaises(ValueError):
            with morph.DEFAULT_NATIVE_BACKEND:
                Thing._type()._encode("x")
        with self.assertRaises(ValueError):
            with morph.DEFAULT_NATIVE_BACKEND:
                Thing._type()._decode("x")
        self.assertEqual(opaque._decode("x"), "x")

    def test_nominal_type_route_preserves_std_any_special_case(self):
        any_type = morph.nominal_type("std.Any")

        self.assertEqual(any_type._decode("payload"), "payload")

    def test_union_type_route_covers_invariants_and_decode_exception(self):
        union_type = morph.union_type(morph.TEXT_TYPE, morph.INTEGER_TYPE)
        self.assertEqual(
            morph.UnionType(types=frozenset({morph.union_type(morph.TEXT_TYPE, morph.INTEGER_TYPE)})).types,
            frozenset({morph.union_type(morph.TEXT_TYPE, morph.INTEGER_TYPE)}),
        )
        with self.assertRaises(NotImplementedError):
            union_type._decode("x")

    def test_qualifier_route_covers_meta_dir_and_exception_contracts(self):
        qualified = morph.nominal_qual(
            "test.Future",
            underlying=morph.StructType(meta_attrs=morph.Struct.new(name=morph.TEXT_TYPE)),
        )

        self.assertFalse(qualified.is_meta)
        self.assertIsNotNone(qualified._metaspec())
        fields = qualified._dir()
        assert fields is not None
        self.assertEqual(repr(morph.val(fields.get("name"))), "test.Future std.Text")
        with self.assertRaises(NotImplementedError):
            qualified._get(("x",), "name")
        with self.assertRaises(NotImplementedError):
            qualified._encode(("x",))
        with self.assertRaises(NotImplementedError):
            qualified._decode(("x",))
