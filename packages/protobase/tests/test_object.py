import unittest
from typing import Annotated, ClassVar, get_args, get_origin, TypeVar

from protobase.object import Object, attr_info_of, normalize_type, slots_of


class ObjectTest(unittest.TestCase):
    def test_attr_info_excludes_classvar(self) -> None:
        class Sample(Object):
            x: int
            y: ClassVar[int] = 1

        attrs = attr_info_of(Sample)
        self.assertEqual(set(attrs.keys()), {"x"})

    def test_default_factory_deepcopy(self) -> None:
        class Bag(Object):
            items: list[int] = []

        first = Bag()
        second = Bag()
        self.assertIsNot(first.items, second.items)
        first.items.append(1)
        self.assertEqual(second.items, [])

    def test_state_includes_attrs(self) -> None:
        class Box(Object):
            value: int

        box = Box(7)
        self.assertEqual(box.__state__(), {"value": 7})

    def test_normalize_type(self) -> None:
        type Alias = list[int]
        normalized = normalize_type(Alias)
        self.assertIs(get_origin(normalized), list)
        self.assertEqual(get_args(normalized), (int,))

        self.assertEqual(normalize_type(Annotated[int, "meta"]), int)

        T = TypeVar("T", int, str)
        self.assertIs(normalize_type(T), T)

    def test_slots_include_weakref(self) -> None:
        class Sample(Object):
            value: int

        self.assertIn("__weakref__", slots_of(Sample))
