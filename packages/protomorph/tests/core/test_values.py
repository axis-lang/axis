from __future__ import annotations

import unittest
from typing import cast

from protobase import frozendict
import protomorph as pm

from protomorph import (
    Builtin,
    Id,
    LeafCarrier,
    Map,
    NativeObjectCarrier,
    Option,
    Result,
    Set,
    Tuple,
    make_value,
    val,
    var,
)


INT = pm.types.integer
STR = pm.types.text
ANY = pm.types.any


class Point(Builtin):
    SPEC_NAME = "test.values.Point"
    x: int


class TestMakeValuePassthrough(unittest.TestCase):
    def test_returns_existing_carrier_unchanged(self):
        carrier = LeafCarrier(INT, 7)

        self.assertIs(make_value(INT, carrier), carrier)


class TestMakeTypeValue(unittest.TestCase):
    def test_spec_type_value_uses_leaf_carrier(self):
        carrier = make_value(ANY, INT)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertIs(carrier.content, INT)

    def test_qual_type_value_uses_leaf_carrier(self):
        qual = pm.types.optional(INT)

        carrier = make_value(ANY, qual)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(carrier.content, qual)

    def test_uniform_type_value_exposes_logical_children(self):
        carrier = make_value(ANY, pm.types.uniform(pm.types.varying(INT, STR)))

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(
            [child.content for child in carrier],
            [pm.types.uniform(INT), pm.types.uniform(STR)],
        )

    def test_varying_type_value_exposes_logical_children(self):
        varying = pm.types.varying(INT, STR)

        carrier = make_value(ANY, varying)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual([child.content for child in carrier], [INT, STR])

    def test_indexed_type_value_exposes_logical_children(self):
        indexed = pm.types.indexed(x=INT, y=STR)

        carrier = make_value(ANY, indexed)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual([child.content for child in carrier], [INT, STR])

    def test_val_spec_keeps_native_object_structure(self):
        carrier = val(pm.types.named("test.Test", INT))

        self.assertIsInstance(carrier, NativeObjectCarrier)
        self.assertEqual([leaf.content for leaf in carrier.children], ["test.Test", (INT,)])

    def test_val_qual_keeps_native_object_structure(self):
        qual = pm.types.optional(INT)

        carrier = val(qual)

        self.assertIsInstance(carrier, NativeObjectCarrier)


class TestMakeValueLeafDispatch(unittest.TestCase):
    def test_placeholder_value_uses_leaf_carrier(self):
        placeholder = var("T")

        carrier = make_value(INT, placeholder)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertIs(carrier.content, placeholder)
        self.assertIs(carrier.descriptor, INT)

    def test_placeholder_descriptor_uses_leaf_carrier(self):
        placeholder = var("T")
        descriptor = var("U")

        carrier = make_value(descriptor, placeholder)

        self.assertIsInstance(carrier, LeafCarrier)

    def test_union_descriptor_uses_leaf_carrier(self):
        descriptor = pm.types.union(INT, STR)

        carrier = make_value(descriptor, 7)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(carrier.content, 7)


class TestMakeValueQualifiedDispatch(unittest.TestCase):
    def test_result_qualifier_builds_result(self):
        descriptor = pm.types.result(INT, err=STR)

        carrier = cast(Result, make_value(descriptor, 1))

        self.assertIsInstance(carrier, Result)
        self.assertTrue(carrier.is_ok)

    def test_optional_qualifier_builds_option(self):
        descriptor = pm.types.optional(INT)

        carrier = cast(Option, make_value(descriptor, 1))

        self.assertIsInstance(carrier, Option)
        self.assertTrue(carrier.is_some)

    def test_set_qualifier_coerces_set_to_frozenset_and_builds_set(self):
        descriptor = pm.types.set(INT)

        carrier = make_value(descriptor, {1, 2})

        self.assertIsInstance(carrier, Set)
        self.assertIsInstance(carrier.content, frozenset)

    def test_map_qualifier_coerces_dict_to_frozendict_and_builds_map(self):
        descriptor = pm.types.map(INT, key=STR)

        carrier = make_value(descriptor, {Id("a"): 1})

        self.assertIsInstance(carrier, Map)
        self.assertIsInstance(carrier.content, frozendict)

    def test_unknown_qualifier_falls_back_to_qualified_descriptor(self):
        descriptor = pm.types.qualify(pm.Spec.of("test.qualifiers.Unknown"), under=INT)

        carrier = make_value(descriptor, 1)

        self.assertIsInstance(carrier, LeafCarrier)
        self.assertIs(carrier.descriptor, INT)


class TestMakeValueTupleDispatch(unittest.TestCase):
    def test_uniform_unique_builds_index(self):
        carrier = make_value(pm.types.uniform(INT, unique=True), (Id("a"), Id("b")))

        self.assertEqual(type(carrier).__name__, "Index")

    def test_uniform_non_unique_builds_tuple(self):
        carrier = make_value(pm.types.uniform(INT), (1, 2))

        self.assertIsInstance(carrier, Tuple)

    def test_varying_builds_tuple(self):
        carrier = make_value(pm.types.varying(INT, STR), (1, "x"))

        self.assertIsInstance(carrier, Tuple)

    def test_indexed_builds_tuple(self):
        carrier = make_value(pm.types.indexed(x=INT), (1,))

        self.assertIsInstance(carrier, Tuple)


class TestMakeValueSpecDispatch(unittest.TestCase):
    def test_leaf_spec_builds_leaf_carrier(self):
        carrier = make_value(INT, 7)

        self.assertIsInstance(carrier, LeafCarrier)

    def test_structured_spec_builds_native_object_carrier(self):
        descriptor = pm.types.named("test.values.Point")

        carrier = make_value(descriptor, Point(1))

        self.assertIsInstance(carrier, NativeObjectCarrier)
        self.assertEqual(carrier.attr(Id("x")).content, 1)


if __name__ == "__main__":
    unittest.main()
