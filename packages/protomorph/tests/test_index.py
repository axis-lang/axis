from __future__ import annotations

import unittest
from typing import cast

from protomorph import Id, Index, Indexed, Option, Spec, Tuple, Uniform, Varying


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


class TestIndexedType(unittest.TestCase):
    def test_schema_access(self):
        descriptor = cast(Indexed, Indexed.of(INT, y=STR))
        schema = descriptor.schema

        self.assertIsNone(schema.entry_at(0).key)
        self.assertIs(schema.entry_at(0).value.content, INT)
        self.assertEqual(list(schema.entries())[1].key, Id("y"))
        self.assertIs(schema.attr(Id("y")).content, STR)

    def test_tuple_attr(self):
        descriptor = cast(Indexed, Indexed.of(INT, y=STR))
        carrier = Tuple(descriptor, (1, "hello"))
        self.assertEqual(carrier.attr(Id("y")).content, "hello")

    def test_tuple_slice_preserves_indexed_descriptor(self):
        descriptor = cast(Indexed, Indexed.of(INT, y=STR, z=FLOAT))
        carrier = Tuple(descriptor, (1, "hello", 2.0))

        sliced = cast(Tuple, carrier[1:])

        self.assertEqual([child.content for child in sliced], ["hello", 2.0])
        self.assertIsInstance(sliced.descriptor, Indexed)
        self.assertEqual(cast(Indexed, sliced.descriptor).index.content, (Id("y"), Id("z")))

    def test_tuple_slice_preserves_indexed_uniform_slots(self):
        descriptor = Indexed(Uniform(INT), Index.of(Id("a"), Id("b"), Id("c")))
        carrier = Tuple(descriptor, (1, 2, 3))

        sliced = cast(Tuple, carrier[1:])

        self.assertEqual([child.content for child in sliced], [2, 3])
        self.assertIsInstance(sliced.descriptor, Indexed)
        self.assertIsInstance(cast(Indexed, sliced.descriptor).slots, Uniform)
        self.assertEqual(cast(Indexed, sliced.descriptor).index.content, (Id("b"), Id("c")))

    def test_contains_requires_shared_index_identity(self):
        index = Index.of(Id("y"))
        left = Indexed(Uniform(INT), index)
        right = Indexed(Uniform(INT), index)
        other_index = Index.of(Id("z"))
        other = Indexed(Uniform(INT), other_index)

        self.assertIn(right, left)
        self.assertNotIn(other, left)


class TestIndexElementDescriptor(unittest.TestCase):
    def test_dense_element_descriptor_is_id(self):
        idx = Index.of(Id("x"), Id("y"))
        id_spec = Spec.of("std.types.Id")
        self.assertIs(idx[0].descriptor, id_spec)
        self.assertIs(idx[1].descriptor, id_spec)

    def test_dense_element_fetch(self):
        idx = Index.of(Id("x"))
        self.assertEqual(idx[0].content, Id("x"))

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
        self.assertEqual(carrier.unwrap().content, Id("x"))

    def test_index_slice_returns_index(self):
        idx = Index.of(Id("a"), None, Id("c"))

        sliced = cast(Index, idx[1:])

        self.assertIsInstance(sliced, Index)
        self.assertEqual(sliced.content, (None, Id("c")))


class TestTupleSlices(unittest.TestCase):
    def test_varying_slice_preserves_varying_descriptor(self):
        carrier = Tuple(Varying.of(INT, STR, FLOAT), (1, "a", 2.0))

        sliced = cast(Tuple, carrier[1:])

        self.assertEqual([child.content for child in sliced], ["a", 2.0])
        self.assertIsInstance(sliced.descriptor, Varying)
        self.assertEqual(cast(Varying, sliced.descriptor).element_types, (STR, FLOAT))

    def test_uniform_slice_preserves_uniform_descriptor(self):
        carrier = Tuple(Uniform(INT), (1, 2, 3))

        sliced = cast(Tuple, carrier[1:])

        self.assertEqual([child.content for child in sliced], [2, 3])
        self.assertIsInstance(sliced.descriptor, Uniform)


if __name__ == "__main__":
    unittest.main()
