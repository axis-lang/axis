from __future__ import annotations

import unittest
from typing import cast

from protobase import frozendict

from pm import Builtin, Spec, placeholder, spec_name
from pm.reasoning import (
    Ambiguous,
    BindingSnapshot,
    BindingsChanged,
    Deferred,
    Engine,
    Floundered,
    Judgment,
    KeyOfOperator,
    MixedCycle,
    NegativeCycle,
    NoSolution,
    Query,
    Rule,
    RuleSetDatabase,
    SessionState,
    Unique,
)


ALICE = Spec.of("test.alice")
BOB = Spec.of("test.bob")
CAROL = Spec.of("test.carol")


def fact(anchor: str, *args: object) -> Spec:
    return Spec.of(anchor, *args)


class Record(Builtin):
    name: str
    age: int


class TestReasoningQuery(unittest.TestCase):
    def test_query_solves_fact(self):
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        x = placeholder("X")

        result = engine.session().query(Spec.of("test.parent", ALICE, x)).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[x], BOB)
        self.assertIsInstance(cast(Unique, result).judgment, Judgment)
        answers = engine.session().query(Spec.of("test.parent", ALICE, x)).public_answers
        self.assertIsInstance(answers[0].judgment, Judgment)

    def test_query_solves_rule_chain(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        db = RuleSetDatabase(
            rules=(
                Rule(
                    Spec.of("test.gp", x, z),
                    (Spec.of("test.parent", x, y), Spec.of("test.parent", y, z)),
                ),
            ),
            facts=(
                fact("test.parent", ALICE, BOB),
                fact("test.parent", BOB, CAROL),
            ),
        )
        engine = Engine(db)
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.gp", ALICE, q)).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], CAROL)
        answer = engine.session().query(Spec.of("test.gp", ALICE, q)).public_answers[0]
        assert answer.judgment is not None
        evidence = answer.judgment.evidence
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(str(evidence.anchor), "std.logic.ByRule")
        self.assertEqual(len(answer.judgment.subjudgments), 2)

    def test_query_reports_multiple_answers(self):
        db = RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB), fact("test.parent", ALICE, CAROL)))
        engine = Engine(db)
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.parent", ALICE, q)).result.outcome

        self.assertIsInstance(result, Ambiguous)
        self.assertGreaterEqual(len(cast(Ambiguous, result).judgments), 1)

    def test_query_positive_recursion_reaches_fixed_point(self):
        x = placeholder("X")
        y = placeholder("Y")
        z = placeholder("Z")
        db = RuleSetDatabase(
            rules=(
                Rule(Spec.of("test.path", x, y), (Spec.of("test.edge", x, y),)),
                Rule(
                    Spec.of("test.path", x, y),
                    (Spec.of("test.edge", x, z), Spec.of("test.path", z, y)),
                ),
            ),
            facts=(
                fact("test.edge", ALICE, BOB),
                fact("test.edge", BOB, CAROL),
            ),
        )
        engine = Engine(db)
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.path", ALICE, q)).result.outcome

        self.assertIsInstance(result, Ambiguous)

    def test_session_local_facts_overlay(self):
        engine = Engine(RuleSetDatabase())
        session = engine.session(
            state=SessionState(local_facts=(fact("test.parent", ALICE, BOB),)),
        )
        q = placeholder("Q")

        result = session.query(Spec.of("test.parent", ALICE, q)).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[q], BOB)

    def test_result_next_session_commits_unique_bindings(self):
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        x = placeholder("X")
        query = engine.session().query(Spec.of("test.parent", ALICE, x))

        result = query.result

        self.assertIsNotNone(result.next_session)
        assert result.next_session is not None
        self.assertEqual(result.next_session.state.bindings.values[x], BOB)

    def test_session_seed_bindings_are_applied(self):
        x = placeholder("X")
        y = placeholder("Y")
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        session = engine.session(
            state=SessionState(BindingSnapshot(frozendict(((x, ALICE),)))),
        )

        result = session.query(Spec.of("test.parent", x, y)).result.outcome

        self.assertIsInstance(result, Unique)
        self.assertEqual(cast(Unique, result).subst[x], ALICE)
        self.assertEqual(cast(Unique, result).subst[y], BOB)

    def test_query_no_solution(self):
        engine = Engine(RuleSetDatabase())
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.parent", ALICE, q)).result.outcome

        self.assertIsInstance(result, NoSolution)
        assert isinstance(result, NoSolution)
        self.assertIsNotNone(result.judgment)
        assert result.judgment is not None
        assert result.judgment.evidence is not None
        self.assertEqual(str(result.judgment.evidence.anchor), "std.logic.ByNoSolution")
        table = engine.session().query(Spec.of("test.parent", ALICE, q)).table
        self.assertFalse(table.is_blocked)
        self.assertFalse(table.is_cycle)
        self.assertFalse(table.has_failures)

    def test_seed_bindings_preserve_structured_no_solution(self):
        x = placeholder("X")
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        session = engine.session(state=SessionState(BindingSnapshot(frozendict(((x, CAROL),)))))

        result = session.query(Spec.of("test.parent", ALICE, x)).result.outcome

        self.assertIsInstance(result, NoSolution)
        assert isinstance(result, NoSolution)
        self.assertEqual(result.reason, "no matching proof")
        self.assertIsNotNone(result.judgment)
        assert result.judgment is not None
        assert result.judgment.evidence is not None
        self.assertEqual(str(result.judgment.evidence.anchor), "std.logic.ByNoSolution")

    def test_non_ground_negation_flounders(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                )
            )
        )
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.safe", q)).result.outcome

        self.assertIsInstance(result, Floundered)
        floundered = cast(Floundered, result)
        self.assertEqual(len(floundered.judgments), 1)
        assert floundered.judgments[0].evidence is not None
        self.assertEqual(str(floundered.judgments[0].evidence.anchor), "std.logic.ByDeferred")

    def test_negation_over_fact_predicate_succeeds_or_fails(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                ),
                facts=(fact("test.blocked", ALICE),),
            )
        )

        blocked = engine.session().query(Spec.of("test.safe", ALICE)).result.outcome
        self.assertIsInstance(engine.session().query(Spec.of("test.safe", BOB)).result.outcome, Unique)
        self.assertIsInstance(blocked, NoSolution)
        assert isinstance(blocked, NoSolution)
        self.assertIsNotNone(blocked.judgment)
        assert blocked.judgment is not None
        self.assertTrue(_has_evidence_anchor(blocked.judgment, "std.logic.ByFact"))
        self.assertTrue(_has_evidence_anchor(blocked.judgment, "std.logic.ByNoSolution"))

    def test_negation_over_derived_predicate_uses_closed_global_tables(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.blocked", x), (Spec.of("test.banned", x),)),
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                ),
                facts=(fact("test.banned", ALICE),),
            )
        )

        blocked = engine.session().query(Spec.of("test.safe", ALICE)).result.outcome
        safe = engine.session().query(Spec.of("test.safe", BOB)).result.outcome

        self.assertIsInstance(blocked, NoSolution)
        self.assertIsInstance(safe, Unique)

    def test_negative_cycle_reported(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.loop", x),
                        (Spec.of("std.logic.Not", Spec.of("test.loop", x)),),
                    ),
                )
            )
        )

        result = engine.session().query(Spec.of("test.loop", ALICE)).result.outcome

        self.assertIsInstance(result, NegativeCycle)
        assert isinstance(result, NegativeCycle)
        self.assertIsNotNone(result.trace)
        assert result.trace is not None
        self.assertEqual(result.trace.kind, "negative")
        table = engine.session().query(Spec.of("test.loop", ALICE)).table
        assert table.cycle_issue is not None
        self.assertEqual(table.cycle_issue.kind, "negative")
        self.assertTrue(table.is_cycle)
        self.assertIsNotNone(result.judgment)
        assert result.judgment is not None
        assert result.judgment.evidence is not None
        self.assertEqual(str(result.judgment.evidence.anchor), "std.logic.ByNegativeCycle")
        self.assertEqual({str(member.goal.anchor) for member in result.trace.members}, {"test.loop"})

    def test_cross_anchor_negative_cycle_preserves_component_trace(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.a", x), (Spec.of("std.logic.Not", Spec.of("test.b", x)),)),
                    Rule(Spec.of("test.b", x), (Spec.of("std.logic.Not", Spec.of("test.a", x)),)),
                )
            )
        )

        result = engine.session().query(Spec.of("test.a", ALICE)).result.outcome

        self.assertIsInstance(result, NegativeCycle)
        assert isinstance(result, NegativeCycle)
        self.assertIsNotNone(result.trace)
        assert result.trace is not None
        self.assertEqual({str(member.goal.anchor) for member in result.trace.members}, {"test.a", "test.b"})

    def test_coinductive_self_cycle_succeeds(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(Rule(Spec.of("test.stream", x), (Spec.of("test.stream", x),)),),
                coinductive_anchors=frozenset(("test.stream",)),
            )
        )

        result = engine.session().query(Spec.of("test.stream", ALICE)).result.outcome

        self.assertIsInstance(result, Unique)
        answer = engine.session().query(Spec.of("test.stream", ALICE)).public_answers[0]
        assert answer.judgment is not None
        assert answer.judgment.evidence is not None
        self.assertEqual(str(answer.judgment.evidence.anchor), "std.logic.ByRule")
        self.assertTrue(_has_evidence_anchor(answer.judgment, "std.logic.ByCoinduction"))

    def test_two_node_coinductive_cycle_succeeds(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.left", x), (Spec.of("test.right", x),)),
                    Rule(Spec.of("test.right", x), (Spec.of("test.left", x),)),
                ),
                coinductive_anchors=frozenset(("test.left", "test.right")),
            )
        )

        result = engine.session().query(Spec.of("test.left", ALICE)).result.outcome

        self.assertIsInstance(result, Unique)

    def test_coinductive_cycle_preserves_trace(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.left", x), (Spec.of("test.right", x),)),
                    Rule(Spec.of("test.right", x), (Spec.of("test.left", x),)),
                ),
                coinductive_anchors=frozenset(("test.left", "test.right")),
            )
        )

        answer = engine.session().query(Spec.of("test.left", ALICE)).public_answers[0]
        coinduction = _find_judgment_by_anchor(answer.judgment, "std.logic.ByCoinduction")

        self.assertIsNotNone(coinduction)
        assert coinduction is not None
        self.assertIsNotNone(coinduction.trace)
        assert coinduction.trace is not None
        self.assertEqual(coinduction.trace.kind, "coinductive")
        self.assertEqual({str(member.goal.anchor) for member in coinduction.trace.members}, {"test.left", "test.right"})

    def test_mixed_cycle_reported(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.co", x), (Spec.of("test.in", x),)),
                    Rule(Spec.of("test.in", x), (Spec.of("test.co", x),)),
                ),
                coinductive_anchors=frozenset(("test.co",)),
            )
        )

        result = engine.session().query(Spec.of("test.co", ALICE)).result.outcome

        self.assertIsInstance(result, MixedCycle)
        assert isinstance(result, MixedCycle)
        self.assertIsNotNone(result.trace)
        assert result.trace is not None
        self.assertEqual(result.trace.kind, "mixed")
        self.assertEqual({str(member.goal.anchor) for member in result.trace.members}, {"test.co", "test.in"})
        self.assertIsNotNone(result.judgment)
        assert result.judgment is not None
        assert result.judgment.evidence is not None
        self.assertEqual(str(result.judgment.evidence.anchor), "std.logic.ByMixedCycle")

    def test_coinductive_cycle_with_negative_edge_is_rejected(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(Spec.of("test.co", x), (Spec.of("test.mid", x),)),
                    Rule(Spec.of("test.mid", x), (Spec.of("std.logic.Not", Spec.of("test.co", x)),)),
                ),
                coinductive_anchors=frozenset(("test.co", "test.mid")),
            )
        )

        result = engine.session().query(Spec.of("test.co", ALICE)).result.outcome

        self.assertIsInstance(result, NegativeCycle)
        assert isinstance(result, NegativeCycle)
        self.assertIsNotNone(result.trace)
        assert result.trace is not None
        self.assertEqual(result.trace.kind, "negative")

    def test_unhandled_operator_is_deferred(self):
        q = placeholder("Q")
        engine = Engine(RuleSetDatabase())

        result = engine.session().query(Spec.of("std.rels.KeyOf", KeyOfOperator.of(q), placeholder("R"))).result

        self.assertIsInstance(result.outcome, Deferred)
        self.assertIsNotNone(result.continuation)
        self.assertTrue(result.can_continue)
        assert result.next_session is not None
        assert result.continuation is not None
        self.assertIs(result.continuation.session, result.next_session)
        deferred = cast(Deferred, result.outcome)
        self.assertEqual(len(deferred.judgments), 1)
        assert deferred.judgments[0].evidence is not None
        self.assertEqual(str(deferred.judgments[0].evidence.anchor), "std.logic.ByDeferred")
        assert result.query.semantic_key is not None
        stored = result.next_session.state.tables.query_tables[result.query.semantic_key]
        self.assertFalse(stored.closed)
        self.assertTrue(stored.active)
        self.assertEqual(stored.status, "blocked")
        self.assertTrue(stored.is_blocked)
        self.assertFalse(stored.has_failures)
        self.assertEqual(stored.frontier, tuple(blocked.goal for blocked in stored.deferred))
        self.assertTrue(any(isinstance(wake, BindingsChanged) for wake in stored.deferred[0].wake_on))
        self.assertIsNotNone(stored.deferred[0].judgment)
        assert stored.deferred[0].judgment is not None
        assert stored.deferred[0].judgment.evidence is not None
        self.assertEqual(str(stored.deferred[0].judgment.evidence.anchor), "std.logic.ByDeferred")

    def test_blocked_query_stores_pending_branch_with_remaining_goals(self):
        x = placeholder("X")
        t = placeholder("T")
        r = placeholder("R")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.combo", x),
                        (Spec.of("std.rels.KeyOf", t, r), Spec.of("test.fact", x)),
                    ),
                ),
                facts=(fact("test.fact", ALICE),),
            )
        )

        result = engine.session().query(Spec.of("test.combo", ALICE)).result

        self.assertIsInstance(result.outcome, Deferred)
        assert result.next_session is not None
        assert result.query.semantic_key is not None
        table = result.next_session.state.tables.query_tables[result.query.semantic_key]
        self.assertEqual(len(table.continuation_state), 1)
        branch = table.continuation_state[0]
        self.assertEqual(len(branch.remaining_goals), 1)
        self.assertEqual(str(branch.remaining_goals[0].anchor), "test.fact")
        self.assertTrue(branch.subst)
        self.assertEqual(branch.subst[0][1].fetch(), ALICE)

    def test_closed_result_has_no_continuation(self):
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        q = placeholder("Q")

        result = engine.session().query(Spec.of("test.parent", ALICE, q)).result

        self.assertFalse(result.can_continue)
        self.assertIsNone(result.continuation)
        self.assertIs(result.resume(), result)

    def test_cycle_table_has_cycle_status(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.loop", x),
                        (Spec.of("std.logic.Not", Spec.of("test.loop", x)),),
                    ),
                )
            )
        )

        result = engine.session().query(Spec.of("test.loop", ALICE)).result

        assert result.next_session is not None
        assert result.query.semantic_key is not None
        table = result.next_session.state.tables.query_tables[result.query.semantic_key]
        self.assertEqual(table.status, "cycle")

    def test_query_result_reuses_session_table_snapshot(self):
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB),)))
        q = placeholder("Q")

        first = engine.session().query(Spec.of("test.parent", ALICE, q)).result
        assert first.next_session is not None
        second = first.next_session.query(Spec.of("test.parent", ALICE, q)).result

        self.assertIsInstance(first.outcome, Unique)
        self.assertIsInstance(second.outcome, Unique)
        self.assertIn(first.query.semantic_key, first.next_session.state.tables.query_tables)

    def test_query_tables_use_canonical_semantic_keys(self):
        engine = Engine(RuleSetDatabase(facts=(fact("test.parent", ALICE, BOB), fact("test.parent", ALICE, CAROL))))
        x = placeholder("X")
        y = placeholder("Y")
        first = engine.session().query(Spec.of("test.parent", x, y)).result
        assert first.next_session is not None
        second = first.next_session.query(Spec.of("test.parent", placeholder("A"), placeholder("B"))).result

        self.assertEqual(len(first.next_session.state.tables.query_tables), 1)
        self.assertEqual(repr(first.query.semantic_key), repr(second.query.semantic_key))
        self.assertIsInstance(second.outcome, Ambiguous)

    def test_session_promotes_ground_answers_into_contextual_tables(self):
        x = placeholder("X")
        y = placeholder("Y")
        engine = Engine(
            RuleSetDatabase(
                rules=(Rule(Spec.of("test.path", x, y), (Spec.of("test.edge", x, y),)),),
            )
        )
        session = engine.session(state=SessionState(local_facts=(fact("test.edge", ALICE, BOB),)))
        q = placeholder("Q")

        result = session.query(Spec.of("test.path", ALICE, q)).result

        assert result.next_session is not None
        promoted = {repr(item) for item in result.next_session.state.tables.answers_by_anchor["test.path"]}
        self.assertIn(repr(Spec.of("test.path", ALICE, BOB)), promoted)

        reused = engine.session(
            context=result.next_session.context,
            state=SessionState(
                result.next_session.state.bindings,
                (),
                result.next_session.state.deferred,
                result.next_session.state.tables,
                result.next_session.state.epoch,
            ),
        ).query(Spec.of("test.path", ALICE, q)).result.outcome

        self.assertIsInstance(reused, Unique)
        self.assertEqual(cast(Unique, reused).subst[q], BOB)

    def test_session_retry_deferred_after_binding_update(self):
        x = placeholder("X")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.safe", x),
                        (Spec.of("std.logic.Not", Spec.of("test.blocked", x)),),
                    ),
                ),
                facts=(fact("test.blocked", ALICE),),
            )
        )

        first = engine.session().query(Spec.of("test.safe", x)).result
        self.assertIsInstance(first.outcome, Floundered)
        assert first.next_session is not None

        rebound = first.next_session.with_bindings(frozendict(((x, ALICE),)))
        retried = rebound.retry_deferred()
        final = retried.query(Spec.of("test.safe", x)).result.outcome

        self.assertIsInstance(final, NoSolution)
        assert first.query.semantic_key is not None
        self.assertIn(first.query.semantic_key, retried.state.tables.query_tables)
        table = retried.state.tables.query_tables[first.query.semantic_key]
        self.assertTrue(table.closed)
        self.assertFalse(table.deferred)
        self.assertFalse(table.answers)

    def test_retry_deferred_synthesizes_direct_unique_without_root_requery(self):
        t = placeholder("T")
        r = placeholder("R")
        engine = Engine(RuleSetDatabase())

        first = engine.session().query(Spec.of("std.rels.KeyOf", t, r)).result
        self.assertIsInstance(first.outcome, Deferred)
        assert first.next_session is not None
        assert first.query.semantic_key is not None

        rebound = first.next_session.with_bindings(frozendict(((t, Spec.of(spec_name(Record))),)))
        retried = rebound.retry_deferred()
        table = retried.state.tables.query_tables[first.query.semantic_key]

        self.assertEqual(tuple(retried.state.tables.query_tables), (first.query.semantic_key,))
        self.assertTrue(table.closed)
        self.assertFalse(table.deferred)
        self.assertTrue(table.answers)

        final = retried.query(Spec.of("std.rels.KeyOf", t, r)).result.outcome
        self.assertIsInstance(final, Unique)

    def test_retry_deferred_synthesizes_ambiguous_answers_without_root_requery(self):
        t = placeholder("T")
        r = placeholder("R")
        q = placeholder("Q")
        engine = Engine(
            RuleSetDatabase(
                rules=(
                    Rule(
                        Spec.of("test.combo", t, r, q),
                        (Spec.of("std.rels.KeyOf", t, r), Spec.of("test.parent", ALICE, q)),
                    ),
                ),
                facts=(fact("test.parent", ALICE, BOB), fact("test.parent", ALICE, CAROL)),
            )
        )

        first = engine.session().query(Spec.of("test.combo", t, r, q)).result
        self.assertIsInstance(first.outcome, Deferred)
        assert first.next_session is not None
        assert first.query.semantic_key is not None

        rebound = first.next_session.with_bindings(frozendict(((t, Spec.of(spec_name(Record))),)))
        retried = rebound.retry_deferred()
        table = retried.state.tables.query_tables[first.query.semantic_key]

        self.assertEqual(tuple(retried.state.tables.query_tables), (first.query.semantic_key,))
        self.assertTrue(table.closed)
        self.assertFalse(table.deferred)
        self.assertEqual(len(table.answers), 2)
        self.assertTrue(all(answer.judgment is not None for answer in table.answers))
        self.assertTrue(all(len(answer.judgment.subjudgments) == 2 for answer in table.answers if answer.judgment is not None))

        final = retried.query(Spec.of("test.combo", t, r, q)).result.outcome
        self.assertIsInstance(final, Ambiguous)

    def test_retry_deferred_ignores_unrelated_binding_change(self):
        t = placeholder("T")
        r = placeholder("R")
        u = placeholder("U")
        engine = Engine(RuleSetDatabase())

        first = engine.session().query(Spec.of("std.rels.KeyOf", t, r)).result
        self.assertIsInstance(first.outcome, Deferred)
        assert first.next_session is not None

        rebound = first.next_session.with_bindings(frozendict(((u, ALICE),)))
        retried = rebound.retry_deferred()
        final = retried.query(Spec.of("std.rels.KeyOf", t, r)).result

        self.assertIsInstance(final.outcome, Deferred)
        self.assertEqual(retried.state.bindings.values[u], ALICE)
def _has_evidence_anchor(judgment: Judgment, anchor: str) -> bool:
    evidence = judgment.evidence
    if evidence is not None and str(evidence.anchor) == anchor:
        return True
    return any(_has_evidence_anchor(child, anchor) for child in judgment.subjudgments)


def _find_judgment_by_anchor(judgment: Judgment | None, anchor: str) -> Judgment | None:
    if judgment is None:
        return None
    evidence = judgment.evidence
    if evidence is not None and str(evidence.anchor) == anchor:
        return judgment
    for child in judgment.subjudgments:
        found = _find_judgment_by_anchor(child, anchor)
        if found is not None:
            return found
    return None


if __name__ == "__main__":
    unittest.main()
