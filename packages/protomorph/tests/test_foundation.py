from __future__ import annotations

import unittest
from typing import cast

from protomorph import Builtin, Item as Field, Id, Placeholder, SimpleVar, Spec, Type, Var, var


class TestBuiltin(unittest.TestCase):
    """Hash-consed identity for Builtin."""

    def test_consing(self):
        """Same args → same object."""
        class Pt(Builtin):
            x: int
            y: int

        a = Pt(1, 2)
        b = Pt(1, 2)
        self.assertIs(a, b)

    def test_different_args(self):
        class Pt(Builtin):
            x: int
            y: int

        self.assertIsNot(Pt(1, 2), Pt(3, 4))

    def test_immutability(self):
        class Pt(Builtin):
            x: int

        p = Pt(1)
        with self.assertRaises(AttributeError):
            p.x = 2  # type: ignore


class TestPlaceholder(unittest.TestCase):
    """Placeholder: universal stand-in, hash-consed by (context, id)."""

    def test_identity(self):
        a = var("T")
        b = var("T")
        self.assertIs(a, b)

    def test_different_id(self):
        self.assertIsNot(var("T"), var("U"))

    def test_different_context(self):
        class C(Builtin):
            x: int
        ctx = C(1)
        self.assertIsNot(var("T"), var("T", ctx=ctx))

    # def test_metatype_is_metadata_spec(self):
    #     self.assertEqual(placeholder("T").metatype(), ("T"))

    def test_arity_zero(self):
        self.assertEqual(var("T").arity, 0)

    def test_spread_placeholder(self):
        p = var("*T")
        self.assertEqual(cast(SimpleVar, p).id, "*T")

    def test_placeholder_is_var(self):
        self.assertIsInstance(var("T"), Var)


class TestField(unittest.TestCase):
    """Field is a NamedTuple(offset, key, type)."""

    def test_creation(self):
        f = Field(0, Id("x"), Spec.of("std.types.Any"))
        self.assertEqual(f.offset, 0)
        self.assertEqual(f.key, Id("x"))
        self.assertEqual(f.value, Spec.of("std.types.Any"))

    def test_no_key(self):
        f = Field(1, None, Spec.of("std.types.Any"))
        self.assertIsNone(f.key)


class TestTypeDefaults(unittest.TestCase):
    """Type base class defaults: arity=0, item_at raises, item raises."""

    def test_default_arity(self):
        self.assertEqual(Spec.of("std.types.Any").arity, 0)

    def test_item_at_raises(self):
        with self.assertRaises(IndexError):
            Spec.of("std.types.Any").item_at(0)

    def test_item_raises(self):
        with self.assertRaises(KeyError):
            Spec.of("std.types.Any").item(Id("x"))

    def test_items_empty(self):
        self.assertEqual(list(Spec.of("std.types.Any").items()), [])


if __name__ == "__main__":
    unittest.main()
