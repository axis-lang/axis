from __future__ import annotations

import unittest
from typing import cast

from protomorph import Builtin, Id, Placeholder, SimpleVar, Spec, Type, Var, var


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

    def test_leaf_len_raises(self):
        with self.assertRaises(TypeError):
            len(var("T"))

    def test_spread_placeholder(self):
        p = var("*T")
        self.assertEqual(cast(SimpleVar, p).id, "*T")

    def test_placeholder_is_var(self):
        self.assertIsInstance(var("T"), Var)


class TestTypeDefaults(unittest.TestCase):
    """Type base class defaults: leaf types expose no schema."""

    def test_default_is_leaf(self):
        self.assertTrue(Spec.of("std.types.Any").is_leaf)

    def test_leaf_len_raises(self):
        with self.assertRaises(TypeError):
            len(Spec.of("std.types.Any"))

    def test_leaf_iter_raises(self):
        with self.assertRaises(TypeError):
            tuple(Spec.of("std.types.Any"))


if __name__ == "__main__":
    unittest.main()
