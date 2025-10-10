import unittest

from axis import builtins

class MapTest(unittest.TestCase):
    def test_map_basic(self):
        m = builtins.Map.from_iter([('a', 1), ('b', 2), ('c', 3)])
        self.assertEqual(len(m), 3)
        self.assertEqual(m.get('a'), 1)
        self.assertEqual(m.get('b'), 2)
        self.assertEqual(m.get('c'), 3)
        with self.assertRaises(KeyError):
            m.get('d')

    def test_map_with_default(self):
        m = builtins.Map.from_iter([('a', 1), ('b', 2)])
        self.assertEqual(m.get('a', default=0), 1)
        self.assertEqual(m.get('b', default=0), 2)
        self.assertEqual(m.get('c', default=0), 0)

    def test_map_with_fallback(self):
        m = builtins.Map.from_iter([('a', 1), ('b', 2)])
        self.assertEqual(m.get('a', fallback=lambda: 0), 1)
        self.assertEqual(m.get('b', fallback=lambda: 0), 2)
        self.assertEqual(m.get('c', fallback=lambda: 0), 0)

    def test_map_map_function(self):
        m = builtins.Map.from_iter([('a', 1), ('b', 2)])
        m2 = m.map(lambda x: x * 10)
        self.assertEqual(len(m2), 2)
        self.assertEqual(m2.get('a'), 10)
        self.assertEqual(m2.get('b'), 20)

class IndexTest(unittest.TestCase):
    def test_index_basic(self):
        index = builtins.Index.from_iter(['a', 'b', None, 'c'])
        self.assertEqual(len(index), 4)
        self.assertEqual(index.get('a'), 0)
        self.assertEqual(index.get('b'), 1)
        self.assertEqual(index.get('c'), 3)
        self.assertEqual(index[0], 'a')
        self.assertEqual(index[1], 'b')
        self.assertEqual(index[2], None)
        self.assertEqual(index[3], 'c')
        with self.assertRaises(KeyError):
            index.get('d')
        with self.assertRaises(KeyError):
            index.get(None)
        with self.assertRaises(IndexError):
            index[4]

class TupleTest(unittest.TestCase):
    def test_tuple_basic(self):
        tpl = builtins.Tuple.from_iter([('a', 1), ('b', 2), (None, 3), ('c', 4)])
        self.assertEqual(len(tpl), 4)
        self.assertEqual(tpl.get('a'), 1)
        self.assertEqual(tpl.get('b'), 2)
        self.assertEqual(tpl.get('c'), 4)
        self.assertEqual(tpl[0], 1)
        self.assertEqual(tpl[1], 2)
        self.assertEqual(tpl[2], 3)
        self.assertEqual(tpl[3], 4)
        with self.assertRaises(KeyError):
            tpl.get('d')
        with self.assertRaises(KeyError):
            tpl.get(None)
        with self.assertRaises(IndexError):
            tpl[4]

        self.assertEqual(repr(tpl), "(a=1, b=2, 3, c=4)")