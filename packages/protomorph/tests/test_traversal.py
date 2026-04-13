from __future__ import annotations

import unittest
from typing import Any, cast

import protomorph as pm

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
        self.assertTrue(all(nest.fetch().bound == nest.descriptor for nest in unnested_pattern))
        self.assertEqual(
            [repr(branch) for branch in unnested_pattern.values()],
            [
                "TraversalEdge(left=@1, weight=@2, right=#1)",
                "TraversalPoint(x=#0, y=2)",
                "TraversalWeight(amount=1)",
            ],
        )


class TestPatternExtraction(unittest.TestCase):
    def test_preserves_constants_and_extracts_vars(self):
        x = var("X", int)

        pattern = Pattern.from_val(val(TraversalPoint(cast(int, x), 2)))

        self.assertEqual(repr(pattern.pattern), "TraversalPoint(x=#0, y=2)")
        self.assertEqual(pattern.slot_count, 1)
        self.assertEqual(pattern.slots[0].fetch().bound, pattern.slots[0].descriptor)

    def test_extracts_wildcards_independently(self):
        pattern = Pattern.from_val(val(MatchPair(pm.Wildcard, pm.Wildcard)))
        morph = Morph.from_val(val(MatchPair(pm.Wildcard, pm.Wildcard)))

        self.assertEqual(repr(pattern.pattern), "MatchPair(left=#0, right=#1)")
        self.assertEqual(pattern.slot_count, 2)
        self.assertTrue(all(slot.descriptor == pm.Spec.of("std.types.Any") for slot in pattern.slots))
        self.assertTrue(all(slot.fetch().bound == slot.descriptor for slot in pattern.slots))
        self.assertEqual(morph.content, (pm.Wildcard, pm.Wildcard))
        self.assertEqual(repr(morph.value), "MatchPair(left=#0, right=#1)")


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
        z = var("Z", Any)
        u = var("U", Any)
        v = var("V", Any)

        left_pattern = Pattern.from_val(
            val(MatchQ(val(MatchA(pm.Wildcard, pm.Wildcard)), pm.Wildcard))
        )
        right_pattern = Pattern.from_val(
            val(MatchQ(pm.Wildcard, val(MatchB(pm.Wildcard, pm.Wildcard))))
        )

        left = Morph(
            descriptor=left_pattern,
            content=(
                val(x),
                val(y),
                val(z),
            ),
        )
        right = Morph(
            descriptor=right_pattern,
            content=(
                val(MatchA(val(x), val(y))),
                val(u),
                val(v),
            ),
        )

        matched = pm.logic.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertTrue(pm.canonical.compatible(left, right))
        self.assertEqual(matched.left, left_pattern)
        self.assertEqual(matched.right, right_pattern)
        self.assertEqual(
            repr(matched.fw_template),
            "<MatchQ(left=#0, right=MatchB(left=#1, right=#2)); #0=MatchA(left=#0, right=#1), #1={ #2 -> MatchB(left=_, right=_) }[#0], #2={ #2 -> MatchB(left=_, right=_) }[#1]>",
        )
        self.assertEqual(
            repr(matched.bw_template),
            "<MatchQ(left=MatchA(left=#0, right=#1), right=#2); #0={ #0 -> MatchA(left=_, right=_) }[#0], #1={ #0 -> MatchA(left=_, right=_) }[#1], #2=MatchB(left=#1, right=#2)>",
        )

        forwarded = matched.forward(left)

        self.assertEqual(forwarded.descriptor, right_pattern)
        self.assertEqual(repr(forwarded.content[0]), "MatchA(left=X, right=Y)")
        self.assertIsInstance(forwarded.content[1].fetch(), pm.Proj)
        self.assertIsInstance(forwarded.content[2].fetch(), pm.Proj)

        slot_1_proj = cast(pm.Proj, forwarded.content[1].fetch())
        slot_2_proj = cast(pm.Proj, forwarded.content[2].fetch())
        self.assertIsInstance(slot_1_proj.value.fetch(), pm.Fuse)
        self.assertIsInstance(slot_2_proj.value.fetch(), pm.Fuse)
        self.assertEqual(slot_1_proj.target.fetch().id, 0)
        self.assertEqual(slot_2_proj.target.fetch().id, 1)
        slot_1_fuse = cast(pm.Fuse, slot_1_proj.value.fetch())
        slot_2_fuse = cast(pm.Fuse, slot_2_proj.value.fetch())
        self.assertEqual(repr(slot_1_fuse.known.descriptor.pattern), "MatchB(left=#0, right=#1)")
        self.assertEqual(slot_1_fuse.parts, frozenset({val(z)}))
        self.assertEqual(slot_2_fuse.parts, frozenset({val(z)}))

        backwarded = matched.backward(right)

        self.assertEqual(backwarded.descriptor, left_pattern)
        self.assertIsInstance(backwarded.content[0].fetch(), pm.Proj)
        self.assertIsInstance(backwarded.content[1].fetch(), pm.Proj)
        self.assertEqual(repr(backwarded.content[2]), "MatchB(left=U, right=V)")
        slot_0_back_proj = cast(pm.Proj, backwarded.content[0].fetch())
        slot_1_back_proj = cast(pm.Proj, backwarded.content[1].fetch())
        self.assertEqual(
            repr(slot_0_back_proj.value),
            "{ MatchA(left=X, right=Y) -> MatchA(left=_, right=_) }",
        )
        self.assertEqual(
            repr(slot_1_back_proj.value),
            "{ MatchA(left=X, right=Y) -> MatchA(left=_, right=_) }",
        )
        self.assertEqual(slot_0_back_proj.target.fetch().id, 0)
        self.assertEqual(slot_1_back_proj.target.fetch().id, 1)

    def test_match_detects_repeated_slot_conflict(self):
        x = var("X", Any)

        left = Morph.from_val(val(MatchPair(val(x), val(x))))
        right = Morph.from_val(val(MatchPair(val(1), val(2))))

        self.assertIsNone(pm.logic.match(left, right))

    def test_match_treats_wildcards_as_distinct_holes(self):
        left = Morph.from_val(val(MatchPair(pm.Wildcard, pm.Wildcard)))
        right = Morph.from_val(val(MatchPair(val(1), val(2))))

        matched = pm.logic.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(repr(matched.fw_template), "MatchPair(left=1, right=2)")
        self.assertEqual(repr(matched.bw_template), "MatchPair(left=1, right=2)")

    def test_match_projects_rigid_constant_when_common_has_no_slot(self):
        x = var("X", str)

        left = Morph.from_val(val(MatchA(val(x), val(1))))
        right = Morph.from_val(val(MatchA(val("K"), val(1))))

        matched = pm.logic.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(repr(matched.fw_template), "MatchA(left='K', right=1)")
        self.assertEqual(repr(matched.bw_template), "MatchA(left='K', right=1)")
        self.assertEqual(matched.forward(left).content, ())
        self.assertEqual(matched.backward(right).content, (val("K"),))

    def test_match_preserves_shared_leaf_in_common_pattern(self):
        x = var("X", Any)
        y = var("Y", Any)
        z = var("Z", Any)

        left = Morph.from_val(val(MatchPair(val(x), val(x))))
        right = Morph.from_val(val(MatchPair(val(y), val(z))))

        matched = pm.logic.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(repr(matched.fw_template), "MatchPair(left=#0, right=#0)")
        self.assertEqual(repr(matched.bw_template), "<MatchPair(left=#0, right=#0); #0={ #0 | #1 -> _ }>")


class TestMorphProjection(unittest.TestCase):
    def test_project_slot_preserves_source_context(self):
        x = var("X", int)
        sample = Morph.from_val(val(TraversalEdge(TraversalPoint(cast(int, x), 2), TraversalWeight(1), 3)))

        projected = sample.project(sample.slots[0])

        self.assertEqual(projected.descriptor, sample.slots[0].descriptor)
        self.assertIsInstance(projected.fetch(), pm.Proj)
        self.assertIs(projected.fetch().value, sample)
        self.assertEqual(projected.fetch().target, sample.slots[0])

    def test_project_nest_preserves_source_context(self):
        x = var("X", int)
        sample = Morph.from_val(val(TraversalEdge(TraversalPoint(cast(int, x), 2), TraversalWeight(1), 3)))
        point_nest = sample.nests[1]

        projected = pm.canonical.project(sample, point_nest)

        self.assertEqual(projected.descriptor, point_nest.descriptor)
        self.assertIsInstance(projected.fetch(), pm.Proj)
        self.assertIs(projected.fetch().value, sample)
        self.assertEqual(projected.fetch().target, point_nest)


class TestNormalize(unittest.TestCase):
    def test_normalize_proj_over_morph_slot_returns_binding(self):
        x = var("X", int)
        sample = Morph.from_val(val(TraversalPoint(cast(int, x), 2)))

        normalized = pm.canonical.normalize(sample.project(sample.slots[0]))

        self.assertEqual(normalized, val(x))

    def test_normalize_proj_over_morph_nest_returns_submorph(self):
        x = var("X", int)
        sample = Morph.from_val(val(TraversalEdge(TraversalPoint(cast(int, x), 2), TraversalWeight(1), 3)))

        normalized = pm.canonical.normalize(sample.project(sample.nests[1]))

        self.assertIsInstance(normalized, Morph)
        branch = cast(Morph, normalized)
        self.assertEqual(repr(branch.descriptor.pattern), "TraversalPoint(x=#0, y=2)")
        self.assertEqual(branch.content, (val(x),))

    def test_normalize_fuse_empty_returns_known(self):
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))

        normalized = pm.canonical.normalize(pm.val(pm.Fuse(known=known, parts=frozenset())))

        self.assertEqual(normalized, known)

    def test_normalize_fuse_flattens_same_known(self):
        x = var("X", Any)
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))
        inner = pm.val(pm.Fuse(known=known, parts=frozenset({val(x)})))

        normalized = pm.canonical.normalize(
            pm.val(pm.Fuse(known=known, parts=frozenset({inner})))
        )

        self.assertIsInstance(normalized.fetch(), pm.Fuse)
        fuse = cast(pm.Fuse, normalized.fetch())
        self.assertEqual(fuse.known, known)
        self.assertEqual(fuse.parts, frozenset({val(x)}))

    def test_normalize_proj_over_live_fuse_projects_into_fuse(self):
        z = var("Z", Any)
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))
        live_fuse = pm.val(pm.Fuse(known=known, parts=frozenset({val(z)})))
        projected = pm.val(pm.Proj(value=live_fuse, target=known.slots[0]))

        normalized = pm.canonical.normalize(projected)

        self.assertIsInstance(normalized.fetch(), pm.Fuse)
        fuse = cast(pm.Fuse, normalized.fetch())
        self.assertEqual(repr(fuse.known.descriptor.pattern), "#0")
        self.assertEqual(fuse.known.content, (pm.Wildcard,))
        self.assertEqual(len(fuse.parts), 1)
        [part] = list(fuse.parts)
        self.assertIsInstance(part.fetch(), pm.Proj)
        self.assertEqual(cast(pm.Proj, part.fetch()).value, val(z))
        self.assertEqual(cast(pm.Proj, part.fetch()).target, known.slots[0])


class TestDisplay(unittest.TestCase):
    def test_morph_repr_reifies_only_leaf_bindings(self):
        x = var("X", Any)
        y = var("Y", Any)

        descriptor = Pattern.from_val(val(MatchQ(val(MatchA(pm.Wildcard, pm.Wildcard)), pm.Wildcard)))
        morph = Morph(
            descriptor=descriptor,
            content=(val(x), val(y), val(MatchB(val(1), val(2)))),
        )

        self.assertEqual(
            repr(morph),
            "<MatchQ(left=MatchA(left=X, right=Y), right=#2); #2=MatchB(left=1, right=2)>",
        )

    def test_morph_repr_expands_operator_leaf_bindings(self):
        z = var("Z", Any)
        descriptor = Pattern.from_val(val(MatchPair(pm.Wildcard, pm.Wildcard)))
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))
        morph = Morph(
            descriptor=descriptor,
            content=(val(1), pm.val(pm.Fuse(known=known, parts=frozenset({val(z)})))),
        )

        self.assertEqual(
            repr(morph),
            "<MatchPair(left=1, right=#1); #1={ Z -> MatchB(left=_, right=_) }>",
        )

    def test_fuse_repr_uses_known_arrow_parts(self):
        z = var("Z", Any)
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))
        fuse = pm.val(pm.Fuse(known=known, parts=frozenset({val(z)})))

        self.assertEqual(repr(fuse), "{ Z -> MatchB(left=_, right=_) }")

    def test_proj_repr_uses_index_syntax(self):
        z = var("Z", Any)
        known = Morph.from_val(val(MatchB(pm.Wildcard, pm.Wildcard)))
        fuse = pm.val(pm.Fuse(known=known, parts=frozenset({val(z)})))
        projected = pm.val(pm.Proj(value=fuse, target=known.slots[0]))

        self.assertEqual(repr(projected), "{ Z -> MatchB(left=_, right=_) }[#0]")

    def test_match_repr_uses_cell_notation(self):
        x = var("X", Any)
        y = var("Y", Any)
        z = var("Z", Any)
        u = var("U", Any)
        v = var("V", Any)

        left_pattern = Pattern.from_val(
            val(MatchQ(val(MatchA(pm.Wildcard, pm.Wildcard)), pm.Wildcard))
        )
        right_pattern = Pattern.from_val(
            val(MatchQ(pm.Wildcard, val(MatchB(pm.Wildcard, pm.Wildcard))))
        )
        left = Morph(descriptor=left_pattern, content=(val(x), val(y), val(z)))
        right = Morph(
            descriptor=right_pattern,
            content=(val(MatchA(val(x), val(y))), val(u), val(v)),
        )

        matched = pm.logic.match(left, right)

        self.assertIsNotNone(matched)
        assert matched is not None
        self.assertEqual(
            repr(matched),
            "MatchQ(left=MatchA(left=#0, right=#1), right=#2) ==[<MatchQ(left=#0, right=MatchB(left=#1, right=#2)); #0=MatchA(left=#0, right=#1), #1={ #2 -> MatchB(left=_, right=_) }[#0], #2={ #2 -> MatchB(left=_, right=_) }[#1]> | <MatchQ(left=MatchA(left=#0, right=#1), right=#2); #0={ #0 -> MatchA(left=_, right=_) }[#0], #1={ #0 -> MatchA(left=_, right=_) }[#1], #2=MatchB(left=#1, right=#2)>]== MatchQ(left=#0, right=MatchB(left=#1, right=#2))",
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
