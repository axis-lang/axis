from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import cast

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Box, DummyContext, DummyVarType, Thing


class FailurePathTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

    def test_construct_route_rejects_opaque_types_and_layout_mismatches(self):
        with self.assertRaises((TypeError, RuntimeError)):
            morph.nominal_type("test.Opaque").construct(value=1)
        with self.assertRaises(ValueError):
            morph.struct_type(int, int).construct(1)
        with self.assertRaises(ValueError):
            morph.struct_type(name=str).construct(name="x", extra=1)
        with self.assertRaises(TypeError):
            morph.struct_type(name=str).construct(name=(1, 2))

    def test_decode_route_rejects_invalid_atomic_and_structural_raw_payloads(self):
        with self.assertRaises(TypeError):
            morph.TEXT_TYPE.decode(1)
        with self.assertRaises(TypeError):
            morph.EMPTY_TYPE.decode("x")
        with self.assertRaises(TypeError):
            morph.struct_type(int, int).decode("x")
        with self.assertRaises(ValueError):
            morph.struct_type(int, int).decode((1,))

    def test_encode_route_rejects_wrong_structural_payload_shape(self):
        type_ = morph.struct_type(name=str, value=int)

        with self.assertRaises(TypeError):
            type_.serialize("x")
        with self.assertRaises(ValueError):
            type_.serialize(("x",))

    def test_literal_and_union_routes_reject_unsupported_inputs(self):
        with self.assertRaises(TypeError):
            morph.literal(cast(morph.Literal, object()))
        with self.assertRaises(TypeError):
            morph.union(frozenset({morph.INTEGER_TYPE}), morph.literal("x"))
        with self.assertRaises(ValueError):
            morph.union_value(int, active=cast(morph.Literal | type | morph.Type | morph.Const | morph.Var, object()))

    def test_val_route_rejects_unsupported_values_and_non_string_dict_keys(self):
        with self.assertRaises(ValueError):
            morph.val()
        with self.assertRaises(ValueError):
            morph.val({1: "x"})
        with self.assertRaises(ValueError):
            morph.val(object())

    def test_var_and_native_builder_routes_cover_invalid_projection_cases(self):
        type_var = morph.var(DummyVarType, DummyContext(), "T")

        with self.assertRaises(ValueError):
            type_var._wrap("U")
        with self.assertRaises(TypeError):
            Thing._type(str)
        with self.assertRaises(TypeError):
            Box._type(cast(type | morph.Type, 1))

    def test_encode_and_type_decode_routes_cover_variable_values(self):
        variable = morph.var(DummyVarType, DummyContext(), "T")

        self.assertEqual(variable.encode(), "T")
        self.assertEqual(variable.type.decode(variable.encode()), variable)


if __name__ == "__main__":
    unittest.main()
