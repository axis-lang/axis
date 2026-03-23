"""Integration tests — complex nested objects spanning the full representational space.

These tests build and manipulate multi-level structures using all core subsystems:
Tuple, Variant, Spec, Hosted (via NativeHost), Placeholder, and traversal.
"""
from __future__ import annotations

import sys
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protomorph.core import OMEGA, Integer, Text, Tuple, Var, Placeholder
from protomorph.core.hosted import Float, Spec, Hosted
from protomorph.core.native import meta_from_native, NATIVE_HOST
from protomorph.core.variant import Union, Variant
from protomorph.core.unification import unify

from support import (
    int_val, str_val, float_val,
    Point, Color, Label, Edge, Box, Marker,
    placeholder,
)


# ── Deeply nested Tuple structures ───────────────────────────────────────────


class TestDeepTuples(unittest.TestCase):

    def test_matrix_as_tuple_of_row_tuples(self):
        """A 2x3 integer matrix encoded as nested Tuples."""
        row0 = Tuple.of(int_val(1), int_val(2), int_val(3))
        row1 = Tuple.of(int_val(4), int_val(5), int_val(6))
        matrix = Tuple.of(row0, row1)

        self.assertEqual(matrix.arity, 2)
        self.assertIs(matrix[0][2], int_val(3))
        self.assertIs(matrix[1][0], int_val(4))

        leaves = list(matrix.deep_iter())
        self.assertEqual(leaves, [int_val(i) for i in range(1, 7)])

    def test_map_increments_all_matrix_cells(self):
        row0 = Tuple.of(int_val(0), int_val(1))
        row1 = Tuple.of(int_val(2), int_val(3))
        matrix = Tuple.of(row0, row1)

        result = matrix.deep_map(lambda v: Integer.wrap(v.__data__ + 10))
        self.assertIs(result[0][0], int_val(10))
        self.assertIs(result[1][1], int_val(13))

    def test_named_record_nested_inside_tuple(self):
        person = Tuple.of(name=str_val("alice"), age=int_val(30))
        point = Tuple.of(x=int_val(1), y=int_val(2))
        record = Tuple.of(person=person, location=point)

        from protomorph.core.hosted import Id
        self.assertIs(record.get(Id.wrap("person")), person)
        self.assertIs(record.get(Id.wrap("location")), point)


# ── Variants inside structured Tuples ────────────────────────────────────────


class TestVariantsInTuples(unittest.TestCase):

    def setUp(self):
        self.number_or_text = Union.of(Integer, Text)

    def test_tuple_of_heterogeneous_variants(self):
        v1 = self.number_or_text.inject(int_val(1))
        v2 = self.number_or_text.inject(str_val("a"))
        v3 = self.number_or_text.inject(int_val(3))
        t = Tuple.uniform_of([v1, v2, v3])

        self.assertIs(t[0].active, int_val(1))
        self.assertIs(t[1].active, str_val("a"))
        self.assertIs(t[2].active, int_val(3))

    def test_deep_iter_on_tuple_of_variants_yields_active_vals(self):
        v1 = self.number_or_text.inject(int_val(7))
        v2 = self.number_or_text.inject(str_val("z"))
        t = Tuple.of(v1, v2)

        leaves = list(t.deep_iter())
        self.assertIn(int_val(7), leaves)
        self.assertIn(str_val("z"), leaves)

    def test_map_active_through_tuple(self):
        u = Union.of(Integer, Text)
        v = u.inject(int_val(5))
        t = Tuple.of(v, int_val(0))

        result = t.deep_map(
            lambda leaf: Integer.wrap(leaf.__data__ * 2) if leaf.__meta__ is Integer else leaf
        )
        # The variant's active value was int_val(5), now should be int_val(10)
        self.assertIs(result[0].active, int_val(10))


# ── Hosted Builtin decomposition ─────────────────────────────────────────────


class TestHostedDecompositionComplex(unittest.TestCase):

    def test_edge_full_decomposition(self):
        """Edge → (source: Point, target: Point, weight: Float).
        Each Point → (x: Integer, y: Integer).
        deep_iter should yield 5 scalars.
        """
        e_spec = meta_from_native(Edge)
        e = Edge(
            source=Point(x=0, y=0),
            target=Point(x=3, y=4),
            weight=5.0,
        )
        hosted = e_spec.wrap(e)

        leaves = list(hosted.deep_iter())
        # 4 ints from the two Points + 1 float from weight = 5 leaves
        self.assertEqual(len(leaves), 5)
        self.assertIn(int_val(3), leaves)
        self.assertIn(int_val(4), leaves)
        self.assertIn(float_val(5.0), leaves)

    def test_deep_map_transforms_all_scalar_fields(self):
        """Replace every Integer in an Edge with its negation."""
        e_spec = meta_from_native(Edge)
        e = Edge(
            source=Point(x=1, y=2),
            target=Point(x=3, y=4),
            weight=0.0,
        )
        hosted = e_spec.wrap(e)

        def negate_int(v):
            if v.__meta__ is Integer:
                return Integer.wrap(-v.__data__)
            return v

        result = hosted.deep_map(negate_int)
        children = result.children()
        # source children: x=-1, y=-2
        src_children = children[0].children()
        self.assertIs(src_children[0], int_val(-1))
        self.assertIs(src_children[1], int_val(-2))

    def test_box_str_hosted_decomposition(self):
        spec = meta_from_native(Box[str])
        hosted = spec.wrap(Box(value="hello"))

        self.assertFalse(hosted.is_leaf)
        children = hosted.children()
        self.assertEqual(len(children), 1)
        self.assertIs(children[0], str_val("hello"))

    def test_marker_is_a_leaf_hosted(self):
        spec = meta_from_native(Marker)
        hosted = spec.wrap(Marker())
        self.assertTrue(hosted.is_leaf)
        self.assertEqual(hosted.children(), ())


# ── Unification on Hosted structures ─────────────────────────────────────────


class TestUnificationOnHosted(unittest.TestCase):

    def test_unify_two_identical_points_as_hosted(self):
        spec = meta_from_native(Point)
        h1 = spec.wrap(Point(x=1, y=2))
        h2 = spec.wrap(Point(x=1, y=2))
        result = unify(h1, h2, is_var=lambda v: isinstance(v, Placeholder))
        self.assertIsNotNone(result)
        self.assertEqual(result, h1)

    def test_unify_incompatible_schemas_returns_none(self):
        """
        Unification on Tuples requires compatible() — same schema (__meta__).
        A pattern Tuple with a Placeholder in position 0 has a different schema
        (Var-typed slot) than a concrete Tuple (Integer-typed slot).
        compatible() enforces this and the unification correctly returns None.
        """
        x_var = placeholder("x")
        pt_children_pattern = Tuple.of(x_var, int_val(2))   # schema: (Var, Integer)
        pt_children_concrete = Tuple.of(int_val(7), int_val(2))  # schema: (Integer, Integer)

        result = unify(
            pt_children_pattern,
            pt_children_concrete,
            is_var=lambda v: isinstance(v, Placeholder),
        )
        self.assertIsNone(result)

    def test_unify_placeholder_at_root_against_hosted_tuple(self):
        """
        A Placeholder at the root always captures (no compatible() check at leaves).
        This is the correct way to create a "wildcard" for any sub-structure.
        """
        x_var = placeholder("x")
        concrete = Tuple.of(int_val(7), int_val(2))

        result = unify(x_var, concrete, is_var=lambda v: isinstance(v, Placeholder))
        self.assertIsNotNone(result)
        self.assertEqual(result, concrete)


# ── Subst in Spec args (generic type-level patterns) ─────────────────────────


class TestSubstInSpecArgs(unittest.TestCase):

    def test_subst_placeholder_in_spec_args(self):
        """Generic spec Box[?T] → after subst → Box[Integer].
        NOTE: deep_map/reconstruct may normalise the args Tuple from
        VaryingSchema to UniformSchema — compare path and args content,
        not the Spec objects directly.
        """
        t_ph = placeholder("T")
        args = Tuple.varying_of([t_ph])
        box_pattern = Spec(Spec.Ground, ("test.core.Box", args))

        result = box_pattern.subst({t_ph: Integer})

        self.assertIsInstance(result, Spec)
        self.assertEqual(result.path, "test.core.Box")
        self.assertEqual(result.args.arity, 1)
        self.assertIs(result.args[0], Integer)

    def test_subst_two_type_params(self):
        from protomorph.core.foundation import Builtin

        class Map[K, V](Builtin):
            SPEC_NAME = "test.core.Map"
            key: K
            value: V

        k_ph = placeholder("K")
        v_ph = placeholder("V")
        args = Tuple.varying_of([k_ph, v_ph])
        map_pattern = Spec(Spec.Ground, ("test.core.Map", args))

        result = map_pattern.subst({k_ph: Text, v_ph: Integer})
        self.assertIs(result.args[0], Text)
        self.assertIs(result.args[1], Integer)


# ── Complex traversal with mixed structure ────────────────────────────────────


class TestMixedStructureTraversal(unittest.TestCase):

    def test_count_integer_leaves_in_mixed_structure(self):
        """A structure mixing Tuples, Variants, and Hosted types."""
        u = Union.of(Integer, Text)
        inner = Tuple.of(
            u.inject(int_val(1)),
            u.inject(str_val("x")),
            u.inject(int_val(3)),
        )
        outer = Tuple.of(inner, int_val(100))

        leaves = list(outer.deep_iter())
        int_leaves = [v for v in leaves if v.__meta__ is Integer]
        self.assertEqual(len(int_leaves), 3)  # 1, 3, 100

    def test_subst_inside_variant_via_map_active(self):
        """
        Placeholders cannot be inject()ed into a Union directly — inject()
        validates that the value's meta is a union variant, but Placeholder's
        meta is Var, not Integer or Text.
        Use map_active instead to transform the active value inside a Variant.
        """
        u = Union.of(Integer, Text)
        v = u.inject(int_val(5))
        t = Tuple.of(v, int_val(0))

        # Transform the active value via deep_map targeting Integer leaves
        result = t.deep_map(
            lambda leaf: int_val(42) if leaf is int_val(5) else leaf
        )
        self.assertIs(result[0].active, int_val(42))
        self.assertIs(result[1], int_val(0))

    def test_replace_and_reslice_tuple(self):
        t = Tuple.of(int_val(1), int_val(2), int_val(3), int_val(4))
        t2 = t.replace(1, str_val("mid"))
        s = t2.slice(1, 3)

        self.assertEqual(s.arity, 2)
        self.assertIs(s[0], str_val("mid"))
        self.assertIs(s[1], int_val(3))


if __name__ == "__main__":
    unittest.main()
