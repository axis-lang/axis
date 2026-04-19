from __future__ import annotations

import unittest

import protomorph as pm

from protomorph import Id, LeafCarrier, Placeholder, Qual, Spec, Tuple, Uniform, var, unify, val


INT = val(int).content
STR = val(str).content
FLOAT = val(float).content


def is_var(carrier) -> bool:
    return isinstance(carrier.content, Placeholder)


class TestSpecCreation(unittest.TestCase):
    def test_of_no_args(self):
        spec = Spec.of("std.Integer")
        self.assertEqual(spec.anchor, "std.Integer")
        self.assertEqual(len(spec.args), 0)

    def test_of_with_args(self):
        spec = Spec.of("std.List", INT)
        self.assertIs(spec.args[0].content, INT)

    def test_of_multiple_args(self):
        spec = Spec.of("std.Map", INT, STR)
        self.assertIs(spec.args[0].content, INT)
        self.assertIs(spec.args[1].content, STR)


class TestSpecWrap(unittest.TestCase):
    def test_wrap_spec_exposes_anchor_and_args(self):
        carrier = val(Spec.of("std.List", INT))
        self.assertEqual(carrier[0].content, "std.List")
        self.assertEqual(carrier[1][0].content, INT)

    def test_subst_wrapped_spec(self):
        T = var("T")
        carrier = val(Spec.of("std.List", T))
        ph_leaf = next(leaf for leaf in pm.walk_leafs(carrier) if leaf.content is T)
        result = pm.walk_subst(carrier, {ph_leaf: LeafCarrier(ph_leaf.descriptor, INT)}).content
        self.assertEqual(repr(result), repr(Spec.of("std.List", INT)))


class TestQual(unittest.TestCase):
    def test_of(self):
        qual = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        self.assertEqual(qual.underlying, Spec.of("std.Integer"))
        self.assertEqual(len(qual.qualifiers), 1)

    def test_wrap_qual_is_traversable(self):
        qual = Qual.of(Spec.Integer, Spec.of("std.List", INT))
        leaves = [leaf.content for leaf in pm.walk_leafs(val(qual))]
        self.assertIn(Spec.Integer, leaves)
        self.assertIn(Spec.of("std.List", INT), leaves)

    def test_of_flattens_nested_qual(self):
        base = Qual.of(Spec.of("std.Integer"), Spec.of("std.List", INT))
        qual = Qual.of(base, Spec.of("std.qualifiers.Set"))
        self.assertEqual(qual.underlying, Spec.of("std.Integer"))
        self.assertEqual(
            [child.content for child in qual.qualifiers],
            [Spec.of("std.List", INT), Spec.of("std.qualifiers.Set")],
        )


class TestTupleSlice(unittest.TestCase):
    def test_spec_args_slice(self):
        spec = Spec.of("std.Map", INT, STR, FLOAT)
        tail = spec.args[1:]
        self.assertEqual([child.content for child in tail], [STR, FLOAT])

    def test_uniform_tuple_slice_preserves_uniform_descriptor(self):
        carrier = Tuple(Uniform(INT), (1, 2, 3))

        sliced = carrier[1:]

        self.assertIsInstance(sliced, Tuple)
        self.assertEqual([child.content for child in sliced], [2, 3])
        self.assertIsInstance(sliced.descriptor, Uniform)



if __name__ == "__main__":
    unittest.main()
