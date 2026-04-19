from __future__ import annotations

import unittest
from typing import cast

import protomorph as pm
from protomorph import Builtin
from protomorph.core.types.shape import _shape_intersection


INT = pm.types.integer
STR = pm.types.text


class Pair(Builtin):
    SPEC_NAME = "test.shape.Pair"
    left: int
    right: str


class PolyPair(Builtin):
    SPEC_NAME = "test.shape.PolyPair"
    left: int | str
    right: str


class TestShape(unittest.TestCase):
    def test_collapsed_leaf_schema_is_single_slot(self):
        shape = pm.types.Shape.collapsed(INT)

        self.assertEqual(shape.schema.content, (INT,))
        self.assertFalse(shape.is_expanded)

    def test_collapsed_structured_schema_is_single_slot(self):
        point = pm.types.named("test.shape.Pair")
        shape = pm.types.Shape.collapsed(point)

        self.assertEqual(shape.schema.content, (point,))

    def test_expanded_schema_flattens_child_schemas(self):
        pair = pm.types.named("test.shape.Pair")
        shape = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )

        self.assertEqual(shape.schema.content, (INT, STR))
        self.assertTrue(shape.is_expanded)

    def test_expanded_shape_requires_active_schema(self):
        with self.assertRaises(AssertionError):
            pm.types.Shape.expanded(INT, pm.types.Shape.collapsed(INT))

    def test_expanded_shape_requires_matching_part_count(self):
        pair = pm.types.named("test.shape.Pair", INT, STR)

        with self.assertRaises(AssertionError):
            pm.types.Shape.expanded(pair, pm.types.Shape.collapsed(INT))

    def test_union_backed_shape_must_stay_collapsed(self):
        either = pm.types.union(INT, STR)

        with self.assertRaises(AssertionError):
            pm.types.Shape.expanded(
                either,
                pm.types.Shape.collapsed(INT),
            )

    def test_collapsed_shape_contains_matching_expanded_shape(self):
        pair = pm.types.named("test.shape.Pair")
        general = pm.types.Shape.collapsed(pair)
        specific = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )

        self.assertIn(specific, general)

    def test_expanded_shape_does_not_contain_collapsed_shape(self):
        pair = pm.types.named("test.shape.Pair")
        general = pm.types.Shape.collapsed(pair)
        specific = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )

        self.assertNotIn(general, specific)

    def test_expanded_shape_allows_union_refinement_in_slot(self):
        pair = pm.types.named("test.shape.PolyPair")

        shape = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )

        assert shape.parts is not None
        self.assertEqual(shape.parts[0].active, INT)

    def test_shape_intersection_prefers_collapsed_cover(self):
        pair = pm.types.named("test.shape.Pair")
        collapsed = pm.types.Shape.collapsed(pair)
        expanded = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )

        self.assertIs(_shape_intersection(collapsed, expanded), collapsed)

    def test_shape_intersection_recurses_on_shared_active(self):
        pair = pm.types.named("test.shape.PolyPair")
        left = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(INT),
            pm.types.Shape.collapsed(STR),
        )
        right = pm.types.Shape.expanded(
            pair,
            pm.types.Shape.collapsed(STR),
            pm.types.Shape.collapsed(STR),
        )

        merged = _shape_intersection(left, right)

        self.assertTrue(merged.is_expanded)
        self.assertEqual(merged.active, pair)
        assert merged.parts is not None
        self.assertEqual(
            cast(pm.Union, merged.parts[0].active).variants,
            frozenset({INT, STR}),
        )
        self.assertIs(merged.parts[1].active, STR)

    def test_shape_intersection_collapses_different_actives(self):
        left = pm.types.Shape.collapsed(INT)
        right = pm.types.Shape.collapsed(STR)

        merged = _shape_intersection(left, right)

        self.assertFalse(merged.is_expanded)
        self.assertEqual(
            cast(pm.Union, merged.active).variants,
            frozenset({INT, STR}),
        )


if __name__ == "__main__":
    unittest.main()
