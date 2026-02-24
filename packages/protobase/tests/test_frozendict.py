import unittest

from protobase.frozendict import frozendict


class FrozenDictTest(unittest.TestCase):
    def test_immutable_operations(self) -> None:
        data = frozendict({"a": 1})
        with self.assertRaises(ValueError):
            data["b"] = 2
        with self.assertRaises(ValueError):
            del data["a"]
        with self.assertRaises(ValueError):
            data.clear()
        with self.assertRaises(ValueError):
            data.pop("a")
        with self.assertRaises(ValueError):
            data.popitem()
        with self.assertRaises(ValueError):
            data.__setattr__("x", 1)

    def test_set_update_delete(self) -> None:
        data = frozendict({"a": 1})
        updated = data.set("b", 2)
        self.assertIsInstance(updated, frozendict)
        self.assertNotEqual(data, updated)
        self.assertNotIn("b", data)

        same = data.setdefault("a", 2)
        self.assertIs(same, data)
        added = data.setdefault("b", 2)
        self.assertIn("b", added)

        deleted = updated.delete("a", updated["a"])
        self.assertNotIn("a", deleted)
        self.assertIn("a", updated)

        merged = data.update({"c": 3})
        self.assertIn("c", merged)
        self.assertNotIn("c", data)

    def test_or_and_ior(self) -> None:
        data = frozendict({"a": 1})
        merged = data | {"b": 2}
        self.assertIsInstance(merged, frozendict)
        self.assertNotIn("b", data)
        self.assertIn("b", merged)

        original = data
        data |= {"c": 3}
        self.assertIsInstance(data, frozendict)
        self.assertIn("c", original)
        self.assertIn("c", data)

    def test_hash_is_cached(self) -> None:
        data = frozendict({"a": 1, "b": 2})
        self.assertFalse(hasattr(data, "__hash_cache__"))
        first = hash(data)
        self.assertTrue(hasattr(data, "__hash_cache__"))
        self.assertEqual(first, hash(data))

    def test_hash_uses_insertion_order(self) -> None:
        one = frozendict({"a": 1, "b": 2})
        two = frozendict({"b": 2, "a": 1})
        self.assertEqual(one, two)
        self.assertNotEqual(list(one.items()), list(two.items()))
        self.assertEqual(hash(one), hash(tuple(one.items())))
        self.assertEqual(hash(two), hash(tuple(two.items())))
