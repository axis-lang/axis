from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, Id, OMEGA,
    Placeholder, placeholder,
    LeafCarrier, TupleCarrier, NativeObjectCarrier,
    VaryingType, UniformType,
    INT_TYPE, STR_TYPE, FLOAT_TYPE,
    native_type, wrap,
    deep_zip,
)


class TestDeepIter(unittest.TestCase):

    def test_leaf_yields_self(self):
        c = LeafCarrier(OMEGA, 42)
        self.assertEqual(list(c.deep_iter()), [c])

    def test_flat_tuple(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = TupleCarrier(vt, (1, "a"))
        leaves = list(c.deep_iter())
        self.assertEqual(len(leaves), 2)
        self.assertEqual(leaves[0].fetch(), 1)
        self.assertEqual(leaves[1].fetch(), "a")

    def test_nested(self):
        class Pt(Builtin):
            x: int
            y: int

        c = wrap(Pt(1, 2))
        leaves = list(c.deep_iter())
        values = [l.fetch() for l in leaves]
        self.assertIn(1, values)
        self.assertIn(2, values)

    def test_custom_is_leaf(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE, FLOAT_TYPE)
        c = TupleCarrier(vt, (1, "a", 3.0))
        # Treat the first child as a non-leaf (even though it is)
        # by never considering it a leaf → it still yields because
        # is_leaf fallback to carrier's own is_leaf
        count = sum(1 for _ in c.deep_iter())
        self.assertEqual(count, 3)


class TestDeepMap(unittest.TestCase):

    def test_identity(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = TupleCarrier(vt, (1, "a"))
        result = c.deep_map(lambda x: x)
        self.assertEqual(result.fetch(), (1, "a"))

    def test_transform_leaves(self):
        vt = VaryingType.make(INT_TYPE, INT_TYPE)
        c = TupleCarrier(vt, (10, 20))
        result = c.deep_map(lambda leaf: LeafCarrier(leaf.__type__, leaf.fetch() * 2))
        self.assertEqual(result.fetch(), (20, 40))


class TestSubst(unittest.TestCase):

    def test_varying_type_subst(self):
        T = placeholder("T")
        vt = VaryingType.make(INT_TYPE, T, STR_TYPE)
        c = wrap(vt)

        # Find the placeholder leaf
        values_carrier = c[1]  # 'values' field of VaryingType/Tuple
        ph_carrier = values_carrier[1]
        self.assertIsInstance(ph_carrier.fetch(), Placeholder)

        # Substitute
        replacement = LeafCarrier(ph_carrier.__type__, FLOAT_TYPE)
        result = c.subst({ph_carrier: replacement}).fetch()

        expected = VaryingType.make(INT_TYPE, FLOAT_TYPE, STR_TYPE)
        self.assertEqual(result, expected)

    def test_subst_with_keys(self):
        T = placeholder("T")
        vt = VaryingType.make(INT_TYPE, T, z=STR_TYPE)
        c = wrap(vt)

        values_carrier = c[1]
        ph_carrier = values_carrier[1]
        replacement = LeafCarrier(ph_carrier.__type__, FLOAT_TYPE)
        result = c.subst({ph_carrier: replacement}).fetch()

        expected = VaryingType.make(INT_TYPE, FLOAT_TYPE, z=STR_TYPE)
        self.assertEqual(result, expected)

    def test_no_match_returns_same(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = wrap(vt)
        phantom = LeafCarrier(OMEGA, "phantom")
        result = c.subst({phantom: LeafCarrier(OMEGA, "replaced")}).fetch()
        self.assertEqual(result, vt)


class TestSearch(unittest.TestCase):

    def test_find_leaf(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        c = TupleCarrier(vt, (1, "a"))
        target = c[1]
        self.assertTrue(c.search(target))

    def test_not_found(self):
        vt = VaryingType.make(INT_TYPE)
        c = TupleCarrier(vt, (1,))
        phantom = LeafCarrier(OMEGA, "nope")
        self.assertFalse(c.search(phantom))


class TestDeepZip(unittest.TestCase):

    def test_matching_structure(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        a = TupleCarrier(vt, (1, "a"))
        b = TupleCarrier(vt, (2, "b"))
        pairs = list(deep_zip(a, b))
        # root pair + 2 leaf pairs
        self.assertEqual(len(pairs), 3)

    def test_skip(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        a = TupleCarrier(vt, (1, "a"))
        b = TupleCarrier(vt, (2, "b"))
        walker = deep_zip(a, b)
        results = []
        for left, right in walker:
            results.append((left, right))
            walker.skip()  # skip children of root → only root pair
        self.assertEqual(len(results), 1)

    def test_mismatched_arity(self):
        vt2 = VaryingType.make(INT_TYPE, STR_TYPE)
        vt3 = VaryingType.make(INT_TYPE, STR_TYPE, FLOAT_TYPE)
        a = TupleCarrier(vt2, (1, "a"))
        b = TupleCarrier(vt3, (1, "a", 3.0))
        pairs = list(deep_zip(a, b))
        # root pair only — arity mismatch prevents descent
        self.assertEqual(len(pairs), 1)


if __name__ == "__main__":
    unittest.main()
