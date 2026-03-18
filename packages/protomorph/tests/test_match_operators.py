from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import cast

from protobase import Consed

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


TYPE_TRAIT = morph.spec_ref("std.traits.Type")
NUMBER_TYPE = morph.nominal_type("std.core.Number")
TRANSITIVE_GOAL = morph.spec_ref("test.Transitive", morph.struct(morph.THIS))


class DemoBridge(morph.SemanticBridgeBase, Consed):
    def solve(
        self,
        goal: morph.Spec,
        state: morph.MatchState,
    ):
        if goal.anchor.path != "test.Extends":
            if goal.anchor.path != "test.Transitive":
                return ()

            args = goal.args or morph.Struct.Empty
            current = args[0] if len(args.values) > 0 else None
            resolved = current.as_type() if isinstance(current, morph.Val) else None
            if isinstance(resolved, morph.NominalQualifier):
                if resolved.spec_ref.anchor.path == "std.qualifiers.Optional":
                    return (state,)
            return ()

        args = goal.args or morph.Struct.Empty
        current = args[0] if len(args.values) > 0 else None
        base = args.get("from", default=None)
        if current == morph.val(morph.INTEGER_TYPE) and base == morph.val(NUMBER_TYPE):
            return (state,)
        return ()


class MatchOperatorTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()
        self._demo_bridge = DemoBridge()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

    def test_struct_and_spec_roundtrip_operator_and_placeholder_values(self):
        operator = morph.view_as(TYPE_TRAIT, morph.ANY)
        struct_value = morph.struct(operator, morph.THIS)
        spec = morph.spec_ref("test.Box", morph.spec(T=operator, Self=morph.THIS))

        self.assertEqual(struct_value[0], operator)
        self.assertEqual(struct_value[1], morph.THIS)
        args = spec.args
        self.assertIsNotNone(args)
        assert args is not None
        self.assertEqual(args.get("T"), operator)
        self.assertEqual(args.get("Self"), morph.THIS)

    def test_subst_rewrites_reserved_this_var_inside_specs(self):
        goal = morph.spec_ref(
            "test.Extends",
            morph.struct(morph.THIS, **{"from": morph.val(NUMBER_TYPE)}),
        )

        resolved = goal.subst(
            lambda value: morph.val(morph.INTEGER_TYPE) if value == morph.THIS else None
        )

        self.assertEqual(
            resolved,
            morph.spec_ref(
                "test.Extends",
                morph.struct(
                    morph.val(morph.INTEGER_TYPE),
                    **{"from": morph.val(NUMBER_TYPE)},
                ),
            ),
        )

    def test_match_var_and_any_cover_bind_and_wildcard_routes(self):
        ctx = DummyContext()
        var = morph.var(DummyVarType, ctx, "T")

        states = tuple(morph.match(var, morph.literal(42)))
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].bindings.get(var), morph.literal(42))

        wildcard_states = tuple(morph.match(morph.ANY, morph.literal(7)))
        self.assertEqual(wildcard_states, (morph.MatchState(),))

    def test_view_as_matches_type_like_values_via_bridge(self):
        ctx = DummyContext()
        capture = morph.var(DummyVarType, ctx, "T")
        pattern = morph.view_as(TYPE_TRAIT, capture)

        states = tuple(
            morph.match(
                pattern,
                morph.anchor("std.core.Text"),
                bridge=self._demo_bridge,
            )
        )

        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].bindings.get(capture), morph.val(morph.TEXT_TYPE))

    def test_view_as_works_when_nested_inside_struct_patterns(self):
        pattern = morph.struct(name=morph.view_as(TYPE_TRAIT, morph.ANY))
        value = morph.struct(name=morph.anchor("std.core.Text"))

        states = tuple(morph.match(pattern, value, bridge=self._demo_bridge))

        self.assertEqual(states, (morph.MatchState(),))

    def test_satisfy_rewrites_this_and_delegates_to_bridge_solver(self):
        goal = morph.spec_ref(
            "test.Extends",
            morph.struct(morph.THIS, **{"from": morph.val(NUMBER_TYPE)}),
        )

        states = tuple(
            morph.match(
                morph.satisfy(goal),
                morph.val(morph.INTEGER_TYPE),
                bridge=self._demo_bridge,
            )
        )

        self.assertEqual(states, (morph.MatchState(),))

    def test_variadic_struct_captures_middle_segment(self):
        ctx = DummyContext()
        capture = morph.var(DummyVarType, ctx, "Rest")
        pattern = morph.variadic_struct(
            prefix=cast(
                morph.Struct[str | None, morph.Val],
                morph.Struct.new(morph.literal(1)),
            ),
            middle=capture,
            suffix=cast(
                morph.Struct[str | None, morph.Val],
                morph.Struct.new(morph.literal(4)),
            ),
        )
        value = morph.struct(
            morph.literal(1),
            morph.literal(2),
            morph.literal(3),
            morph.literal(4),
        )

        states = tuple(morph.match(pattern, value, bridge=self._demo_bridge))

        self.assertEqual(len(states), 1)
        self.assertEqual(
            states[0].bindings.get(capture),
            morph.struct(morph.literal(2), morph.literal(3)),
        )

    def test_qualifier_suffix_matches_inner_suffix_with_default_skip(self):
        inner = morph.nominal_qual(
            "std.qualifiers.Map",
            morph.spec(K=str),
            underlying=morph.INTEGER_TYPE,
        )
        outer = morph.nominal_qual("std.qualifiers.Optional", underlying=inner)

        states = tuple(
            morph.match(
                morph.qualifier_suffix(inner),
                cast(morph.Val, outer),
                bridge=self._demo_bridge,
            )
        )

        self.assertEqual(states, (morph.MatchState(),))

    def test_qualifier_suffix_respects_conditional_skip_rules(self):
        inner = morph.nominal_qual(
            "std.qualifiers.Map",
            morph.spec(K=str),
            underlying=morph.INTEGER_TYPE,
        )
        outer = morph.nominal_qual("std.qualifiers.Optional", underlying=inner)
        skip_if = morph.satisfy(TRANSITIVE_GOAL)

        inner_states = tuple(
            morph.match(
                morph.qualifier_suffix(inner, skip_if=skip_if),
                cast(morph.Val, outer),
                bridge=self._demo_bridge,
            )
        )
        terminal_states = tuple(
            morph.match(
                morph.qualifier_suffix(morph.INTEGER_TYPE, skip_if=skip_if),
                cast(morph.Val, outer),
                bridge=self._demo_bridge,
            )
        )

        self.assertEqual(inner_states, (morph.MatchState(),))
        self.assertEqual(terminal_states, ())


if __name__ == "__main__":
    unittest.main()
