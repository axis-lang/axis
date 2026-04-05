from __future__ import annotations

import unittest
from typing import cast

from protobase import frozendict

import protomorph
from protomorph import Builtin, Host, Spec, placeholder, spec_name
from protomorph.native import instantiate_builtin
from protomorph.reasoning import (
    Answer,
    Deferred,
    Engine,
    KeyOfOperator,
    NoSolution,
    OpAnswer,
    OpExpand,
    OpFailed,
    RuleSetDatabase,
    SolveContext,
    AttrOperator,
    TypeOfOperator,
    Unique,
)


ALICE = Spec.of("test.alice")
BOB = Spec.of("test.bob")


class Record(Builtin):
    name: str
    age: int


class ExpandHost(Host):
    def eval_logic_op(self, operator, *, goal, session):
        return OpExpand((Spec.of("test.parent", ALICE, BOB),))


class AnswerHost(Host):
    def eval_logic_op(self, operator, *, goal, session):
        return OpAnswer((Answer(goal, evidence=Spec.of("test.evidence")),))


class FailedHost(Host):
    def eval_logic_op(self, operator, *, goal, session):
        return OpFailed("cannot evaluate")


class OverrideKeyOfHost(Host):
    def eval_logic_op(self, operator, *, goal, session):
        return OpAnswer((Answer(goal, evidence=Spec.of("test.override")),))


class SubstAnswerHost(Host):
    answer_placeholder: protomorph.Placeholder

    def eval_logic_op(self, operator, *, goal, session):
        return OpAnswer((Answer(goal, frozendict(((self.answer_placeholder, BOB),)), Spec.of("test.subst")),))


class TestReasoningOperators(unittest.TestCase):
    def test_instantiate_builtin_reconstructs_logic_attr_operator(self):
        args = protomorph.VaryingType.new(protomorph.wrap(ALICE), protomorph.wrap("name"))

        builtin = instantiate_builtin("std.logic.Attr", args)

        self.assertIsInstance(builtin, AttrOperator)
        assert isinstance(builtin, AttrOperator)
        self.assertEqual(builtin.of_value.fetch(), ALICE)
        self.assertEqual(builtin.key, protomorph.Id("name"))

    def test_instantiate_builtin_reconstructs_logic_typeof_operator(self):
        args = protomorph.VaryingType.new(protomorph.wrap("hey"))

        builtin = instantiate_builtin("std.logic.TypeOf", args)

        self.assertIsInstance(builtin, TypeOfOperator)
        assert isinstance(builtin, TypeOfOperator)
        self.assertEqual(builtin.of_value.fetch(), "hey")

    def test_operator_expand_resolves_query(self):
        goal = Spec.of("test.inspect", KeyOfOperator.of(ALICE))
        engine = Engine(RuleSetDatabase(facts=(Spec.of("test.parent", ALICE, BOB),), host=ExpandHost()))
        result = engine.session(context=SolveContext("expand")).query(goal).result.outcome

        self.assertIsInstance(result, Unique)

    def test_operator_answer_is_used_directly(self):
        engine = Engine(RuleSetDatabase(host=AnswerHost()))
        goal = Spec.of("test.inspect", KeyOfOperator.of(ALICE))
        result = engine.session(context=SolveContext("answer")).query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).evidence, Spec.of("test.evidence"))
        self.assertIsNotNone(cast(Unique, result).judgment)

    def test_operator_answer_applies_visible_substitution(self):
        q = placeholder("Q")
        engine = Engine(RuleSetDatabase(host=SubstAnswerHost(q)))
        goal = Spec.of("test.inspect", KeyOfOperator.of(ALICE), q)
        result = engine.session(context=SolveContext("answer-subst")).query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], BOB)

    def test_operator_failed_becomes_no_solution(self):
        engine = Engine(RuleSetDatabase(host=FailedHost()))
        goal = Spec.of("test.inspect", KeyOfOperator.of(ALICE))
        result = engine.session(context=SolveContext("failed")).query(goal).result.outcome

        self.assertIsInstance(result, NoSolution)

    def test_session_retry_deferred_replays_with_new_host(self):
        engine = Engine(RuleSetDatabase())
        goal = Spec.of("test.inspect", KeyOfOperator.of(placeholder("X")))

        deferred_result = engine.session().query(goal).result
        self.assertIsInstance(deferred_result.outcome, Deferred)
        self.assertIsNotNone(deferred_result.next_session)
        assert deferred_result.next_session is not None

        rebound = deferred_result.next_session.__class__(
            Engine(RuleSetDatabase(host=AnswerHost())),
            deferred_result.next_session.context,
            deferred_result.next_session.state,
        )
        retried = rebound.retry_deferred()

        stored = retried.query(goal).result.outcome
        self.assertIsInstance(stored, Unique)

    def test_builtin_keyof_returns_structural_keys(self):
        engine = Engine(RuleSetDatabase())
        r = placeholder("R")
        goal = Spec.of("std.rels.KeyOf", Spec.of(spec_name(Record)), r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[r], ("name", "age"))

    def test_builtin_keyof_unknown_target_is_deferred(self):
        engine = Engine(RuleSetDatabase())
        t = placeholder("T")
        r = placeholder("R")
        goal = Spec.of("std.rels.KeyOf", t, r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Deferred)

    def test_builtin_keyof_uses_operator_pipeline(self):
        engine = Engine(RuleSetDatabase(host=OverrideKeyOfHost()))
        r = placeholder("R")
        goal = Spec.of("std.rels.KeyOf", Spec.of(spec_name(Record)), r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).evidence, Spec.of("test.override"))

    def test_builtin_projection_returns_field_type(self):
        engine = Engine(RuleSetDatabase())
        r = placeholder("R")
        goal = Spec.of("std.rels.Proj", Spec.of(spec_name(Record)), "name", r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(repr(cast(Unique, result).subst[r]), repr(Spec.of("Text")))

    def test_builtin_projection_unknown_target_is_deferred(self):
        engine = Engine(RuleSetDatabase())
        t = placeholder("T")
        r = placeholder("R")
        goal = Spec.of("std.rels.Proj", t, "name", r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Deferred)

    def test_builtin_typeof_returns_runtime_type(self):
        engine = Engine(RuleSetDatabase())
        r = placeholder("R")
        goal = Spec.of("std.logic.TypeOf", "hey", r)

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[r], protomorph.wrap("hey").type.fetch())

    def test_builtin_conforms_identity_accepts_typeof_value(self):
        engine = Engine(RuleSetDatabase())
        goal = Spec.of("std.facts.Conforms", TypeOfOperator.of("hey"), to=protomorph.wrap("hey").type.fetch())

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, Unique)

    def test_builtin_conforms_identity_rejects_distinct_types(self):
        engine = Engine(RuleSetDatabase())
        goal = Spec.of("std.facts.Conforms", TypeOfOperator.of("hey"), to=protomorph.wrap(3).type.fetch())

        result = engine.session().query(goal).result.outcome

        self.assertIsInstance(result, NoSolution)


if __name__ == "__main__":
    unittest.main()
