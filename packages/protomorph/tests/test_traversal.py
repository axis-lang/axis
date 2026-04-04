from __future__ import annotations

import unittest
from typing import cast

from protomorph import (
    Builtin,
    Placeholder, placeholder,
    LeafCarrier, Option, Result, Spec, Tuple,
    VaryingType,
    wrap,
    deep_zip,
)


INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())
FLOAT = cast(Spec, wrap(float).fetch())


class TestDeepIter(unittest.TestCase):
    
    def test_flat_tuple(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        leaves = list(c.deep_iter())
        self.assertEqual([leaf.fetch() for leaf in leaves], [1, "a"])

    def test_nested(self):
        class Pt(Builtin):
            x: int
            y: int

        c = wrap(Pt(1, 2))
        values = [leaf.fetch() for leaf in c.deep_iter() if isinstance(leaf.fetch(), int)]
        self.assertIn(1, values)
        self.assertIn(2, values)


class TestDeepMap(unittest.TestCase):
    def test_identity(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        self.assertEqual(c.deep_map(lambda x: x).fetch(), (1, "a"))

    def test_transform_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        c = Tuple(vt, (10, 20))
        result = c.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2))
        self.assertEqual(result.fetch(), (20, 40))

    def test_transform_result_ok_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        carrier = Result.ok(Tuple(vt, (10, 20)))

        result = cast(Result, carrier.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2)))

        self.assertTrue(result.is_ok)
        self.assertEqual(result.unwrap().fetch(), (20, 40))

    def test_transform_option_some_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        carrier = Option.some(Tuple(vt, (10, 20)))

        result = cast(Option, carrier.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2)))

        self.assertTrue(result.is_some)
        self.assertEqual(result.unwrap().fetch(), (20, 40))


class TestSubst(unittest.TestCase):
    def test_varying_type_subst(self):
        T = placeholder("T")
        vt = VaryingType.of(INT, T, STR)
        c = wrap(vt)
        ph_carrier = next(leaf for leaf in c.deep_iter() if leaf.fetch() is T)
        replacement = LeafCarrier(ph_carrier.descriptor, FLOAT)
        result = c.subst({ph_carrier: replacement}).fetch()
        self.assertEqual(repr(result), repr(VaryingType.of(INT, FLOAT, STR)))


class TestSearch(unittest.TestCase):
    def test_find_leaf(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        self.assertTrue(c.search(c[1]))

    def test_find_leaf_inside_result_ok(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        inner = Tuple(vt, (1, "a"))
        carrier = Result.ok(inner)

        self.assertTrue(carrier.search(inner[1]))

    def test_find_leaf_inside_option_some(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        inner = Tuple(vt, (1, "a"))
        carrier = Option.some(inner)

        self.assertTrue(carrier.search(inner[1]))


class TestDeepZip(unittest.TestCase):
    def test_matching_structure(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        a = Tuple(vt, (1, "a"))
        b = Tuple(vt, (2, "b"))
        self.assertEqual(len(list(deep_zip(a, b))), 3)

    def test_skip(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        a = Tuple(vt, (1, "a"))
        b = Tuple(vt, (2, "b"))
        walker = deep_zip(a, b)
        results = []
        for left, right in walker:
            results.append((left, right))
            walker.skip()
        self.assertEqual(len(results), 1)

    def test_mismatch_raises(self):
        a = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a"))
        b = Tuple(cast(VaryingType, VaryingType.of(INT, FLOAT)), (2, 3.0))
        with self.assertRaises(Exception):
            list(deep_zip(a, b))


if __name__ == "__main__":
    unittest.main()
