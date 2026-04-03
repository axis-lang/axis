from __future__ import annotations

import unittest
from typing import Any, cast

from protomorph import Builtin, Err, Id, Index, LeafCarrier, Ok, Qual, Result, Spec, Tuple, UniformType, VaryingType, placeholder, wrap


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

class TestResultCarrier(unittest.TestCase):
    def test_result_make_requires_explicit_variant(self):
        result_int = Qual.of(INT, Spec.of("std.qualifiers.Result", STR))

        with self.assertRaises(TypeError):
            result_int.make(1)

    def test_result_err_uses_result_error_type(self):
        result_int = Qual.of(INT, Spec.of("std.qualifiers.Result", STR))

        carrier = cast(Result, result_int.make(Err("bad")))

        self.assertTrue(carrier.is_err)
        self.assertEqual(carrier.error_carrier().descriptor, STR)

    def test_result_ok_constructor_uses_result_qualifier(self):
        value = LeafCarrier(INT, 1)

        carrier = Result.ok(value)

        self.assertEqual(type(carrier.descriptor).__name__, "Qual")
        self.assertTrue(carrier.is_ok)
        self.assertEqual(carrier.value_carrier().descriptor, INT)

    def test_result_ok_constructor_preserves_qualified_descriptor(self):
        value = LeafCarrier(Qual.of(INT, Spec.of("std.qualifiers.Map", STR)), 1)

        carrier = Result.ok(value)

        self.assertEqual(carrier.value_carrier().descriptor, INT)
        self.assertEqual(carrier.descriptor.underlying, INT)
        self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[0].fetch()).anchor, "std.qualifiers.Map")
        self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[-1].fetch()).anchor, "std.qualifiers.Result")

    def test_result_ok_constructor_rejects_non_carrier(self):
        with self.assertRaises(TypeError):
            cast(Any, Result.ok)(1)

    def test_result_make_accepts_explicit_ok_variant(self):
        result_int = Qual.of(INT, Spec.of("std.qualifiers.Result", STR))

        carrier = cast(Result, result_int.make(Ok(1)))

        self.assertTrue(carrier.is_ok)
        self.assertEqual(carrier.value_carrier().fetch(), 1)


class TestTypeProperty(unittest.TestCase):
    def test_type_carrier(self):
        carrier = LeafCarrier(INT, 42)
        self.assertEqual(carrier.type.fetch(), INT)


if __name__ == "__main__":
    unittest.main()
