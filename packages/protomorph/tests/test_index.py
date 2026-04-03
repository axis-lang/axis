from __future__ import annotations

import unittest
from typing import cast

from protomorph import Id, Index, IndexedType, Item, Spread, Spec, Tuple, VaryingType


INT = Spec.of("std.types.Integer")
STR = Spec.of("std.types.Text")
FLOAT = Spec.of("std.types.Decimal")


class TestIndex(unittest.TestCase):
    def test_make(self):
        idx = Index.of(Id("a"), None, Id("c"))
        self.assertEqual(idx.arity, 3)
        self.assertTrue(idx.is_sparse)
        self.assertEqual(idx.key_at(0), Id("a"))
        self.assertEqual(idx.key_at(1), None)

    def test_offset_of(self):
        idx = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(idx.offset_of(Id("z")), 2)


class TestSpread(unittest.TestCase):
    def test_creation(self):
        s = Spread((1, 2, 3))
        self.assertEqual(s.values, (1, 2, 3))


class TestIndexedType(unittest.TestCase):
    def test_item_access(self):
        descriptor = cast(IndexedType, IndexedType.of(INT, y=STR))
        self.assertEqual(descriptor.item_at(0), Item(0, None, INT))
        self.assertEqual(descriptor.item_at(1), Item(1, Id("y"), STR))
        self.assertIs(descriptor.item(Id("y")).value, STR)

    def test_tuple_attr(self):
        descriptor = cast(IndexedType, IndexedType.of(INT, y=STR))
        carrier = Tuple(descriptor, (1, "hello"))
        self.assertEqual(carrier.attr(Id("y")).fetch(), "hello")

    def test_splice_resynthesizes_index(self):
        descriptor = IndexedType(
            VaryingType(cast(tuple, (INT, Spread((STR, FLOAT)), INT))),
            Index.of(Id("a"), None, Id("c")),
        )
        spliced = cast(IndexedType, descriptor.splice())
        self.assertEqual(spliced.item_at(0).key, Id("a"))
        self.assertIsNone(spliced.item_at(1).key)
        self.assertIsNone(spliced.item_at(2).key)
        self.assertEqual(spliced.item_at(3).key, Id("c"))


if __name__ == "__main__":
    unittest.main()
