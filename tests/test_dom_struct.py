import unittest

from axis import dom


class IndexTest(unittest.TestCase):
    def test_index_basic(self):
        idx = dom.Struct.Index(keys=("a", None, "b"))
        self.assertEqual(idx.arity, 3)
        self.assertTrue(idx.is_sparse)
        self.assertEqual(idx._keyed_indices.get("a"), 0)
        self.assertEqual(idx._keyed_indices.get("b"), 2)

    def test_index_duplicate_keys(self):
        idx = dom.Struct.Index(keys=("a", None, "a"))
        self.assertEqual(len(idx._keyed_indices), 1)


class ShapeTest(unittest.TestCase):
    def test_shape_variants(self):
        full = dom.Struct.Shape(arity=3, keys=frozenset({"a", "b", "c"}))
        sparse = dom.Struct.Shape(arity=3, keys=frozenset({"a", "b"}))
        empty = dom.Struct.Shape(arity=3, keys=frozenset())

        self.assertTrue(full.is_full)
        self.assertFalse(full.is_sparse)
        self.assertFalse(full.is_empty)

        self.assertTrue(sparse.is_sparse)
        self.assertFalse(sparse.is_full)
        self.assertFalse(sparse.is_empty)

        self.assertTrue(empty.is_empty)
        self.assertFalse(empty.is_full)
        self.assertFalse(empty.is_sparse)


class StructTest(unittest.TestCase):
    def test_struct_new_mixed(self):
        tup = dom.Struct.new(1, 2, a=3)
        self.assertEqual(tup.index.keys, (None, None, "a"))
        self.assertEqual(tup.values, (1, 2, 3))
        self.assertEqual(tup.shape.keys, frozenset({"a"}))

    def test_struct_list_mode(self):
        tup = dom.Struct.new(1, 2, 3)
        self.assertEqual(tup.index.keys, (None, None, None))
        self.assertEqual(tup.shape.keys, frozenset())

    def test_struct_record_mode(self):
        tup = dom.Struct.new(a=1, b=2)
        self.assertEqual(tup.index.keys, ("a", "b"))
        self.assertEqual(tup.shape.keys, frozenset({"a", "b"}))

    def test_struct_equality(self):
        tup1 = dom.Struct.new(1, 2, a=3)
        tup2 = dom.Struct.new(1, 2, a=3)
        self.assertEqual(tup1, tup2)
