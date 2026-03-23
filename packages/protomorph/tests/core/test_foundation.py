from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, Id, OMEGA, Omega,
    Placeholder, placeholder,
    Field, Type,
)


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


class TestOmega(unittest.TestCase):
    """Omega is a fixed point: metatype() → itself."""

    def test_fixed_point(self):
        self.assertIs(OMEGA.metatype(), OMEGA)

    def test_is_singleton(self):
        self.assertIs(Omega(), OMEGA)

    def test_arity_zero(self):
        self.assertEqual(OMEGA.arity, 0)


class TestPlaceholder(unittest.TestCase):
    """Placeholder: universal stand-in, hash-consed by (context, id)."""

    def test_identity(self):
        a = placeholder("T")
        b = placeholder("T")
        self.assertIs(a, b)

    def test_different_id(self):
        self.assertIsNot(placeholder("T"), placeholder("U"))

    def test_different_context(self):
        class C(Builtin):
            x: int
        ctx = C(1)
        self.assertIsNot(placeholder("T"), placeholder("T", context=ctx))

    def test_metatype_is_omega(self):
        self.assertIs(placeholder("T").metatype(), OMEGA)

    def test_arity_zero(self):
        self.assertEqual(placeholder("T").arity, 0)

    def test_spread_placeholder(self):
        p = placeholder("*T")
        self.assertEqual(p.id, "*T")


class TestField(unittest.TestCase):
    """Field is a NamedTuple(offset, key, type)."""

    def test_creation(self):
        f = Field(0, Id("x"), OMEGA)
        self.assertEqual(f.offset, 0)
        self.assertEqual(f.key, Id("x"))
        self.assertIs(f.type, OMEGA)

    def test_no_key(self):
        f = Field(1, None, OMEGA)
        self.assertIsNone(f.key)


class TestTypeDefaults(unittest.TestCase):
    """Type base class defaults: arity=0, field_at raises, field raises."""

    def test_default_arity(self):
        self.assertEqual(OMEGA.arity, 0)

    def test_field_at_raises(self):
        with self.assertRaises(IndexError):
            OMEGA.field_at(0)

    def test_field_raises(self):
        with self.assertRaises(KeyError):
            OMEGA.field(Id("x"))

    def test_iter_fields_empty(self):
        self.assertEqual(list(OMEGA.iter_fields()), [])


if __name__ == "__main__":
    unittest.main()
