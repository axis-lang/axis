from __future__ import annotations

import unittest
from typing import cast

from pm import(
    Builtin, Id, Index,
    Placeholder, placeholder,
    NativeObjectCarrier, LeafCarrier, TupleCarrier, Spec,
    UniformType, VaryingType,
    native_type, wrap,
)


INT = wrap(int)
STR = wrap(str)
ANY = Spec.of("std.core.Any")


class TestLeafCarrier(unittest.TestCase):
    def test_is_leaf(self):
        c = LeafCarrier(ANY, 42)
        self.assertTrue(c.is_leaf)

    def test_fetch(self):
        c = LeafCarrier(ANY, "hello")
        self.assertEqual(c.fetch(), "hello")

    def test_reconstruct_returns_self(self):
        c = LeafCarrier(ANY, 42)
        self.assertIs(c.reconstruct(()), c)


class TestTupleCarrier(unittest.TestCase):
    def test_uniform_iteration(self):
        ut = UniformType(INT, Index.Empty)
        c = TupleCarrier(ut, (10, 20, 30))
        self.assertEqual([child.fetch() for child in c], [10, 20, 30])

    def test_varying_iteration(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = TupleCarrier(vt, (42, "hello"))
        self.assertEqual([child.fetch() for child in c], [42, "hello"])

    def test_getitem(self):
        ut = UniformType(INT, Index.Empty)
        c = TupleCarrier(ut, (10, 20))
        self.assertEqual(c[0].fetch(), 10)
        self.assertEqual(c[1].fetch(), 20)

    def test_reconstruct(self):
        ut = UniformType(INT, Index.Empty)
        c = TupleCarrier(ut, (10, 20))
        children = (LeafCarrier(INT, 100), LeafCarrier(INT, 200))
        r = c.reconstruct(children)
        self.assertEqual(r.fetch(), (100, 200))


class TestNativeObjectCarrier(unittest.TestCase):
    def test_iteration(self):
        class Pt(Builtin):
            x: int
            y: int

        c = native_type(Pt).make(Pt(1, 2))
        self.assertEqual([child.fetch() for child in c], [1, 2])

    def test_attr(self):
        class Pt(Builtin):
            x: int
            y: int

        c = wrap(Pt(3, 4))
        self.assertEqual(c.attr(Id("x")).fetch(), 3)
        self.assertEqual(c.attr(Id("y")).fetch(), 4)

    def test_reconstruct(self):
        class Pt(Builtin):
            x: int
            y: int

        c = wrap(Pt(1, 2))
        children = (LeafCarrier(ANY, 10), LeafCarrier(ANY, 20))
        self.assertEqual(c.reconstruct(children).fetch(), Pt(10, 20))


class TestChildPlaceholderSpecialCase(unittest.TestCase):
    def test_placeholder_data_becomes_leaf(self):
        ph = placeholder("T")
        child = LeafCarrier(ANY, 0).child(INT, ph)
        self.assertIsInstance(child, LeafCarrier)
        self.assertIs(child.fetch(), ph)


class TestTypeProperty(unittest.TestCase):
    def test_type_carrier(self):
        c = LeafCarrier(INT, 42)
        tc = c.type
        self.assertIsInstance(tc, NativeObjectCarrier)
        self.assertIs(tc.fetch(), INT)


if __name__ == "__main__":
    unittest.main()
