import copy
import unittest

from protobase.record import Consed, Inmutable, Record, mutate


class RecordTest(unittest.TestCase):
    def test_repr_omits_defaults(self) -> None:
        class Point(Record):
            x: int
            y: int = 0

        self.assertTrue(repr(Point(1)).endswith("Point(1)"))
        self.assertTrue(repr(Point(1, 2)).endswith("Point(1, y=2)"))

    def test_ordering(self) -> None:
        class Pair(Record):
            a: int
            b: int

        self.assertTrue(Pair(1, 2) < Pair(2, 0))
        self.assertTrue(Pair(2, 0) > Pair(1, 2))

    def test_copy_and_deepcopy(self) -> None:
        class Leaf(Record):
            value: int

        class Node(Record):
            leaf: Leaf

        node = Node(Leaf(3))
        shallow = copy.copy(node)
        deep = copy.deepcopy(node)
        self.assertIsNot(shallow, node)
        self.assertIsNot(deep, node)
        self.assertIsNot(shallow.leaf, node.leaf)
        self.assertIsNot(deep.leaf, node.leaf)

    def test_mutate(self) -> None:
        class Box(Record):
            value: int

        box = Box(1)
        updated = mutate(box, value=2)
        self.assertEqual(box.value, 1)
        self.assertEqual(updated.value, 2)
        self.assertIsNot(box, updated)


class InmutableRecordTest(unittest.TestCase):
    def test_structural_hash_cache(self) -> None:
        class Symbol(Inmutable):
            name: str

        sym = Symbol("x")
        self.assertFalse(hasattr(sym, "__hash_cache__"))
        first = hash(sym)
        self.assertTrue(hasattr(sym, "__hash_cache__"))
        self.assertEqual(first, hash(sym))

    def test_immutable_setattr(self) -> None:
        class Box(Inmutable):
            value: int

        box = Box(1)
        with self.assertRaises(AttributeError):
            box.value = 2


class ConsedTest(unittest.TestCase):
    def test_hash_consing(self) -> None:
        class Symbol(Consed):
            name: str

        a = Symbol("x")
        b = Symbol("x")
        c = Symbol("y")
        self.assertIs(a, b)
        self.assertIsNot(a, c)
