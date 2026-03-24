from __future__ import annotations

import unittest

from protomorph.core import (
    Anchor, 
    Placeholder, placeholder,
    LeafCarrier,
    VaryingType,
    AnchorType, Spec, Qual, ANCHOR_TYPE,
    unify, wrap,
)


INT = wrap(int)
STR = wrap(str)
FLOAT = wrap(float)


def is_var(c) -> bool:
    return isinstance(c.fetch(), Placeholder)


class TestSpecCreation(unittest.TestCase):
    def test_of_no_args(self):
        s = Spec.of("std.Integer")
        self.assertEqual(s.anchor, Anchor("std.Integer"))
        self.assertEqual(len(list(s.args)), 0)

    def test_of_with_args(self):
        s = Spec.of("std.List", INT)
        self.assertEqual(s.args[0].fetch(), INT)

    def test_of_multiple_args(self):
        s = Spec.of("std.Map", INT, STR)
        self.assertEqual(s.args[0].fetch(), INT)
        self.assertEqual(s.args[1].fetch(), STR)


class TestSpecAsCarrier(unittest.TestCase):
    def test_deep_iter_no_args(self):
        s = Spec.of("std.Integer")
        leaves = [l.fetch() for l in s.deep_iter()]
        self.assertIn(Anchor("std.Integer"), leaves)

    def test_deep_iter_with_args(self):
        s = Spec.of("std.List", INT)
        leaves = [l.fetch() for l in s.deep_iter()]
        self.assertIn(INT, leaves)

    def test_reconstruct(self):
        s = Spec.of("std.List", INT)
        r = s.reconstruct(tuple(s))
        self.assertEqual(r.fetch(), s.fetch())

    def test_len(self):
        s = Spec.of("std.Map", INT, STR)
        self.assertEqual(len(s), 3)


class TestSpecAsType(unittest.TestCase):
    def test_metatype_is_metadata_spec(self):
        s = Spec.of("std.Integer")
        self.assertEqual(s.metatype(), Spec.of("std.metas.Specialization"))

    def test_make_produces_leaf(self):
        s = Spec.of("std.Integer")
        c = s.make(42)
        self.assertIsInstance(c, LeafCarrier)
        self.assertEqual(c.fetch(), 42)
        self.assertIs(c.descriptor, s)


class TestSpecSubst(unittest.TestCase):
    def test_subst_placeholder_in_args(self):
        T = placeholder("T")
        s = Spec.of("std.List", T)
        ph_leaf = next(l for l in s.deep_iter() if l.fetch() is T)
        result = s.subst({ph_leaf: LeafCarrier(ph_leaf.descriptor, INT)})
        self.assertEqual(result, Spec.of("std.List", INT))


class TestSpecUnify(unittest.TestCase):
    def test_unify_captures_arg(self):
        T = placeholder("T")
        pattern = Spec.of("std.List", T)
        concrete = Spec.of("std.List", INT)
        result = unify(pattern, concrete, is_var=lambda it: it.content is T)
        self.assertEqual(result, concrete)

    def test_unify_different_anchors_fails(self):
        T = placeholder("T")
        a = Spec.of("std.List", T)
        b = Spec.of("std.Set", INT)
        self.assertIsNone(unify(a, b, is_var=is_var))


class TestQualCreation(unittest.TestCase):
    def test_of(self):
        integer = Spec.of("std.Integer")
        list_q = Spec.of("std.List", INT)
        q = Qual.of(integer, list_q)
        self.assertIs(q.underlying, integer)
        self.assertEqual(len(q), 2)

    def test_qualifiers(self):
        integer = Spec.of("std.Integer")
        list_q = Spec.of("std.List", INT)
        q = Qual.of(integer, list_q)
        self.assertEqual(q.qualifiers, (list_q,))


class TestQualAsCarrier(unittest.TestCase):
    def test_deep_iter(self):
        q = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        self.assertTrue(list(q.deep_iter()))

    def test_subst(self):
        T = placeholder("T")
        q = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", T))
        ph_leaf = next(l for l in q.deep_iter() if l.fetch() is T)
        result = q.subst({ph_leaf: LeafCarrier(ph_leaf.descriptor, INT)})
        self.assertEqual(result, Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT)))


class TestQualAsType(unittest.TestCase):
    def test_metatype_is_metadata_spec(self):
        self.assertEqual(
            Qual.of(Spec.of("std.Integer")).metatype(),
            Spec.of("std.metas.Qualifier"),
        )

    def test_make_delegates_to_underlying(self):
        spec = Spec.of("std.Integer")
        q = Qual.of(spec)
        c = q.make(42)
        self.assertIsInstance(c, LeafCarrier)
        self.assertIs(c.descriptor, spec)


class TestTupleHeadTail(unittest.TestCase):
    def test_varying_type_tail(self):
        vt = VaryingType.make(INT, STR, FLOAT)
        tail = vt.tail
        self.assertEqual(tail.values, (STR, FLOAT))


class TestAnchorType(unittest.TestCase):
    def test_spec_schema_uses_special_anchor_type(self):
        spec = Spec.of("std.Integer")
        self.assertIsInstance(spec.descriptor.item_at(0).value, AnchorType)

    def test_anchor_type_is_leaf_descriptor(self):
        c = ANCHOR_TYPE.make("std.Integer")
        self.assertIsInstance(ANCHOR_TYPE, Spec)
        self.assertIsInstance(ANCHOR_TYPE.descriptor.item_at(0).value, AnchorType)
        self.assertIsInstance(c, LeafCarrier)
        self.assertEqual(c.fetch(), "std.Integer")

    def test_anchor_type_make_returns_leaf_carrier(self):
        anchor_type = AnchorType()
        carrier = anchor_type.make("std.Integer")
        self.assertIsInstance(carrier, LeafCarrier)
        self.assertEqual(carrier.fetch(), "std.Integer")


if __name__ == "__main__":
    unittest.main()
