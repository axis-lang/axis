from __future__ import annotations

import unittest

from protobase import frozendict

from protomorph import Builtin, Spec, placeholder, spec_name
from protomorph.reasoning import Deferred, DeferredGoal, Engine, KeyOfOperator, OperatorPending, Rule, RuleSetDatabase, SessionState, default_wake_on
from protomorph.reasoning.subst import materialize_branch_goals


ALICE = Spec.of("test.alice")


class Record(Builtin):
    name: str
    age: int


class TestReasoningSession(unittest.TestCase):
    def test_with_deferred_dedupes_structurally(self):
        q = placeholder("Q")
        blocked = DeferredGoal(
            Spec.of("std.rels.KeyOf", q, placeholder("R")),
            OperatorPending(Spec.of("std.rels.KeyOf", q, placeholder("R")), KeyOfOperator.of(q)),
            wake_on=default_wake_on(OperatorPending(Spec.of("std.rels.KeyOf", q, placeholder("R")), KeyOfOperator.of(q))),
        )
        session = Engine(RuleSetDatabase()).session().with_deferred((blocked, blocked))

        self.assertEqual(len(session.state.deferred), 1)

    def test_session_indexes_deferred_by_placeholder(self):
        t = placeholder("T")
        r = placeholder("R")
        engine = Engine(RuleSetDatabase())
        result = engine.session().query(Spec.of("std.rels.KeyOf", t, r)).result
        assert result.next_session is not None

        indexed = result.next_session.state.tables.deferred_by_placeholder
        self.assertIn(t, indexed)
        self.assertIn(r, indexed)

    def test_with_local_facts_tracks_recent_anchor_delta(self):
        session = Engine(RuleSetDatabase()).session(state=SessionState())
        next_session = session.with_local_facts(Spec.of("test.parent", ALICE, Spec.of("test.bob")))

        self.assertEqual(next_session.state.recent_local_fact_anchors, ("test.parent",))

    def test_retry_deferred_preserves_branch_state_when_still_blocked(self):
        t = placeholder("T")
        r = placeholder("R")
        engine = Engine(RuleSetDatabase())
        first = engine.session().query(Spec.of("std.rels.KeyOf", t, r)).result
        assert first.next_session is not None
        assert first.query.semantic_key is not None
        before = first.next_session.state.tables.query_tables[first.query.semantic_key]

        retried = first.next_session.retry_deferred()
        after = retried.state.tables.query_tables[first.query.semantic_key]

        self.assertEqual(len(before.continuation_state), len(after.continuation_state))
        self.assertEqual(before.frontier, after.frontier)

    def test_retry_deferred_progresses_branch_without_full_reblock(self):
        t = placeholder("T")
        r = placeholder("R")
        u = placeholder("U")
        s = placeholder("S")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.combo", t, r, u, s),
                        (Spec.of("std.rels.KeyOf", t, r), Spec.of("std.rels.KeyOf", u, s)),
                    ),
                )
            )
        )

        first = engine.session().query(Spec.of("test.combo", t, r, u, s)).result
        self.assertIsInstance(first.outcome, Deferred)
        assert first.next_session is not None
        assert first.query.semantic_key is not None

        progressed = first.next_session.with_bindings(frozendict(((t, Spec.of(spec_name(Record))),)))
        retried = progressed.retry_deferred()
        result = retried.query(Spec.of("test.combo", t, r, u, s)).result.outcome

        self.assertIsInstance(result, Deferred)

    def test_retry_deferred_accumulates_subjudgment_on_progressed_branch(self):
        t = placeholder("T")
        r = placeholder("R")
        u = placeholder("U")
        s = placeholder("S")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.combo", t, r, u, s),
                        (Spec.of("std.rels.KeyOf", t, r), Spec.of("std.rels.KeyOf", u, s)),
                    ),
                )
            )
        )

        first = engine.session().query(Spec.of("test.combo", t, r, u, s)).result
        assert first.next_session is not None

        progressed = first.next_session.with_bindings(frozendict(((t, Spec.of(spec_name(Record))),)))
        retried = progressed.retry_deferred()
        result = retried.query(Spec.of("test.combo", t, r, u, s)).result

        self.assertIsInstance(result.outcome, Deferred)
        assert result.next_session is not None
        assert result.query.semantic_key is not None
        branch = result.next_session.state.tables.query_tables[result.query.semantic_key].continuation_state[0]
        materialized_blocked, materialized_remaining = materialize_branch_goals(branch)
        self.assertEqual(str(materialized_blocked.anchor), "std.rels.KeyOf")
        self.assertEqual(materialized_remaining, ())
        self.assertEqual(len(branch.subjudgments), 1)


if __name__ == "__main__":
    unittest.main()
