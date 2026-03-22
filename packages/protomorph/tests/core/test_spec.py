"""Tests for Spec and Qual — typed references and qualified types."""
from __future__ import annotations

import sys
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Tuple
from protomorph.core.hosted import Float, Spec, Qual

from support import int_val, bare_spec


# ── Spec construction ─────────────────────────────────────────────────────────


class TestSpecConstruction(unittest.TestCase):

    def test_bare_spec_has_correct_path(self):
        s = bare_spec("my.module.Foo")
        self.assertEqual(s.path, "my.module.Foo")

    def test_bare_spec_has_empty_args(self):
        s = bare_spec("my.module.Foo")
        self.assertEqual(s.args.arity, 0)
        self.assertIs(s.args, Tuple.Empty)

    def test_spec_with_args(self):
        args = Tuple.varying_of([Integer, Text])
        s = Spec(Spec.Ground, ("test.Generic", args))
        self.assertEqual(s.path, "test.Generic")
        self.assertEqual(s.args.arity, 2)

    def test_spec_hash_consing(self):
        s1 = bare_spec("test.X")
        s2 = bare_spec("test.X")
        self.assertIs(s1, s2)

    def test_predefined_scalar_specs(self):
        # The standard scalars are Specs
        self.assertIsInstance(Integer, Spec)
        self.assertIsInstance(Text, Spec)
        self.assertIsInstance(Float, Spec)
        self.assertEqual(Integer.path, "std.Integer")
        self.assertEqual(Text.path, "std.Text")


# ── Spec structural algebra ───────────────────────────────────────────────────


class TestSpecStructuralAlgebra(unittest.TestCase):

    def test_bare_spec_is_leaf(self):
        self.assertTrue(bare_spec("test.Leaf").is_leaf)

    def test_spec_with_args_is_not_leaf(self):
        args = Tuple.varying_of([Integer])
        s = Spec(Spec.Ground, ("test.Container", args))
        self.assertFalse(s.is_leaf)

    def test_bare_spec_has_no_children(self):
        self.assertEqual(bare_spec("test.Leaf").children(), ())

    def test_spec_with_args_children_are_args_tuple(self):
        args = Tuple.varying_of([Integer, Text])
        s = Spec(Spec.Ground, ("test.Pair", args))
        children = s.children()
        self.assertEqual(len(children), 1)
        self.assertIs(children[0], args)

    def test_spec_reconstruct_no_children_returns_same(self):
        s = bare_spec("test.X")
        self.assertIs(s.reconstruct(()), s)

    def test_spec_reconstruct_with_new_args(self):
        args1 = Tuple.varying_of([Integer])
        args2 = Tuple.varying_of([Text])
        s = Spec(Spec.Ground, ("test.Box", args1))
        s2 = s.reconstruct((args2,))
        self.assertEqual(s2.path, "test.Box")
        self.assertIs(s2.args, args2)


# ── Spec.wrap ────────────────────────────────────────────────────────────────


class TestSpecWrap(unittest.TestCase):

    def test_spec_wrap_produces_hosted(self):
        from protomorph.core.hosted import Hosted
        from protomorph.core.foundation import Builtin

        class Pixel(Builtin):
            SPEC_NAME = "test.core.Pixel"
            r: int
            g: int
            b: int

        s = bare_spec("test.core.Pixel")
        pix = Pixel(r=255, g=0, b=128)
        h = s.wrap(pix)
        self.assertIsInstance(h, Hosted)
        self.assertIs(h.__meta__, s)
        self.assertIs(h.__data__, pix)


# ── Qual construction ─────────────────────────────────────────────────────────


class TestQual(unittest.TestCase):
    """
    Qual is built via _raw_meta_tuple which stores Meta objects as raw __data__.
    Accessing .underlying and .qualifiers triggers Ground.wrap(meta) → unwrap Pure
    → reconstructs the same Spec via hash-consing.  This emits a UserWarning
    (known design issue with _raw_meta_tuple).
    """

    def _list_qual(self, elem):
        from protomorph.core.native import _list_qual
        return _list_qual(elem)

    def _dict_qual(self, key, val):
        from protomorph.core.native import _dict_qual
        return _dict_qual(key, val)

    def test_list_qual_underlying_is_elem_meta(self):
        q = self._list_qual(Integer)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            underlying = q.underlying
        self.assertIs(underlying, Integer)

    def test_list_qual_qualifier_spec_path(self):
        q = self._list_qual(Integer)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            qual_spec = q.qualifiers[0]
        self.assertIsInstance(qual_spec, Spec)
        self.assertEqual(qual_spec.path, "std.qualifiers.List")

    def test_dict_qual_underlying_is_key_meta(self):
        q = self._dict_qual(Text, Integer)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            underlying = q.underlying
        self.assertIs(underlying, Text)

    def test_dict_qual_qualifier_encodes_value_type(self):
        q = self._dict_qual(Text, Integer)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            qual_spec = q.qualifiers[0]
        self.assertIsInstance(qual_spec, Spec)
        self.assertEqual(qual_spec.path, "std.qualifiers.Dict")

    def test_qual_is_leaf_when_empty(self):
        q = Qual(OMEGA, Tuple.Empty)
        self.assertTrue(q.is_leaf)

    def test_qual_not_leaf_when_has_data(self):
        q = self._list_qual(Integer)
        self.assertFalse(q.is_leaf)

    def test_underlying_access_emits_warning(self):
        """
        API note: accessing Qual.underlying triggers Ground.wrap(Pure) warning.
        This is a known consequence of _raw_meta_tuple storing Metas as raw data.
        """
        q = self._list_qual(Integer)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = q.underlying
        self.assertTrue(
            any("unwrapping __data__" in str(w.message) for w in caught),
            "Expected UserWarning about unwrapping Pure from Qual.underlying",
        )


if __name__ == "__main__":
    unittest.main()
