import unittest

from axis import dom


# class TestTuple(unittest.TestCase):
#     def test_shape(self):
#         s1 = dom.Shape(arity=3, keys=frozenset({"a", "b", "c"}))
#         s2 = dom.Shape(arity=3, keys=frozenset({"a", "b", "c"}))
#         s3 = dom.Shape(arity=3, keys=frozenset({"a", "b"}))
#         s4 = dom.Shape(arity=4, keys=frozenset({"a", "b", "c"}))

#         self.assertEqual(s1, s2)
#         self.assertNotEqual(s1, s3)
#         self.assertNotEqual(s1, s4)

#         self.assertTrue(s1.is_full)
#         self.assertFalse(s1.is_empty)
#         self.assertFalse(s1.is_sparse)

#         self.assertFalse(s3.is_full)
#         self.assertFalse(s3.is_empty)
#         self.assertTrue(s3.is_sparse)

#         self.assertFalse(s4.is_full)
#         self.assertFalse(s4.is_empty)
#         self.assertTrue(s4.is_sparse)

#     def test_index(self):
#         idx = dom.Index(keys=("a", None, "c", "d", None))
#         self.assertEqual(idx.arity, 5)
#         self.assertEqual(idx.keys, ("a", None, "c", "d", None))
#         self.assertEqual(idx._keyed_indices, {"a": 0, "c": 2, "d": 3})
#         self.assertEqual(idx._indexed_keys, {0: "a", 2: "c", 3: "d"})

#         with self.assertRaises(AssertionError):
#             dom.Index(keys=("a", None, "c", "a"))  # Duplicate key 'a'