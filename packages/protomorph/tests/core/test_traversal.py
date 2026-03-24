from __future__ import annotations

import unittest
from typing import cast

from protomorph.core import (
    Builtin, 
    Placeholder, placeholder,
    LeafCarrier, TupleCarrier,
    VaryingType,
    wrap,
    deep_zip,
)


INT = wrap(int)
STR = wrap(str)
FLOAT = wrap(float)


class TestDeepIter(unittest.TestCase):
    
    def test_flat_tuple(self):
        vt = cast(VaryingType, VaryingType.make(INT, STR))
        c = TupleCarrier(vt, (1, "a"))
        leaves = list(c.deep_iter())
        self.assertEqual([leaf.fetch() for leaf in leaves], [1, "a"])

    def test_nested(self):
        class Pt(Builtin):
            x: int
            y: int

        c = wrap(Pt(1, 2))
        values = [leaf.fetch() for leaf in c.deep_iter()]
        self.assertIn(1, values)
        self.assertIn(2, values)


class TestDeepMap(unittest.TestCase):
    def test_identity(self):
        vt = cast(VaryingType, VaryingType.make(INT, STR))
        c = TupleCarrier(vt, (1, "a"))
        self.assertEqual(c.deep_map(lambda x: x).fetch(), (1, "a"))

    def test_transform_leaves(self):
        vt = cast(VaryingType, VaryingType.make(INT, INT))
        c = TupleCarrier(vt, (10, 20))
        result = c.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2))
        self.assertEqual(result.fetch(), (20, 40))


class TestSubst(unittest.TestCase):
    def test_varying_type_subst(self):
        T = placeholder("T")
        vt = VaryingType.make(INT, T, STR)
        c = wrap(vt)
        ph_carrier = next(leaf for leaf in c.deep_iter() if leaf.fetch() is T)
        replacement = LeafCarrier(ph_carrier.descriptor, FLOAT)
        result = c.subst({ph_carrier: replacement}).fetch()
        self.assertEqual(result, VaryingType.make(INT, FLOAT, STR))


class TestSearch(unittest.TestCase):
    def test_find_leaf(self):
        vt = cast(VaryingType, VaryingType.make(INT, STR))
        c = TupleCarrier(vt, (1, "a"))
        self.assertTrue(c.search(c[1]))


class TestDeepZip(unittest.TestCase):
    def test_matching_structure(self):
        vt = cast(VaryingType, VaryingType.make(INT, STR))
        a = TupleCarrier(vt, (1, "a"))
        b = TupleCarrier(vt, (2, "b"))
        self.assertEqual(len(list(deep_zip(a, b))), 3)

    def test_skip(self):
        vt = cast(VaryingType, VaryingType.make(INT, STR))
        a = TupleCarrier(vt, (1, "a"))
        b = TupleCarrier(vt, (2, "b"))
        walker = deep_zip(a, b)
        results = []
        for left, right in walker:
            results.append((left, right))
            walker.skip()
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
