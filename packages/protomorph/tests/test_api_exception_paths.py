from __future__ import annotations

import unittest
from typing import cast
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


class ApiExceptionPathTests(unittest.TestCase):
    def test_literal_route_rejects_unsupported_python_scalars(self):
        invalid_literal = cast(morph.Literal, object())
        with self.assertRaises(TypeError):
            morph.literal(invalid_literal)

    def test_union_route_rejects_active_variant_outside_union(self):
        with self.assertRaises(TypeError):
            morph.union(frozenset({morph.INTEGER_TYPE}), morph.literal("x"))

    def test_val_route_requires_at_least_one_argument(self):
        with self.assertRaises(ValueError):
            morph.val()

    def test_val_route_rejects_non_string_dict_keys(self):
        with self.assertRaises(ValueError):
            morph.val({1: "x"})

    def test_val_route_rejects_unsupported_host_values(self):
        with self.assertRaises(ValueError):
            morph.val(object())

    def test_encode_and_decode_routes_reject_non_const_values(self):
        variable = morph.var(DummyVarType, DummyContext(), "T")

        with self.assertRaises(TypeError):
            morph.encode(variable)
        with self.assertRaises(TypeError):
            morph.decode(variable)

    def test_native_type_route_rejects_unknown_python_classes(self):
        with self.assertRaises(TypeError):
            morph.native_type(cast(type, dict))
