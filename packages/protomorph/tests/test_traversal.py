from __future__ import annotations

import unittest
from typing import Any, cast

import protomorph as pm
from protobase import frozendict

from protomorph import (
    Builtin,
    Placeholder, var,
    Morph, Pattern, Shape, Wildcard,
    LeafCarrier, Option, Result, Spec, Tuple, Val,
    VaryingType,
    val,
    deep_zip,
)


INT = cast(Spec, val(int).fetch())
STR = cast(Spec, val(str).fetch())
FLOAT = cast(Spec, val(float).fetch())


class TraversalPoint(Builtin):
    x: int
    y: int


class TraversalWeight(Builtin):
    amount: int


class TraversalEdge(Builtin):
    left: TraversalPoint
    weight: TraversalWeight
    right: int


class LatticeBranchA(Builtin):
    value: int


class LatticeBranchB(Builtin):
    value: int


class LatticeNode(Builtin):
    left: Val
    right: Val


class MatchA(Builtin):
    left: Val
    right: Val


class MatchB(Builtin):
    left: Val
    right: Val


class MatchQ(Builtin):
    left: Val
    right: Val


class MatchPair(Builtin):
    left: Val
    right: Val


class TestIter(unittest.TestCase):
    def test_yields_root_then_children_pre_order(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        nodes = list(c.iter())
        # pre-order: root first, then its children left-to-right
        self.assertIs(nodes[0], c)
        self.assertEqual([n.fetch() for n in nodes[1:]], [1, "a"])

    def test_pure_leaf_yields_only_self(self):
        leaf = LeafCarrier(INT, 42)
        nodes = list(leaf.iter())
        self.assertEqual(len(nodes), 1)
        self.assertIs(nodes[0], leaf)

    def test_nested_pre_order(self):
        inner = Tuple(cast(VaryingType, VaryingType.of(INT, INT)), (1, 2))
        outer_t = cast(VaryingType, VaryingType.of(inner.descriptor, INT))
        outer = Tuple(outer_t, (inner, 3))
        nodes = list(outer.iter())
        # outer, inner, 1, 2, 3
        self.assertIs(nodes[0], outer)
        self.assertIs(nodes[1], inner)
        self.assertEqual([n.fetch() for n in nodes[2:]], [1, 2, 3])


class TestValFlags(unittest.TestCase):
    def test_wildcard_flag(self):
        self.assertTrue(Wildcard.is_wildcard)
        self.assertFalse(val(42).is_wildcard)


class TestIterLeafs(unittest.TestCase):
    def test_flat_tuple(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        leaves = list(c.iter_leafs())
        self.assertEqual([leaf.fetch() for leaf in leaves], [1, "a"])

    def test_nested(self):
        class Pt(Builtin):
            x: int
            y: int

        c = val(Pt(1, 2))
        values = [leaf.fetch() for leaf in c.iter_leafs() if isinstance(leaf.fetch(), int)]
        self.assertIn(1, values)
        self.assertIn(2, values)

    def test_pure_leaf_yields_self(self):
        leaf = LeafCarrier(INT, 42)
        self.assertEqual([n.fetch() for n in leaf.iter_leafs()], [42])


class TestIterBranches(unittest.TestCase):
    def test_flat_tuple_yields_only_root(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        branches = list(c.iter_branches())
        self.assertEqual(len(branches), 1)
        self.assertIs(branches[0], c)

    def test_nested_pre_order(self):
        inner = Tuple(cast(VaryingType, VaryingType.of(INT, INT)), (1, 2))
        outer_t = cast(VaryingType, VaryingType.of(inner.descriptor, INT))
        outer = Tuple(outer_t, (inner, 3))
        branches = list(outer.iter_branches())
        # pre-order: outer before inner; leaves (1, 2, 3) excluded
        self.assertEqual(branches, [outer, inner])

    def test_pure_leaf_yields_nothing(self):
        leaf = LeafCarrier(INT, 42)
        self.assertEqual(list(leaf.iter_branches()), [])


class TestDeepMap(unittest.TestCase):
    def test_identity(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        self.assertEqual(c.deep_map(lambda x: x).fetch(), (1, "a"))

    def test_transform_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        c = Tuple(vt, (10, 20))
        result = c.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2))
        self.assertEqual(result.fetch(), (20, 40))

    def test_transform_result_ok_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        carrier = Result.ok(Tuple(vt, (10, 20)))

        result = cast(Result, carrier.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2)))

        self.assertTrue(result.is_ok)
        self.assertEqual(result.unwrap().fetch(), (20, 40))

    def test_transform_option_some_leaves(self):
        vt = cast(VaryingType, VaryingType.of(INT, INT))
        carrier = Option.some(Tuple(vt, (10, 20)))

        result = cast(Option, carrier.deep_map(lambda leaf: LeafCarrier(leaf.descriptor, leaf.fetch() * 2)))

        self.assertTrue(result.is_some)
        self.assertEqual(result.unwrap().fetch(), (20, 40))


class TestUnnest(unittest.TestCase):
    def test_unnest_pattern_over_builtin(self):
        x = var("X", int)
        y = var("Y", int)
        sample = val(TraversalEdge(TraversalPoint(cast(int, x), 2), TraversalWeight(1), cast(int, y)))
        pattern = Pattern.from_val(sample)

        unnested_pattern = pm.canonical.unnest(pattern)

        self.assertEqual(len(unnested_pattern), 3)
        self.assertEqual(
            [repr(branch) for branch in unnested_pattern.values()],
            [
                "TraversalEdge(left=@1, weight=@2, right=#3)",
                "TraversalPoint(x=#0, y=#1)",
                "TraversalWeight(amount=#2)",
            ],
        )


class TestShape(unittest.TestCase):
    def test_shape_is_pure_projection_of_pattern(self):
        x = var("X", int)
        y = var("Y", int)
        sample = val(TraversalEdge(TraversalPoint(cast(int, x), 2), TraversalWeight(1), cast(int, y)))

        pattern = Pattern.from_val(sample)
        shape = pattern.shape

        self.assertEqual(
            repr(shape.pattern),
            "TraversalEdge(left=TraversalPoint(x=_, y=_), weight=TraversalWeight(amount=_), right=_)",
        )
        self.assertEqual(repr(pattern.shape.pattern), repr(shape.pattern))

    def test_shape_specialization_and_meet(self):
        general = Shape.from_val(val(LatticeNode(val(1), val(2))))
        left_specific = Shape.from_val(val(LatticeNode(val(LatticeBranchA(1)), val(2))))
        right_specific = Shape.from_val(val(LatticeNode(val(1), val(LatticeBranchB(2)))))
        incompatible = Shape.from_val(val(LatticeNode(val(LatticeBranchB(1)), val(2))))

        self.assertTrue(general.specializes(general))
        self.assertTrue(left_specific.specializes(general))
        self.assertTrue(general.generalizes(left_specific))
        self.assertEqual(pm.canonical.relation(left_specific, general), pm.Relation.CONTRACTS)
        self.assertEqual(pm.canonical.relation(general, left_specific), pm.Relation.EXPANDS)
        self.assertEqual(pm.canonical.relation(left_specific, right_specific), pm.Relation.REFRAMES)
        self.assertEqual(pm.canonical.relation(left_specific, incompatible), pm.Relation.DISJOINT)
        self.assertTrue(left_specific.compatible_with(right_specific))
        self.assertFalse(left_specific.compatible_with(incompatible))

        meet = left_specific.meet(right_specific)
        self.assertIsNotNone(meet)
        self.assertEqual(repr(cast(Shape, right_specific.meet(left_specific)).pattern), repr(cast(Shape, meet).pattern))
        self.assertEqual(
            repr(cast(Shape, meet).pattern),
            "LatticeNode(left=LatticeBranchA(value=_), right=LatticeBranchB(value=_))",
        )


class TestCanonicalMatch(unittest.TestCase):
    def test_match_projects_common_slots_and_nests(self):
        x = var("X", Any)
        y = var("Y", Any)
        u = var("U", Any)
        v = var("V", Any)

        left_pattern = Pattern.from_val(
            val(MatchQ(val(MatchA(val(1), val(2))), val(3)))
        )
        right_pattern = Pattern.from_val(
            val(MatchQ(val(1), val(MatchB(val(2), val(3)))))
        )

        left = Morph(
            pattern=left_pattern,
            bindings=frozendict({
                left_pattern.slots[0]: val(x),
                left_pattern.slots[1]: val(y),
                left_pattern.slots[2]: val(MatchB(val(u), val(v))),
            }),
        )
        right = Morph(
            pattern=right_pattern,
            bindings=frozendict({
                right_pattern.slots[0]: val(MatchA(val(x), val(y))),
                right_pattern.slots[1]: val(u),
                right_pattern.slots[2]: val(v),
            }),
        )

        matched = pm.canonical.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertTrue(pm.canonical.compatible(left, right))
        self.assertEqual(repr(cast(Pattern, pm.canonical.meet(left, right)).pattern), repr(matched.common.pattern))
        self.assertEqual(
            repr(matched.common.pattern),
            "MatchQ(left=MatchA(left=#0, right=#1), right=MatchB(left=#2, right=#3))",
        )
        self.assertEqual(
            [repr(matched.left.bindings[slot]) for slot in left_pattern.slots],
            ["#0", "#1", "@2"],
        )
        self.assertEqual(
            [repr(matched.right.bindings[slot]) for slot in right_pattern.slots],
            ["@1", "#2", "#3"],
        )

    def test_match_detects_repeated_slot_conflict(self):
        x = var("X", Any)

        left = Morph.from_val(val(MatchPair(val(x), val(x))))
        right = Morph.from_val(val(MatchPair(val(1), val(2))))

        self.assertIsNone(pm.canonical.match(left, right))

    def test_match_preserves_shared_leaf_in_common_pattern(self):
        x = var("X", Any)
        y = var("Y", Any)
        z = var("Z", Any)

        left = Morph.from_val(val(MatchPair(val(x), val(x))))
        right = Morph.from_val(val(MatchPair(val(y), val(z))))

        matched = pm.canonical.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(repr(matched.common.pattern), "MatchPair(left=#0, right=#0)")
        self.assertEqual(
            [repr(matched.right.bindings[slot]) for slot in right.pattern.slots],
            ["#0", "#0"],
        )

class TestSubst(unittest.TestCase):
    def test_varying_type_subst(self):
        T = var("T", int)
        vt = VaryingType.of(INT, T, STR)
        c = val(vt)
        ph_carrier = next(leaf for leaf in c.iter_leafs() if leaf.fetch() is T)
        replacement = LeafCarrier(ph_carrier.descriptor, FLOAT)
        result = c.subst({ph_carrier: replacement}).fetch()
        self.assertEqual(repr(result), repr(VaryingType.of(INT, FLOAT, STR)))


class TestSearch(unittest.TestCase):
    def test_find_leaf(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        c = Tuple(vt, (1, "a"))
        self.assertTrue(c.search(c[1]))

    def test_find_leaf_inside_result_ok(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        inner = Tuple(vt, (1, "a"))
        carrier = Result.ok(inner)

        self.assertTrue(carrier.search(inner[1]))

    def test_find_leaf_inside_option_some(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        inner = Tuple(vt, (1, "a"))
        carrier = Option.some(inner)

        self.assertTrue(carrier.search(inner[1]))


class TestDeepZip(unittest.TestCase):
    def test_matching_structure(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        a = Tuple(vt, (1, "a"))
        b = Tuple(vt, (2, "b"))
        self.assertEqual(len(list(deep_zip(a, b))), 3)

    def test_skip(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR))
        a = Tuple(vt, (1, "a"))
        b = Tuple(vt, (2, "b"))
        walker = deep_zip(a, b)
        results = []
        for left, right in walker:
            results.append((left, right))
            walker.skip()
        self.assertEqual(len(results), 1)

    def test_mismatch_raises(self):
        a = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a"))
        b = Tuple(cast(VaryingType, VaryingType.of(INT, FLOAT)), (2, 3.0))
        with self.assertRaises(Exception):
            list(deep_zip(a, b))


if __name__ == "__main__":
    unittest.main()
