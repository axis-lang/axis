from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import cast

from protobase import frozendict

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


class MatchTreeTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

    def test_compile_groups_exact_values_under_value_switch(self):
        tree = morph.compile(
            frozendict(
                {
                    morph.literal(1): frozenset({"one"}),
                    morph.literal(2): frozenset({"two"}),
                }
            )
        )

        self.assertIsInstance(tree.root, morph.MatchSwitch)
        self.assertEqual(tree.goals, frozenset({frozenset({"one"}), frozenset({"two"})}))
        self.assertEqual(tree.resolve(morph.literal(1)), "one")
        self.assertEqual(tree.resolve(morph.literal(2)), "two")
        self.assertIsNone(tree.resolve(morph.literal(3)))

    def test_compile_rejects_empty_pattern_set(self):
        with self.assertRaises(ValueError):
            morph.compile(frozendict())

    def test_compile_uses_fallback_for_wildcard_patterns(self):
        tree = morph.compile(
            frozendict(
                {
                    morph.literal(1): frozenset({"one"}),
                    morph.ANY: frozenset({"any"}),
                }
            )
        )

        result = tree.search(morph.literal(1))
        self.assertEqual(result.goals, frozenset({"one", "any"}))
        self.assertTrue(result.is_ambiguous)
        self.assertEqual(tree.resolve(morph.literal(2)), "any")

    def test_struct_patterns_bind_vars_into_envs(self):
        ctx = DummyContext()
        t = morph.var(DummyVarType, ctx, "T")
        pattern = morph.struct(t, name=morph.ANY)
        tree = morph.compile(
            frozendict(
                {
                    pattern: frozenset({"struct"}),
                }
            )
        )

        value = morph.struct(morph.literal(7), name=morph.literal("axis"))
        result = tree.search(value)

        self.assertEqual(result.goals, frozenset({"struct"}))
        envs = result.envs_by_goal["struct"]
        self.assertEqual(len(envs), 1)
        self.assertEqual(envs[0].bindings[t], morph.literal(7))

    def test_repeated_var_requires_equal_values(self):
        ctx = DummyContext()
        t = morph.var(DummyVarType, ctx, "T")
        tree = morph.compile(frozendict({morph.struct(t, t): frozenset({"same"})}))

        self.assertEqual(tree.resolve(morph.struct(morph.literal(1), morph.literal(1))), "same")
        self.assertIsNone(tree.resolve(morph.struct(morph.literal(1), morph.literal(2))))

    def test_compile_result_tracks_terminal_leaves(self):
        tree = morph.compile(
            frozendict(
                {
                    morph.literal(1): frozenset({"one", "uno"}),
                }
            )
        )

        self.assertEqual(len(tree.compiled.leaves), 1)
        leaf = next(iter(tree.compiled.leaves))
        self.assertEqual(leaf.goals, frozenset({"one", "uno"}))
        self.assertEqual(tree.ambiguous_goals, frozenset({frozenset({"one", "uno"})}))

    def test_struct_schema_closed_matches_struct_values(self):
        ctx = DummyContext()
        t = morph.var(DummyVarType, ctx, "T")
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    (None, morph.StructSchema.Field(match_expr=t)),
                    ("name", morph.StructSchema.Field(match_expr=morph.ANY)),
                )
            )
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        value = morph.struct(morph.literal(7), name=morph.literal("axis"))
        result = tree.search(value)

        self.assertEqual(result.goals, frozenset({"schema"}))
        self.assertEqual(result.envs_by_goal["schema"][0].bindings[t], morph.literal(7))

    def test_compile_can_mix_struct_schema_and_value_patterns(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                ((None, morph.StructSchema.Field(match_expr=morph.literal(1))),)
            )
        )
        tree = morph.compile(
            frozendict(
                {
                    schema: frozenset({"schema"}),
                    morph.literal(2): frozenset({"two"}),
                }
            )
        )

        self.assertEqual(tree.resolve(morph.struct(morph.literal(1))), "schema")
        self.assertEqual(tree.resolve(morph.literal(2)), "two")

    def test_search_accepts_const_wrapped_struct_input(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter((("name", morph.StructSchema.Field(match_expr=morph.ANY)),))
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        result = tree.search(morph.struct(name=morph.literal("axis")))
        self.assertEqual(result.goals, frozenset({"schema"}))

    def test_field_type_discriminator_partitions_closed_struct_patterns(self):
        int_pattern = morph.struct(morph.literal(1))
        text_pattern = morph.struct(morph.literal("x"))

        tree = morph.compile(
            frozendict(
                {
                    int_pattern: frozenset({"int"}),
                    text_pattern: frozenset({"text"}),
                }
            )
        )

        self.assertIsInstance(tree.root, morph.MatchSwitch)
        root = cast(morph.MatchSwitch, tree.root)
        self.assertIsInstance(root.discriminator, morph.FieldTypeDiscriminator)
        self.assertEqual(tree.resolve(morph.struct(morph.literal(1))), "int")
        self.assertEqual(tree.resolve(morph.struct(morph.literal("x"))), "text")

    def test_struct_schema_defaults_expand_internally(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    (None, morph.StructSchema.Field(match_expr=morph.literal(1))),
                    (
                        "name",
                        morph.StructSchema.Field(
                            match_expr=morph.ANY,
                            default=morph.literal("anon"),
                        ),
                    ),
                )
            )
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        self.assertEqual(tree.resolve(morph.struct(morph.literal(1))), "schema")
        self.assertEqual(
            tree.resolve(morph.struct(morph.literal(1), name=morph.literal("axis"))),
            "schema",
        )

    def test_struct_schema_expands_trailing_positional_defaults(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    (None, morph.StructSchema.Field(match_expr=morph.literal(1))),
                    (None, morph.StructSchema.Field(match_expr=morph.literal(2), default=morph.literal(2))),
                )
            )
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        self.assertEqual(tree.resolve(morph.struct(morph.literal(1))), "schema")
        self.assertEqual(tree.resolve(morph.struct(morph.literal(1), morph.literal(2))), "schema")

    def test_closed_schema_rejects_extra_nominal_field(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter((("name", morph.StructSchema.Field(match_expr=morph.ANY)),))
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        self.assertIsNone(tree.resolve(morph.struct(name=morph.literal("axis"), extra=morph.literal(1))))

    def test_closed_schema_rejects_wrong_key_order(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    ("left", morph.StructSchema.Field(match_expr=morph.ANY)),
                    ("right", morph.StructSchema.Field(match_expr=morph.ANY)),
                )
            )
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))
        value = morph.Struct.from_iter(
            (
                ("right", morph.literal(2)),
                ("left", morph.literal(1)),
            )
        ).as_const()

        self.assertIsNone(tree.resolve(value))

    def test_variadic_struct_schema_matches_middle_as_struct(self):
        ctx = DummyContext()
        rest = morph.var(DummyVarType, ctx, "Rest")
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    (None, morph.StructSchema.Field(match_expr=morph.literal(1))),
                    ("tail", morph.StructSchema.Field(match_expr=morph.literal(9))),
                )
            ),
            varsign=morph.VariadicSignature(
                prefix_len=1,
                suffix_len=1,
                prefix_index=morph.Struct.Index((None,)),
                suffix_index=morph.Struct.Index(("tail",)),
            ),
            middle=rest,
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        value = morph.struct(
            morph.literal(1),
            morph.literal(2),
            morph.literal(3),
            tail=morph.literal(9),
        )
        result = tree.search(value)

        self.assertEqual(result.goals, frozenset({"schema"}))
        self.assertEqual(
            result.envs_by_goal["schema"][0].bindings[rest],
            morph.struct(morph.literal(2), morph.literal(3)),
        )

    def test_open_tail_without_spread_matches(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(((None, morph.StructSchema.Field(match_expr=morph.literal(1))),)),
            varsign=morph.VariadicSignature(
                prefix_len=1,
                suffix_len=0,
                prefix_index=morph.Struct.Index((None,)),
                suffix_index=morph.Struct.Index(()),
            ),
            middle=morph.ANY,
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        self.assertEqual(tree.resolve(morph.struct(morph.literal(1), morph.literal(2), morph.literal(3))), "schema")

    def test_variadic_schema_rejects_too_short_input(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                (
                    (None, morph.StructSchema.Field(match_expr=morph.literal(1))),
                    ("tail", morph.StructSchema.Field(match_expr=morph.literal(9))),
                )
            ),
            varsign=morph.VariadicSignature(
                prefix_len=1,
                suffix_len=1,
                prefix_index=morph.Struct.Index((None,)),
                suffix_index=morph.Struct.Index(("tail",)),
            ),
        )
        tree = morph.compile(frozendict({schema: frozenset({"schema"})}))

        self.assertIsNone(tree.resolve(morph.struct(morph.literal(1))))

    def test_variadic_struct_schema_validates_signature_shape(self):
        schema = morph.StructSchema(
            fields=morph.Struct.from_iter(
                ((None, morph.StructSchema.Field(match_expr=morph.literal(1))),)
            ),
            varsign=morph.VariadicSignature(
                prefix_len=1,
                suffix_len=1,
                prefix_index=morph.Struct.Index((None,)),
                suffix_index=morph.Struct.Index(("tail",)),
            ),
        )

        with self.assertRaises(ValueError):
            morph.compile(frozendict({schema: frozenset({"schema"})}))


if __name__ == "__main__":
    unittest.main()
