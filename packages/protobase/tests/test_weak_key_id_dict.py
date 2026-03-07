import gc
import unittest
import weakref

from protobase import Metadata, WeakKeyIdDictionary, cached_property


class EqObject:
    __slots__ = ("value", "__weakref__")

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EqObject)

    def __hash__(self) -> int:
        return 0


class WeakKeyIdDictionaryTest(unittest.TestCase):
    def test_identity_preserved(self):
        store: WeakKeyIdDictionary[EqObject, str] = WeakKeyIdDictionary()
        a = EqObject(1)
        b = EqObject(2)

        self.assertEqual(a, b)
        store[a] = "first"
        store[b] = "second"

        self.assertEqual(store[a], "first")
        self.assertEqual(store[b], "second")
        self.assertEqual(len(store), 2)

    def test_remove_if_match_guard(self):
        store: WeakKeyIdDictionary[EqObject, str] = WeakKeyIdDictionary()
        obj = EqObject(3)

        store[obj] = "initial"
        key_id = id(obj)
        old_ref = store._data[key_id][0]

        store[obj] = "updated"
        store._remove_if_match(key_id, old_ref)

        self.assertEqual(store[obj], "updated")
        self.assertEqual(len(store), 1)

    def test_cleanup_on_gc(self):
        store: WeakKeyIdDictionary[EqObject, str] = WeakKeyIdDictionary()
        obj = EqObject(4)
        store[obj] = "value"

        ref = weakref.ref(obj)
        del obj
        gc.collect()

        self.assertIsNone(ref())
        self.assertEqual(len(store), 0)


class MetadataIntegrationTest(unittest.TestCase):
    def test_metadata_identity(self):
        class Tag(Metadata[EqObject]):
            pass

        a = EqObject(1)
        b = EqObject(2)
        tag_a = Tag()
        tag_b = Tag()

        tag_a.tag(a)
        tag_b.tag(b)

        self.assertIs(Tag.of(a), tag_a)
        self.assertIs(Tag.of(b), tag_b)


class CachedPropertyIntegrationTest(unittest.TestCase):
    def test_cached_property_identity(self):
        calls = {"count": 0}

        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            def __eq__(self, other: object) -> bool:
                return isinstance(other, Box)

            def __hash__(self) -> int:
                return 0

            @cached_property
            def doubled(self) -> int:
                calls["count"] += 1
                return self.value * 2

        first = Box(2)
        second = Box(3)

        self.assertEqual(first.doubled, 4)
        self.assertEqual(second.doubled, 6)
        self.assertEqual(calls["count"], 2)

        self.assertEqual(first.doubled, 4)
        self.assertEqual(second.doubled, 6)
        self.assertEqual(calls["count"], 2)
