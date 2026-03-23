from __future__ import annotations

import unittest

from protomorph.core import (
    Id, Index, EMPTY_INDEX, Spread, Tuple,
)


class TestIndex(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(len(EMPTY_INDEX), 0)
        self.assertEqual(list(EMPTY_INDEX), [])

    def test_make(self):
        idx = Index.make("a", "b", "c")
        self.assertEqual(len(idx), 3)
        self.assertEqual(idx[0], "a")
        self.assertEqual(idx[2], "c")

    def test_contains(self):
        idx = Index.make("a", "b")
        self.assertIn("a", idx)
        self.assertNotIn("z", idx)

    def test_offset_of(self):
        idx = Index.make("x", "y", "z")
        self.assertEqual(idx.offset_of("y"), 1)

    def test_consing(self):
        a = Index(("a", "b"))
        b = Index(("a", "b"))
        self.assertIs(a, b)


class TestTuple(unittest.TestCase):

    def test_make_positional(self):
        t = Tuple.make(10, 20, 30)
        self.assertEqual(len(t), 3)
        self.assertEqual(t[0], 10)
        self.assertEqual(t[1], 20)
        self.assertEqual(t[2], 30)
        self.assertIs(t.index, EMPTY_INDEX)

    def test_make_keyword(self):
        t = Tuple.make(x=1, y=2)
        self.assertEqual(len(t), 2)
        self.assertEqual(t[Id("x")], 1)
        self.assertEqual(t[Id("y")], 2)

    def test_make_mixed(self):
        t = Tuple.make(1, 2, z=3)
        self.assertEqual(len(t), 3)
        self.assertEqual(t[0], 1)
        self.assertEqual(t[1], 2)
        self.assertEqual(t[Id("z")], 3)

    def test_iter(self):
        t = Tuple.make(10, 20)
        self.assertEqual(list(t), [10, 20])

    def test_contains(self):
        t = Tuple.make(10, 20)
        self.assertIn(10, t)
        self.assertNotIn(99, t)

    def test_items(self):
        t = Tuple.make(x=1, y=2)
        items = list(t.items())
        self.assertEqual(items, [(Id("x"), 1), (Id("y"), 2)])

    def test_consing(self):
        a = Tuple.make(1, 2, 3)
        b = Tuple.make(1, 2, 3)
        self.assertIs(a, b)


class TestSpread(unittest.TestCase):

    def test_creation(self):
        s = Spread((1, 2, 3))
        self.assertEqual(s.values, (1, 2, 3))

    def test_consing(self):
        self.assertIs(Spread((1, 2)), Spread((1, 2)))


class TestSplice(unittest.TestCase):

    def test_no_spread_returns_self(self):
        t = Tuple.make(1, 2, 3)
        self.assertIs(t.splice(), t)

    def test_splice_middle(self):
        t = Tuple(EMPTY_INDEX, (10, Spread((20, 30)), 40))
        result = t.splice()
        self.assertEqual(list(result), [10, 20, 30, 40])

    def test_splice_preserves_keys(self):
        idx = Index((Id("a"), None, Id("c")))
        t = Tuple(idx, (1, Spread((2, 3)), 4))
        result = t.splice()
        self.assertEqual(list(result), [1, 2, 3, 4])
        # 'a' preserved, spread positions get None, 'c' preserved
        self.assertEqual(result.index.keys[0], Id("a"))
        self.assertIsNone(result.index.keys[1])
        self.assertIsNone(result.index.keys[2])
        self.assertEqual(result.index.keys[3], Id("c"))

    def test_splice_empty_spread(self):
        t = Tuple(EMPTY_INDEX, (1, Spread(()), 2))
        result = t.splice()
        self.assertEqual(list(result), [1, 2])


if __name__ == "__main__":
    unittest.main()
