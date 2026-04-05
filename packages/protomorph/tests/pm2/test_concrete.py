from __future__ import annotations

import unittest
from typing import cast

from pm import Id, Index, IndexedType, LeafCarrier, Spec, Tuple, UniformType, UnionType, VaryingType, wrap


INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())
FLOAT = cast(Spec, wrap(float).fetch())


class TestAtomicSpecs(unittest.TestCase):
    def test_int_is_spec(self):
        self.assertEqual(INT, Spec.of("std.types.Integer"))

    def test_make_leaf_carrier(self):
        carrier = INT.make(42)
        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(carrier.fetch(), 42)


class TestUniformType(unittest.TestCase):
    def test_arity_none(self):
        self.assertIsNone(UniformType(INT).arity)

    def test_item_at(self):
        item = UniformType(STR).item_at(5)
        self.assertEqual(item.offset, 5)
        self.assertIs(item.value, STR)

    def test_make(self):
        carrier = UniformType(INT).make((1, 2))
        self.assertIsInstance(carrier, Tuple)


class TestUnionType(unittest.TestCase):
    def test_of_single_returns_type(self):
        self.assertIs(UnionType.of(INT), INT)

    def test_of_multiple(self):
        union = cast(UnionType, UnionType.of(INT, STR))
        self.assertEqual(union.variants, frozenset({INT, STR}))


class TestVaryingType(unittest.TestCase):
    def test_make_positional(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR, FLOAT))
        self.assertEqual(vt.values, (INT, STR, FLOAT))

    def test_indexed(self):
        vt = cast(IndexedType, IndexedType.of(x=INT, y=STR))
        self.assertIs(vt.item(Id("x")).value, INT)

    def test_carrier(self):
        vt = cast(VaryingType, VaryingType.of(INT))
        self.assertIsInstance(vt.make((42,)), Tuple)


if __name__ == "__main__":
    unittest.main()
