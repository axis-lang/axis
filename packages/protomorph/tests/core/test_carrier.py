from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, Id, OMEGA,
    Placeholder, placeholder,
    Carrier, NativeObjectCarrier, LeafCarrier, TupleCarrier,
    ScalarType, UniformType, VaryingType, NativeType,
    INT_TYPE, STR_TYPE, FLOAT_TYPE,
    native_type, wrap,
)


class TestLeafCarrier(unittest.TestCase):

    def test_is_leaf(self):
        c = LeafCarrier(OMEGA, 42)
        self.assertTrue(c.is_leaf)

    def test_fetch(self):
        c = LeafCarrier(OMEGA, "hello")
        self.assertEqual(c.fetch(), "hello")

    def test_reconstruct_returns_self(self):
        c = LeafCarrier(OMEGA, 42)
        self.assertIs(c.reconstruct(()), c)

    def test_consing(self):
        a = LeafCarrier(OMEGA, 42)
        b = LeafCarrier(OMEGA, 42)
        self.assertIs(a, b)


class TestTupleCarrier(unittest.TestCase):

    def test_uniform_iteration(self):
        ut = UniformType(INT_TYPE)
        c = TupleCarrier(ut, (10, 20, 30))
        children = list(c)
        self.assertEqual(len(children), 3)
        self.assertEqual(children[0].fetch(), 10)
        self.assertEqual(children[2].fetch(), 30)

    def test_varying_iteration(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = TupleCarrier(vt, (42, "hello"))
        children = list(c)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].fetch(), 42)
        self.assertEqual(children[1].fetch(), "hello")

    def test_getitem(self):
        ut = UniformType(INT_TYPE)
        c = TupleCarrier(ut, (10, 20))
        self.assertEqual(c[0].fetch(), 10)
        self.assertEqual(c[1].fetch(), 20)

    def test_reconstruct(self):
        ut = UniformType(INT_TYPE)
        c = TupleCarrier(ut, (10, 20))
        children = (LeafCarrier(INT_TYPE, 100), LeafCarrier(INT_TYPE, 200))
        r = c.reconstruct(children)
        self.assertEqual(r.fetch(), (100, 200))

    def test_len_uniform_from_data(self):
        ut = UniformType(INT_TYPE)
        c = TupleCarrier(ut, (1, 2, 3))
        self.assertEqual(len(c), 3)

    def test_len_varying_from_type(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = TupleCarrier(vt, (1, "a"))
        self.assertEqual(len(c), 2)


class TestNativeObjectCarrier(unittest.TestCase):

    def test_iteration(self):
        class Pt(Builtin):
            x: int
            y: int

        pt = Pt(1, 2)
        pt_type = native_type(Pt)
        c = NativeObjectCarrier(pt_type, pt)
        children = list(c)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].fetch(), 1)
        self.assertEqual(children[1].fetch(), 2)

    def test_attr(self):
        class Pt(Builtin):
            x: int
            y: int

        pt = Pt(3, 4)
        c = wrap(pt)
        self.assertEqual(c.attr(Id("x")).fetch(), 3)
        self.assertEqual(c.attr(Id("y")).fetch(), 4)

    def test_reconstruct(self):
        class Pt(Builtin):
            x: int
            y: int

        pt = Pt(1, 2)
        c = wrap(pt)
        children = (LeafCarrier(OMEGA, 10), LeafCarrier(OMEGA, 20))
        r = c.reconstruct(children)
        self.assertEqual(r.fetch(), Pt(10, 20))

    def test_not_leaf(self):
        class Pt(Builtin):
            x: int

        c = wrap(Pt(1))
        self.assertFalse(c.is_leaf)


class TestChildPlaceholderSpecialCase(unittest.TestCase):
    """Carrier.child() wraps Placeholder data as LeafCarrier."""

    def test_placeholder_data_becomes_leaf(self):
        ph = placeholder("T")
        c = LeafCarrier(OMEGA, 0)
        child = c.child(INT_TYPE, ph)
        self.assertIsInstance(child, LeafCarrier)
        self.assertIs(child.fetch(), ph)


class TestTypeProperty(unittest.TestCase):
    """carrier.type returns a Carrier wrapping the type."""

    def test_type_carrier(self):
        c = LeafCarrier(INT_TYPE, 42)
        tc = c.type
        self.assertIsInstance(tc, NativeObjectCarrier)
        self.assertIs(tc.fetch(), INT_TYPE)


if __name__ == "__main__":
    unittest.main()
