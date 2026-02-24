import gc
import unittest

from protobase.cached_property import cached_property, slot_cached_property
from protobase.object import Object


class SlotCachedPropertyTest(unittest.TestCase):
    def test_slot_cached_property_caches_in_slot(self) -> None:
        calls = {"count": 0}

        class Box(Object):
            value: int

            @slot_cached_property
            def doubled(self) -> int:
                calls["count"] += 1
                return self.value * 2

        box = Box(3)
        self.assertEqual(box.doubled, 6)
        self.assertEqual(box.doubled, 6)
        self.assertEqual(calls["count"], 1)
        self.assertTrue(hasattr(box, "_Box__doubled"))

    def test_slot_cached_property_requires_set_name(self) -> None:
        prop = slot_cached_property(lambda self: 1)
        with self.assertRaises(TypeError):
            prop.__get__(object(), object)


class CachedPropertyTest(unittest.TestCase):
    def test_cached_property_caches(self) -> None:
        calls = {"count": 0}

        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @cached_property
            def doubled(self) -> int:
                calls["count"] += 1
                return self.value * 2

        box = Box(4)
        self.assertEqual(box.doubled, 8)
        self.assertEqual(box.doubled, 8)
        self.assertEqual(calls["count"], 1)

    def test_cached_property_requires_weakref_slot(self) -> None:
        with self.assertRaises(TypeError):

            class Bad:
                __slots__ = ("value",)

                @cached_property
                def doubled(self) -> int:
                    return 2

    def test_cached_property_does_not_keep_object_alive(self) -> None:
        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @cached_property
            def doubled(self) -> int:
                return self.value * 2

        prop = Box.doubled
        box = Box(5)
        _ = box.doubled
        self.assertEqual(len(prop._cache), 1)
        box = None
        gc.collect()
        self.assertEqual(len(prop._cache), 0)
