from __future__ import annotations

import unittest

from protomorph import Id, LeafCarrier, Placeholder, Qual, Spec, var, unify, val


INT = val(int).fetch()
STR = val(str).fetch()
FLOAT = val(float).fetch()


def is_var(carrier) -> bool:
    return isinstance(carrier.fetch(), Placeholder)


class TestSpecCreation(unittest.TestCase):
    def test_of_no_args(self):
        spec = Spec.of("std.Integer")
        self.assertEqual(spec.anchor, "std.Integer")
        self.assertEqual(len(spec.args), 0)

    def test_of_with_args(self):
        spec = Spec.of("std.List", INT)
        self.assertIs(spec.args[0].fetch(), INT)

    def test_of_multiple_args(self):
        spec = Spec.of("std.Map", INT, STR)
        self.assertIs(spec.args[0].fetch(), INT)
        self.assertIs(spec.args[1].fetch(), STR)


class TestSpecWrap(unittest.TestCase):
    def test_wrap_spec_exposes_anchor_and_args(self):
        carrier = val(Spec.of("std.List", INT))
        self.assertEqual(carrier[0].fetch(), "std.List")
        self.assertEqual(carrier[1][0].fetch(), INT)

    def test_subst_wrapped_spec(self):
        T = var("T")
        carrier = val(Spec.of("std.List", T))
        ph_leaf = next(leaf for leaf in carrier.iter_leafs() if leaf.fetch() is T)
        result = carrier.subst({ph_leaf: LeafCarrier(ph_leaf.descriptor, INT)}).fetch()
        self.assertEqual(repr(result), repr(Spec.of("std.List", INT)))


class TestQual(unittest.TestCase):
    def test_of(self):
        qual = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        self.assertEqual(qual.underlying, Spec.of("std.Integer"))
        self.assertEqual(len(qual.qualifiers), 1)

    def test_wrap_qual_is_traversable(self):
        qual = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        leaves = [leaf.fetch() for leaf in val(qual).iter_leafs()]
        self.assertIn(Spec.of("std.Integer"), leaves)
        self.assertIn(Spec.of("std.List", INT), leaves)

    def test_of_flattens_nested_qual(self):
        base = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        qual = Qual.of(base, Spec.of("std.qualifiers.Set"))
        self.assertEqual(qual.underlying, Spec.of("std.Integer"))
        self.assertEqual(
            [child.fetch() for child in qual.qualifiers],
            [Spec.of("std.List", INT), Spec.of("std.qualifiers.Set")],
        )


class TestTupleTail(unittest.TestCase):
    def test_spec_args_tail(self):
        spec = Spec.of("std.Map", INT, STR, FLOAT)
        tail = spec.args.tail
        self.assertEqual([child.fetch() for child in tail], [STR, FLOAT])


if __name__ == "__main__":
    unittest.main()
