from __future__ import annotations

import unittest
from typing import cast

from protomorph import Id, Index, Indexed, LeafCarrier, Spec, Tuple, Uniform, Union, Varying, val
import protomorph as pm


INT = cast(Spec, val(int).content)
STR = cast(Spec, val(str).content)
FLOAT = cast(Spec, val(float).content)


class TestAtomicSpecs(unittest.TestCase):
    def test_int_is_spec(self):
        self.assertEqual(INT, Spec.of("std.types.Integer"))

    def test_make_leaf_carrier(self):
        carrier = INT.make(42)
        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(carrier.content, 42)


class TestUniformType(unittest.TestCase):
    def test_leaf_element_schema_is_none(self):
        self.assertIsNone(Uniform(INT).schema)

    def test_schema_projects_structured_element(self):
        schema = Uniform(cast(Varying, Varying.of(INT, STR))).schema

        assert schema is not None
        self.assertEqual(schema[0].content, Uniform(INT))
        self.assertEqual(schema[1].content, Uniform(STR))

    def test_make(self):
        carrier = Uniform(INT).make((1, 2))
        self.assertIsInstance(carrier, Tuple)

    def test_contains_same_element_type(self):
        self.assertIn(Uniform(INT), Uniform(INT))

    def test_unique_false_contains_unique_true(self):
        self.assertIn(Uniform(INT, unique=True), Uniform(INT, unique=False))

    def test_unique_true_does_not_contain_non_unique(self):
        self.assertNotIn(Uniform(INT, unique=False), Uniform(INT, unique=True))


class TestUnionType(unittest.TestCase):
    def test_of_single_returns_type(self):
        self.assertIs(pm.types.Union.of(INT), INT)

    def test_of_multiple(self):
        union = cast(pm.Union, pm.types.Union.of(INT, STR))
        self.assertEqual(union.variants, frozenset({INT, STR}))

    def test_contains_member_variant(self):
        union = cast(pm.Union, pm.types.Union.of(INT, STR))

        self.assertIn(INT, union)

    def test_contains_subset_union(self):
        union = cast(pm.Union, pm.types.Union.of(INT, STR, FLOAT))
        subset = cast(pm.Union, pm.types.Union.of(INT, STR))

        self.assertIn(subset, union)


class TestVaryingType(unittest.TestCase):
    def test_make_positional(self):
        vt = cast(Varying, Varying.of(INT, STR, FLOAT))
        self.assertEqual(vt.element_types, (INT, STR, FLOAT))

    def test_indexed(self):
        vt = cast(Indexed, Indexed.of(x=INT, y=STR))
        self.assertIs(vt.schema.attr(Id("x")).content, INT)

    def test_carrier(self):
        vt = cast(Varying, Varying.of(INT))
        self.assertIsInstance(vt.make((42,)), Tuple)

    def test_contains_element_by_element(self):
        self.assertIn(Varying.of(INT, STR), Varying.of(INT, STR))


if __name__ == "__main__":
    unittest.main()
