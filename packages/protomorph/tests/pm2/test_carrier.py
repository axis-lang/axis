from __future__ import annotations

import unittest
from typing import cast

from pm import Builtin, Id, Index, LeafCarrier, Placeholder, Spec, Tuple, UniformType, VaryingType, placeholder, wrap


INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())
ANY = Spec.of("std.core.Any")


class TestLeafCarrier(unittest.TestCase):
    def test_is_leaf(self):
        self.assertTrue(LeafCarrier(ANY, 42).is_leaf)

    def test_fetch(self):
        self.assertEqual(LeafCarrier(ANY, "hello").fetch(), "hello")


class TestTuple(unittest.TestCase):
    def test_uniform_iteration(self):
        carrier = Tuple(UniformType(INT), (10, 20, 30))
        self.assertEqual([child.fetch() for child in carrier], [10, 20, 30])

    def test_varying_iteration(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (42, "hello"))
        self.assertEqual([child.fetch() for child in carrier], [42, "hello"])

    def test_reconstruct(self):
        carrier = Tuple(UniformType(INT), (10, 20))
        children = (LeafCarrier(INT, 100), LeafCarrier(INT, 200))
        self.assertEqual(carrier.reconstruct(children).fetch(), (100, 200))

    def test_invalid_arity_raises(self):
        with self.assertRaises(AssertionError):
            Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, 2, 3))


class TestIndexCarrier(unittest.TestCase):
    def test_sparse(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertTrue(index.is_sparse)

    def test_offset_of(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(index.offset_of(Id("z")), 2)

    def test_offsets(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(index.offsets, {Id("x"): 0, Id("z"): 2})


class TestNativeObjectCarrier(unittest.TestCase):
    def test_attr(self):
        class Pt(Builtin):
            SPEC_NAME = "test.carrier.Point"
            x: int
            y: int

        carrier = wrap(Pt(3, 4))
        self.assertEqual(carrier.attr(Id("x")).fetch(), 3)
        self.assertEqual(carrier.attr(Id("y")).fetch(), 4)

    def test_reconstruct(self):
        class Pt(Builtin):
            SPEC_NAME = "test.carrier.Point2"
            x: int
            y: int

        carrier = wrap(Pt(1, 2))
        rebuilt = carrier.reconstruct((LeafCarrier(ANY, 10), LeafCarrier(ANY, 20)))
        self.assertEqual(rebuilt.fetch(), Pt(10, 20))


class TestChildRules(unittest.TestCase):
    def test_placeholder_data_becomes_leaf(self):
        ph = placeholder("T")
        child = LeafCarrier(ANY, 0).child(INT, ph)
        self.assertIsInstance(child, LeafCarrier)
        self.assertIs(child.fetch(), ph)

    def test_type_data_becomes_type_carrier(self):
        child = LeafCarrier(ANY, 0).child(ANY, INT)
        self.assertEqual(child.fetch(), INT)

    def test_nested_carrier_is_preserved(self):
        nested = LeafCarrier(INT, 7)
        child = LeafCarrier(ANY, 0).child(ANY, nested)
        self.assertIs(child, nested)


class TestTypeProperty(unittest.TestCase):
    def test_type_carrier(self):
        carrier = LeafCarrier(INT, 42)
        self.assertEqual(carrier.type.fetch(), INT)


if __name__ == "__main__":
    unittest.main()
