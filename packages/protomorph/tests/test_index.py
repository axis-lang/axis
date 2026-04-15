from __future__ import annotations

import unittest
from typing import cast

from protomorph import Id, Index, IndexedType, Item, Option, Spread, Spec, Tuple, VaryingType


INT = Spec.of("std.types.Integer")
STR = Spec.of("std.types.Text")
FLOAT = Spec.of("std.types.Decimal")


class TestIndex(unittest.TestCase):
    def test_make(self):
        idx = Index.of(Id("a"), None, Id("c"))
        self.assertEqual(len(idx), 3)
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
    def test_schema_access(self):
        descriptor = cast(IndexedType, IndexedType.of(INT, y=STR))
        schema = descriptor.schema

        self.assertEqual(schema.payload_item_at(0), Item(0, None, INT))
        self.assertEqual(schema.payload_item_at(1), Item(1, Id("y"), STR))
        self.assertIs(schema.attr(Id("y")).fetch(), STR)

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
        schema = spliced.schema

        self.assertEqual(schema.payload_item_at(0).key, Id("a"))
        self.assertIsNone(schema.payload_item_at(1).key)
        self.assertIsNone(schema.payload_item_at(2).key)
        self.assertEqual(schema.payload_item_at(3).key, Id("c"))


class TestIndexElementDescriptor(unittest.TestCase):
    def test_dense_element_descriptor_is_id(self):
        idx = Index.of(Id("x"), Id("y"))
        id_spec = Spec.of("std.types.Id")
        self.assertIs(idx[0].descriptor, id_spec)
        self.assertIs(idx[1].descriptor, id_spec)

    def test_dense_element_fetch(self):
        idx = Index.of(Id("x"))
        self.assertEqual(idx[0].fetch(), Id("x"))

    def test_sparse_element_descriptor_is_optional_id(self):
        from protomorph import Qual, Option
        optional_id = Qual.of(Spec.of("std.types.Id"), Spec.of("std.qualifiers.Optional"))
        idx = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(idx[0].descriptor, optional_id)
        self.assertEqual(idx[1].descriptor, optional_id)
        self.assertEqual(idx[2].descriptor, optional_id)

    def test_sparse_none_slot_is_none_option(self):
        idx = Index.of(Id("x"), None)
        self.assertIsInstance(idx[1], Option)
        self.assertTrue(cast(Option, idx[1]).is_none)

    def test_sparse_key_slot_is_some_option(self):
        idx = Index.of(Id("x"), None)
        carrier = cast(Option, idx[0])
        self.assertIsInstance(carrier, Option)
        self.assertTrue(carrier.is_some)
        self.assertEqual(carrier.unwrap().fetch(), Id("x"))


if __name__ == "__main__":
    unittest.main()
