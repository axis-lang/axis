"""Tests for protomorph.core.foundation — OMEGA, Ground, Val, Meta."""
from __future__ import annotations

import sys
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Spec, Tuple, ground
from protomorph.core.hosted import Float
from protomorph.core.foundation import Ground
from protomorph.core.variant import Union

from support import int_val, str_val


class TestOmega(unittest.TestCase):

    def test_is_self_referential(self):
        self.assertIs(OMEGA.__meta__, OMEGA)
        self.assertIsNone(OMEGA.__data__)

    def test_is_singleton(self):
        from protomorph.core import OMEGA as again
        self.assertIs(OMEGA, again)

    def test_meta_chain_yields_only_itself(self):
        self.assertEqual(list(OMEGA.meta_chain()), [OMEGA])

    def test_is_leaf(self):
        self.assertTrue(OMEGA.is_leaf)


class TestGround(unittest.TestCase):

    def test_spec_ground_carries_spec_class(self):
        self.assertIs(Spec.Ground.__data__, Spec)

    def test_ground_meta_is_omega(self):
        self.assertIs(Spec.Ground.__meta__, OMEGA)

    def test_ground_wrap_constructs_spec(self):
        result = Spec.Ground.wrap(("test.X", Tuple.Empty))
        self.assertIsInstance(result, Spec)
        self.assertEqual(result.path, "test.X")

    def test_ground_wrap_with_pure_emits_warning_and_unwraps(self):
        existing = Spec(Spec.Ground, ("test.Y", Tuple.Empty))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = Spec.Ground.wrap(existing)
        self.assertTrue(any("unwrapping __data__" in str(w.message) for w in caught))
        self.assertIs(result, existing)

    def test_ground_factory_function(self):
        from protomorph.core.schema import UniformSchema
        g = ground(UniformSchema)
        self.assertIs(g.__data__, UniformSchema)
        self.assertIsInstance(g, Ground)


class TestHashConsing(unittest.TestCase):

    def test_same_data_returns_same_object(self):
        self.assertIs(int_val(42), int_val(42))

    def test_different_data_returns_different_objects(self):
        self.assertIsNot(int_val(1), int_val(2))

    def test_same_data_different_meta_returns_different_objects(self):
        self.assertIsNot(Integer.wrap(99), Text.wrap(99))

    def test_spec_hash_consing(self):
        s1 = Spec(Spec.Ground, ("test.Foo", Tuple.Empty))
        s2 = Spec(Spec.Ground, ("test.Foo", Tuple.Empty))
        self.assertIs(s1, s2)

    def test_spec_different_paths_are_different_objects(self):
        s1 = Spec(Spec.Ground, ("test.Foo", Tuple.Empty))
        s2 = Spec(Spec.Ground, ("test.Bar", Tuple.Empty))
        self.assertIsNot(s1, s2)


class TestMetaChain(unittest.TestCase):

    def test_scalar_val_chain(self):
        # Hosted.__meta__ = Integer (Spec)
        # Integer.__meta__ = Spec.Ground (Ground)
        # Spec.Ground.__meta__ = OMEGA
        chain = list(int_val(5).meta_chain())
        self.assertIs(chain[0], Integer)
        self.assertIs(chain[-1], OMEGA)

    def test_spec_chain(self):
        chain = list(Integer.meta_chain())
        self.assertIs(chain[0], Spec.Ground)
        self.assertIs(chain[-1], OMEGA)


class TestIsLeaf(unittest.TestCase):

    def test_scalar_is_leaf(self):
        self.assertTrue(int_val(1).is_leaf)
        self.assertTrue(str_val("hi").is_leaf)

    def test_tuple_is_not_leaf(self):
        t = Tuple.of(int_val(1), int_val(2))
        self.assertFalse(t.is_leaf)

    def test_empty_tuple_is_not_leaf(self):
        # Tuple structural contract: always non-leaf even when empty
        self.assertFalse(Tuple.Empty.is_leaf)


class TestIsSubtype(unittest.TestCase):

    def test_meta_is_subtype_of_itself(self):
        self.assertTrue(Integer.is_subtype(Integer))

    def test_meta_is_subtype_of_union_containing_it(self):
        u = Union.of(Integer, Text)
        self.assertTrue(Integer.is_subtype(u))
        self.assertTrue(Text.is_subtype(u))

    def test_meta_not_subtype_of_disjoint_union(self):
        u = Union.of(Integer, Text)
        self.assertFalse(Float.is_subtype(u))

    def test_union_is_subtype_of_wider_union(self):
        narrow = Union.of(Integer, Text)
        wide = Union.of(Integer, Text, Float)
        self.assertTrue(narrow.is_subtype(wide))

    def test_wider_union_not_subtype_of_narrower(self):
        narrow = Union.of(Integer, Text)
        wide = Union.of(Integer, Text, Float)
        self.assertFalse(wide.is_subtype(narrow))


if __name__ == "__main__":
    unittest.main()
