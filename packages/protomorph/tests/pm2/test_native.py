from __future__ import annotations

import unittest
from typing import cast

from pm import (
    Builtin,
    HOST,
    NativeHost,
    NativeObjectCarrier,
    LeafCarrier,
    Spec,
    Qual,
    VaryingType,
    Placeholder,
    placeholder,
    register,
    spec_name,
    wrap,
)



INT = wrap(int)
STR = wrap(str)


class Point(Builtin):
    x: int
    y: int


class Container[T](Builtin):
    value: T


class Pair[A, B](Builtin):
    first: A
    second: B


class TestSpecName(unittest.TestCase):
    def test_default_name(self):
        name = spec_name(Point)
        self.assertIn("Point", name)
        self.assertIn(".", name)

    def test_explicit_name(self):
        class Custom(Builtin):
            SPEC_NAME = "my.Custom"

        self.assertEqual(spec_name(Custom), "my.Custom")


class TestRegister(unittest.TestCase):
    def test_register_returns_spec(self):
        spec = register(Point)
        self.assertIsInstance(spec, Spec)
        self.assertEqual(spec.anchor, spec_name(Point))


class TestNativeHostSchemaFor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = NativeHost()

    def test_unknown_spec_returns_none(self):
        spec = Spec.of("unknown.Thing")
        self.assertIsNone(self.host.schema_for(spec))

    def test_simple_class_schema(self):
        spec = Spec.of(spec_name(Point))
        schema = cast(VaryingType, self.host.schema_for(spec))
        self.assertIsNotNone(schema)
        self.assertIsInstance(schema, VaryingType)
        self.assertEqual(schema.arity, 2)
        self.assertEqual(schema.item_at(0).value, INT)
        self.assertEqual(schema.item_at(1).value, INT)

    def test_generic_unspecialized(self):
        spec = Spec.of(spec_name(Container))
        schema = cast(VaryingType, self.host.schema_for(spec))
        self.assertIsNotNone(schema)
        self.assertEqual(schema.arity, 1)
        ft = schema.item_at(0).value
        self.assertIsInstance(ft, Placeholder)

    def test_generic_specialized(self):
        spec = Spec.of(spec_name(Container), INT)
        schema = cast(VaryingType, self.host.schema_for(spec))
        self.assertIsNotNone(schema)
        self.assertEqual(schema.item_at(0).value, INT)

    def test_pair_specialized(self):
        spec = Spec.of(spec_name(Pair), INT, STR)
        schema = cast(VaryingType, self.host.schema_for(spec))
        self.assertIsNotNone(schema)
        self.assertEqual(schema.item_at(0).value, INT)
        self.assertEqual(schema.item_at(1).value, STR)


class TestSpecDelegation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._token = HOST.set(NativeHost())

    @classmethod
    def tearDownClass(cls):
        HOST.reset(cls._token)

    def test_arity(self):
        spec = Spec.of(spec_name(Point))
        self.assertEqual(spec.arity, 2)

    def test_item_at(self):
        spec = Spec.of(spec_name(Point))
        f = spec.item_at(0)
        self.assertEqual(f.key, "x")
        self.assertEqual(f.value, INT)

    def test_carrier_produces_native_object(self):
        spec = Spec.of(spec_name(Point))
        c = spec.make(Point(x=10, y=20))
        self.assertIsInstance(c, NativeObjectCarrier)

    def test_unknown_spec_is_leaf(self):
        spec = Spec.of("unknown.Thing")
        c = spec.make(42)
        self.assertIsInstance(c, LeafCarrier)


class TestQualDelegation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._token = HOST.set(NativeHost())

    @classmethod
    def tearDownClass(cls):
        HOST.reset(cls._token)

    def test_qual_delegates_to_underlying(self):
        spec = Spec.of(spec_name(Point))
        qual = Qual.of(spec, Spec.of("some.qualifier"))
        self.assertEqual(qual.arity, 2)
        f = qual.item_at(0)
        self.assertEqual(f.key, "x")

    def test_qual_carrier(self):
        spec = Spec.of(spec_name(Point))
        qual = Qual.of(spec, Spec.of("some.qualifier"))
        c = qual.make(Point(x=1, y=2))
        self.assertIsInstance(c, NativeObjectCarrier)


if __name__ == "__main__":
    unittest.main()
