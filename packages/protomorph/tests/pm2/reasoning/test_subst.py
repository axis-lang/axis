from __future__ import annotations

import unittest

from protobase import frozendict

from pm import Spec, placeholder
from pm.reasoning import BindingSnapshot, DeferredGoal, GoalCtx, GoalVar, KeyOfOperator, PendingBranch, QueryVar, Rule, TypeFunctionBlocked
from pm.reasoning.subst import (
    branch_session_bindings,
    canonicalize_branch,
    canonicalize_branch_specs,
    canonicalize,
    class_info_of,
    compile_template,
    extract_visible_subst,
    goal_placeholder_info,
    ground_fact_for,
    instantiate_template,
    instantiate_query,
    materialize_branch_goals,
    make_union_find,
    public_subst,
    rule_context_for,
    seed_query_bindings,
    wrap_logic,
)
from pm.reasoning.vars import RuleAppCtx, RuleVar
from pm.unification import unify


ALICE = Spec.of("test.alice")
BOB = Spec.of("test.bob")


class TestReasoningSubst(unittest.TestCase):
    def test_public_subst_roundtrip(self):
        y = placeholder("Y")
        goal = Spec.of("test.parent", ALICE, y)
        runtime, placeholders, slots = instantiate_query(goal)
        canonical = canonicalize(runtime, make_union_find())
        uf = make_union_find()
        self.assertTrue(seed_query_bindings(uf, slots, placeholders, BindingSnapshot()))
        self.assertIsNotNone(unify(slots[0], wrap_logic(BOB), subst=uf))

        subst = extract_visible_subst(canonical, uf)
        public = public_subst(placeholders, canonical, subst)

        self.assertEqual(public[y], BOB)

    def test_operator_values_are_not_promoted_to_query_placeholders(self):
        x = placeholder("X")
        r = placeholder("R")
        goal = Spec.of("std.rels.KeyOf", KeyOfOperator.of(x), r)

        _, placeholders, _ = instantiate_query(goal)

        self.assertEqual(placeholders, (r,))

    def test_ground_fact_for_returns_none_for_unresolved_slots(self):
        x = placeholder("X")
        goal = Spec.of("test.parent", ALICE, x)
        runtime, _, _ = instantiate_query(goal)
        canonical = canonicalize(runtime, make_union_find())

        self.assertIsNone(ground_fact_for(canonical.key, ()))

    def test_canonicalize_emits_goal_vars_with_structured_context(self):
        y = placeholder("Y")
        runtime, _, _ = instantiate_query(Spec.of("test.parent", ALICE, y))

        canonical = canonicalize(runtime, make_union_find())

        residual = canonical.key.args.content[1]
        self.assertIsInstance(residual, GoalVar)
        assert isinstance(residual, GoalVar)
        self.assertEqual(residual.slot, 0)
        self.assertIsInstance(residual.ctx, GoalCtx)
        self.assertEqual(str(residual.ctx.skeleton.anchor), "test.parent")

    def test_rule_context_template_key_is_alpha_normalized(self):
        x = placeholder("X")
        y = placeholder("Y")
        a = placeholder("A")
        b = placeholder("B")

        first = Rule(Spec.of("test.edge", x, y), (Spec.of("test.edge", y, x),))
        second = Rule(Spec.of("test.edge", a, b), (Spec.of("test.edge", b, a),))

        first_ctx = rule_context_for(first)
        second_ctx = rule_context_for(second)

        self.assertEqual(repr(first_ctx.template_key), repr(second_ctx.template_key))
        self.assertEqual(first_ctx.source_names, ("X", "Y"))
        self.assertEqual(second_ctx.source_names, ("A", "B"))

    def test_union_find_tracks_collapsed_query_and_rule_origins(self):
        q = placeholder("Q")
        r = placeholder("R")
        runtime_goal, _, slots = instantiate_query(Spec.of("test.edge", q))
        rule = Rule(Spec.of("test.edge", r), ())
        rule_ctx = rule_context_for(rule)
        compiled = compile_template(rule.head, rule_ctx)
        app_ctx = RuleAppCtx(parent_goal=rule_ctx.template_key.head, rule_ctx=rule_ctx, app_serial=1)
        uf = make_union_find()

        self.assertIsNotNone(unify(runtime_goal, instantiate_template(compiled, app_ctx), subst=uf))

        info = class_info_of(uf, slots[0])
        self.assertIsNotNone(info)
        assert info is not None
        self.assertEqual({type(origin).__name__ for origin in info.origins}, {"QueryVar", "RuleVar"})
        self.assertTrue(any(isinstance(origin, QueryVar) and origin.slot == 0 for origin in info.origins))
        self.assertIn(RuleVar(ctx=rule_ctx, slot=0), info.origins)
        self.assertEqual(info.source_names, frozenset({"Q", "R"}))

    def test_canonicalize_branch_persists_structured_substitution(self):
        x = placeholder("X")
        y = placeholder("Y")
        runtime_goal, _, slots = instantiate_query(Spec.of("test.pair", x, y))
        uf = make_union_find()

        self.assertIsNotNone(unify(slots[0], wrap_logic(ALICE), subst=uf))

        blocked_template = wrap_logic(Spec.of("test.blocked", x))
        blocked_leaf = next(leaf for leaf in blocked_template.deep_iter() if leaf.fetch() == x)
        blocked_carrier = blocked_template.subst({blocked_leaf: slots[0]})

        remaining_template = wrap_logic(Spec.of("test.ready", x, y))
        remaining_mapping = {
            leaf: slots[0] if leaf.fetch() == x else slots[1]
            for leaf in remaining_template.deep_iter()
            if leaf.fetch() in {x, y}
        }
        remaining_carrier = remaining_template.subst(remaining_mapping)

        blocked_goal, remaining_goals, subst, slot_info = canonicalize_branch(
            blocked_carrier,
            (remaining_carrier,),
            uf,
        )

        self.assertEqual(str(blocked_goal.anchor), "test.blocked")
        self.assertEqual(len(remaining_goals), 1)
        self.assertEqual(subst, ((0, wrap_logic(ALICE)),))
        self.assertIsNotNone(slot_info[0])
        assert slot_info[0] is not None
        self.assertEqual(slot_info[0].source_names, frozenset({"X"}))

    def test_materialize_branch_goals_applies_branch_substitution(self):
        blocked, remaining, subst, slot_info = canonicalize_branch_specs(
            Spec.of("test.blocked", placeholder("A")),
            (Spec.of("test.ready", placeholder("A")),),
        )
        branch = PendingBranch(
            blocked=DeferredGoal(blocked, TypeFunctionBlocked(blocked, "wait")),
            remaining_goals=remaining,
            subst=((0, wrap_logic(ALICE)),),
            slot_info=slot_info,
        )

        materialized_blocked, materialized_remaining = materialize_branch_goals(branch)

        self.assertEqual(repr(materialized_blocked), repr(Spec.of("test.blocked", ALICE)))
        self.assertEqual(repr(materialized_remaining[0]), repr(Spec.of("test.ready", ALICE)))

    def test_branch_session_bindings_bridge_query_origins(self):
        t = placeholder("T")
        r = placeholder("R")
        runtime_goal, placeholders, slots = instantiate_query(Spec.of("std.rels.KeyOf", t, r))
        canonical = canonicalize(runtime_goal, make_union_find())
        blocked, remaining, subst, slot_info = canonicalize_branch_specs(
            canonical.key,
            (),
            goal_placeholder_info(canonical),
        )
        branch = PendingBranch(
            blocked=DeferredGoal(blocked, TypeFunctionBlocked(blocked, "keyof")),
            remaining_goals=remaining,
            subst=subst,
            slot_info=slot_info,
        )

        bridged = branch_session_bindings(
            branch,
            BindingSnapshot(frozendict(((placeholders[0], ALICE),))),
        )

        self.assertEqual(bridged, ((0, ALICE),))


if __name__ == "__main__":
    unittest.main()
