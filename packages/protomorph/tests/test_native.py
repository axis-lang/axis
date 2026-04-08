from __future__ import annotations

import unittest
from typing import cast

from protomorph import Builtin, Id, IndexedType, NATIVE_REALM, NativeObjectCarrier, NativeRealm, NativeVar, Qual, Placeholder, REALM, Spec, current_realm, var, val, spec_name


INT = cast(Spec, val(int).fetch())
STR = cast(Spec, val(str).fetch())


class Point(Builtin):
    SPEC_NAME = "test.Point"
    x: int
    y: int


class Container[T](Builtin):
    SPEC_NAME = "test.Container"
    value: T


class Pair[A, B](Builtin):
    SPEC_NAME = "test.Pair"
    first: A
    second: B


class TestWrap(unittest.TestCase):
    def test_wrap_builtin_class_returns_type_carrier(self):
        carrier = val(Point)
        self.assertIsInstance(carrier.fetch(), Spec)
        self.assertEqual(carrier.fetch(), Spec.of(spec_name(Point)))

    def test_wrap_scalar_annotation_returns_type_carrier(self):
        carrier = val(int)
        self.assertEqual(carrier.fetch(), Spec.of("std.types.Integer"))

    def test_wrap_runtime_builtin_returns_native_carrier(self):
        carrier = val(Point(1, 2))
        self.assertIsInstance(carrier, NativeObjectCarrier)
        self.assertEqual(carrier.attr(Id("x")).fetch(), 1)
        self.assertEqual(carrier.attr(Id("y")).fetch(), 2)


class TestNativeHostSchemaFor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = NativeRealm()

    def test_unknown_spec_returns_none(self):
        self.assertIsNone(self.host.schema_for(Spec.of("unknown.Thing")))

    def test_simple_class_schema(self):
        schema = cast(IndexedType, self.host.schema_for(Spec.of(spec_name(Point))))
        self.assertEqual(schema.item_at(0).value, INT)
        self.assertEqual(schema.item_at(1).value, INT)

    def test_generic_unspecialized(self):
        schema = cast(IndexedType, self.host.schema_for(Spec.of(spec_name(Container))))
        self.assertIsInstance(schema.item_at(0).value, Placeholder)
        self.assertIsInstance(schema.item_at(0).value, NativeVar)

    def test_generic_specialized(self):
        schema = cast(IndexedType, self.host.schema_for(Spec.of(spec_name(Container), INT)))
        self.assertIs(schema.item_at(0).value, INT)

    def test_pair_specialized(self):
        schema = cast(IndexedType, self.host.schema_for(Spec.of(spec_name(Pair), INT, STR)))
        self.assertIs(schema.item_at(0).value, INT)
        self.assertIs(schema.item_at(1).value, STR)


class TestDelegation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = REALM.set(NativeRealm())

    @classmethod
    def tearDownClass(cls):
        REALM.reset(cls.token)

    def test_spec_item_access_delegates_to_host(self):
        spec = Spec.of(spec_name(Point))
        self.assertEqual(spec.item_at(0).key, "x")
        self.assertEqual(spec.item(Id("y")).value, INT)

    def test_qual_item_access_is_opaque_without_derived_schema(self):
        spec = Spec.of(spec_name(Point))
        qual = Qual.of(spec, Spec.of("std.qualifiers.List"))
        with self.assertRaises(IndexError):
            qual.item_at(0)


class TestRealmContext(unittest.TestCase):
    def test_realm_context_manager_sets_current_realm(self):
        realm = NativeRealm()
        with realm:
            self.assertIs(current_realm(), realm)


if __name__ == "__main__":
    unittest.main()
