from __future__ import annotations

import unittest
from typing import cast

import protomorph as pm
from protobase import frozendict

from protomorph import (
    Builtin,
    WILDCARD,
    LeafCarrier,
    PlaceholderMetatype,
    Spec,
    Varying,
    var,
    val,
)


ANY = Spec.of("std.types.Any")
INT = cast(Spec, val(int).content)
STR = cast(Spec, val(str).content)


class Point(Builtin):
    SPEC_NAME = "test.matching.Point"
    x: int
    y: int


class TestCarrierPatternFlag(unittest.TestCase):
    def test_placeholder_metatype_wraps_placeholder(self):
        T = var("T")
        meta = cast(PlaceholderMetatype, T.metatype())
        self.assertEqual(meta.of, T)
        self.assertEqual(meta.level, 1)


class TestSimpleMatching(unittest.TestCase):
    def test_leaf_var_captures_subject(self):
        T = var("T")
        pattern = LeafCarrier(ANY, T)
        subject = val(42)

        result = pm.match.match(pattern, subject)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values[pattern], pm.match.Binding(frozenset({subject})))

    def test_custom_is_var_can_disable_capture(self):
        T = var("T")
        pattern = LeafCarrier(ANY, T)
        subject = LeafCarrier(ANY, T)

        result = pm.match.match(pattern, subject, is_var=lambda _: False)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values, frozendict())

    def test_multiple_captures_accumulate(self):
        T = var("T")
        pair = pm.Tuple(cast(pm.Type[tuple], Varying((ANY, ANY))), (T, T))
        subject = pm.Tuple(cast(pm.Type[tuple], Varying((ANY, ANY))), (1, 2))

        result = pm.match.match(pair, subject)

        self.assertIsNotNone(result)
        assert result is not None
        binding = result.solutions[0].env.values[pair[0]]
        self.assertEqual({capture.content for capture in binding.captures}, {1, 2})

    def test_matchenv_merge_raises_exceptiongroup_for_all_conflicts(self):
        T = LeafCarrier(ANY, var("T"))
        U = LeafCarrier(ANY, var("U"))
        env = pm.match.Env(
            frozendict(
                {
                    T: pm.match.Binding(frozenset({val(1), val(2)})),
                    U: pm.match.Binding(frozenset({val("a"), val("b")})),
                }
            )
        )

        def merge_one(var, binding):
            if len(binding.captures) != 1:
                raise ValueError(f"bad {var!r}")
            return next(iter(binding.captures))

        with self.assertRaises(ExceptionGroup) as ctx:
            env.merge(is_var=lambda _: True, var_merge=merge_one)

        self.assertEqual(len(ctx.exception.exceptions), 2)

    def test_structural_builtin_match(self):
        result = pm.match.match(val(Point(1, 2)), val(Point(1, 2)))
        self.assertIsNotNone(result)

    def test_wildcard_mark_matches_without_capture(self):
        pattern = LeafCarrier(ANY, WILDCARD)
        subject = val(42)

        result = pm.match.match(pattern, subject)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values, frozendict())


class TestSummaryCompile(unittest.TestCase):
    def test_compile_wraps_tree(self):
        summary = pm.match.CaseSummary(
            pattern=val(1),
            shape=pm.match.ShapeSummary(min_positional_count=0, max_positional_count=0, allowed_keys=frozenset()),
        )
        tree = pm.match.compile({summary: "one"})
        self.assertIsInstance(tree.content, pm.match.Tree)

    def test_shape_groups_compile_to_matchmany(self):
        no_args = pm.match.CaseSummary(
            pattern=val(1),
            shape=pm.match.ShapeSummary(min_positional_count=0, max_positional_count=0, allowed_keys=frozenset()),
        )
        one_arg = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=pm.match.ShapeSummary(min_positional_count=1, max_positional_count=1, allowed_keys=frozenset()),
        )

        tree = pm.match.compile({no_args: "zero", one_arg: "one"})
        tree_val = cast(pm.match.Tree, tree.content)

        self.assertIsInstance(tree_val.root, pm.match.Many)

    def test_same_shape_is_guarded(self):
        summary = pm.match.CaseSummary(
            pattern=val(1),
            shape=pm.match.ShapeSummary(min_positional_count=0, max_positional_count=0, allowed_keys=frozenset()),
        )
        tree = pm.match.compile({summary: "one"})
        tree_val = cast(pm.match.Tree, tree.content)
        self.assertIsInstance(tree_val.root, pm.match.GuardShape)

    def test_prefix_descriptor_switch_selected_first(self):
        int_summary = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=pm.match.ShapeSummary(min_positional_count=1, max_positional_count=1, allowed_keys=frozenset()),
            prefix_descriptors=(INT,),
        )
        str_summary = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=pm.match.ShapeSummary(min_positional_count=1, max_positional_count=1, allowed_keys=frozenset()),
            prefix_descriptors=(STR,),
        )

        tree = pm.match.compile({int_summary: "int", str_summary: "str"})
        root = cast(pm.match.GuardShape, cast(pm.match.Tree, tree.content).root)
        self.assertIsInstance(root.child, pm.match.SwitchFieldDescriptors)

    def test_nominal_descriptor_switch_used_when_positional_not_available(self):
        text_key = pm.Id("text")
        int_summary = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=pm.match.ShapeSummary(
                min_positional_count=0,
                max_positional_count=0,
                required_keys=frozenset({text_key}),
                allowed_keys=frozenset({text_key}),
            ),
            required_nominal_descriptors=frozendict({text_key: INT}),
        )
        str_summary = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=pm.match.ShapeSummary(
                min_positional_count=0,
                max_positional_count=0,
                required_keys=frozenset({text_key}),
                allowed_keys=frozenset({text_key}),
            ),
            required_nominal_descriptors=frozendict({text_key: STR}),
        )

        tree = pm.match.compile({int_summary: "int", str_summary: "str"})
        root = cast(pm.match.GuardShape, cast(pm.match.Tree, tree.content).root)
        self.assertIsInstance(root.child, pm.match.SwitchNominalDescriptors)

    def test_ambiguity_residual_leaf(self):
        a = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, var("T")),
            shape=pm.match.ShapeSummary(min_positional_count=1, max_positional_count=1, allowed_keys=frozenset()),
            prefix_descriptors=(None,),
        )
        b = pm.match.CaseSummary(
            pattern=LeafCarrier(ANY, var("U")),
            shape=pm.match.ShapeSummary(min_positional_count=1, max_positional_count=1, allowed_keys=frozenset()),
            prefix_descriptors=(None,),
        )
        tree = pm.match.compile({a: "left", b: "right"})
        tree_val = cast(pm.match.Tree, tree.content)
        root = cast(pm.match.GuardShape, tree_val.root)
        self.assertIsInstance(root.child, pm.match.Leaf)
        self.assertEqual(len(pm.match.diagnose(tree_val)), 1)


if __name__ == "__main__":
    unittest.main()
