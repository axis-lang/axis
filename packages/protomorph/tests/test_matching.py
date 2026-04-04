from __future__ import annotations

import unittest
from typing import cast

import protomorph as pm
from protobase import frozendict

from protomorph import (
    Builtin,
    WILDCARD,
    LeafCarrier,
    MatchBinding,
    MatchCaseSummary,
    MatchEnv,
    MatchGuardShape,
    MatchLeaf,
    MatchMany,
    MatchShapeSummary,
    MatchSwitchFieldDescriptors,
    MatchSwitchNominalDescriptors,
    MatchTree,
    PlaceholderMetatype,
    Spec,
    VaryingType,
    compile,
    diagnose,
    match,
    placeholder,
    wrap,
)


ANY = Spec.of("std.core.Any")
INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())


class Point(Builtin):
    SPEC_NAME = "test.matching.Point"
    x: int
    y: int


class TestCarrierPatternFlag(unittest.TestCase):
    def test_plain_value_is_not_pattern(self):
        self.assertFalse(wrap(Point(1, 2)).is_pattern)

    def test_placeholder_leaf_is_pattern(self):
        T = placeholder("T")
        self.assertTrue(LeafCarrier(ANY, T).is_pattern)

    def test_placeholder_metatype_wraps_placeholder(self):
        T = placeholder("T")
        meta = cast(PlaceholderMetatype, T.metatype())
        self.assertEqual(meta.of, T)
        self.assertEqual(meta.level, 1)


class TestSimpleMatching(unittest.TestCase):
    def test_leaf_var_captures_subject(self):
        T = placeholder("T")
        pattern = LeafCarrier(ANY, T)
        subject = wrap(42)

        result = match(pattern, subject)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values[pattern], MatchBinding(frozenset({subject})))

    def test_custom_is_var_can_disable_capture(self):
        T = placeholder("T")
        pattern = LeafCarrier(ANY, T)
        subject = LeafCarrier(ANY, T)

        result = match(pattern, subject, is_var=lambda _: False)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values, frozendict())

    def test_multiple_captures_accumulate(self):
        T = placeholder("T")
        pair = pm.Tuple(cast(pm.Type[tuple], VaryingType((ANY, ANY))), (T, T))
        subject = pm.Tuple(cast(pm.Type[tuple], VaryingType((ANY, ANY))), (1, 2))

        result = match(pair, subject)

        self.assertIsNotNone(result)
        assert result is not None
        binding = result.solutions[0].env.values[pair[0]]
        self.assertEqual({capture.fetch() for capture in binding.captures}, {1, 2})

    def test_matchenv_merge_raises_exceptiongroup_for_all_conflicts(self):
        T = LeafCarrier(ANY, placeholder("T"))
        U = LeafCarrier(ANY, placeholder("U"))
        env = MatchEnv(
            frozendict(
                {
                    T: MatchBinding(frozenset({wrap(1), wrap(2)})),
                    U: MatchBinding(frozenset({wrap("a"), wrap("b")})),
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
        result = match(wrap(Point(1, 2)), wrap(Point(1, 2)))
        self.assertIsNotNone(result)

    def test_wildcard_mark_matches_without_capture(self):
        pattern = LeafCarrier(ANY, WILDCARD)
        subject = wrap(42)

        result = match(pattern, subject)

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.solutions[0].env.values, frozendict())


class TestSummaryCompile(unittest.TestCase):
    def test_compile_wraps_tree(self):
        summary = MatchCaseSummary(
            pattern=wrap(1),
            shape=MatchShapeSummary(min_arity=0, max_arity=0, allowed_keys=frozenset()),
        )
        tree = compile({summary: "one"})
        self.assertIsInstance(tree.fetch(), MatchTree)

    def test_shape_groups_compile_to_matchmany(self):
        no_args = MatchCaseSummary(
            pattern=wrap(1),
            shape=MatchShapeSummary(min_arity=0, max_arity=0, allowed_keys=frozenset()),
        )
        one_arg = MatchCaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=MatchShapeSummary(min_arity=1, max_arity=1, allowed_keys=frozenset()),
        )

        tree = compile({no_args: "zero", one_arg: "one"})
        tree_val = cast(MatchTree, tree.fetch())

        self.assertIsInstance(tree_val.root, MatchMany)

    def test_same_shape_is_guarded(self):
        summary = MatchCaseSummary(
            pattern=wrap(1),
            shape=MatchShapeSummary(min_arity=0, max_arity=0, allowed_keys=frozenset()),
        )
        tree = compile({summary: "one"})
        tree_val = cast(MatchTree, tree.fetch())
        self.assertIsInstance(tree_val.root, MatchGuardShape)

    def test_prefix_descriptor_switch_selected_first(self):
        int_summary = MatchCaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=MatchShapeSummary(min_arity=1, max_arity=1, allowed_keys=frozenset()),
            prefix_descriptors=(INT,),
        )
        str_summary = MatchCaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=MatchShapeSummary(min_arity=1, max_arity=1, allowed_keys=frozenset()),
            prefix_descriptors=(STR,),
        )

        tree = compile({int_summary: "int", str_summary: "str"})
        root = cast(MatchGuardShape, cast(MatchTree, tree.fetch()).root)
        self.assertIsInstance(root.child, MatchSwitchFieldDescriptors)

    def test_nominal_descriptor_switch_used_when_positional_not_available(self):
        text_key = pm.Id("text")
        int_summary = MatchCaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=MatchShapeSummary(min_arity=0, max_arity=0, required_keys=frozenset({text_key}), allowed_keys=frozenset({text_key})),
            required_nominal_descriptors=frozendict({text_key: INT}),
        )
        str_summary = MatchCaseSummary(
            pattern=LeafCarrier(ANY, 1),
            shape=MatchShapeSummary(min_arity=0, max_arity=0, required_keys=frozenset({text_key}), allowed_keys=frozenset({text_key})),
            required_nominal_descriptors=frozendict({text_key: STR}),
        )

        tree = compile({int_summary: "int", str_summary: "str"})
        root = cast(MatchGuardShape, cast(MatchTree, tree.fetch()).root)
        self.assertIsInstance(root.child, MatchSwitchNominalDescriptors)

    def test_ambiguity_residual_leaf(self):
        a = MatchCaseSummary(
            pattern=LeafCarrier(ANY, placeholder("T")),
            shape=MatchShapeSummary(min_arity=1, max_arity=1, allowed_keys=frozenset()),
            prefix_descriptors=(None,),
        )
        b = MatchCaseSummary(
            pattern=LeafCarrier(ANY, placeholder("U")),
            shape=MatchShapeSummary(min_arity=1, max_arity=1, allowed_keys=frozenset()),
            prefix_descriptors=(None,),
        )
        tree = compile({a: "left", b: "right"})
        tree_val = cast(MatchTree, tree.fetch())
        root = cast(MatchGuardShape, tree_val.root)
        self.assertIsInstance(root.child, MatchLeaf)
        self.assertEqual(len(diagnose(tree_val)), 1)


if __name__ == "__main__":
    unittest.main()
