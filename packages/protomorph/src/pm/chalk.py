from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Literal, cast

from protobase import Consed, flux, frozendict

import pm
from .foundation import Builtin

__all__ = [
    "ChalkDatabase",
    "RuleSet",
    "ChalkSolver",
    "ChalkSession",
    "ChalkResult",
    "Unique",
    "Ambiguous",
    "NoSolution",
    "Deferred",
    "Floundered",
    "MixedCycle",
    "NegativeCycle",
    "Answer",
    "DeferredGoal",
    "Blocker",
    "StratumPending",
    "NonGroundNegation",
    "OperatorPending",
    "SolverOperator",
    "KeyOfOperator",
    "ProjectionOperator",
]

type ChalkValue = pm.Builtin | tuple | frozenset | bool | int | float | str | bytes | None


class Answer(Builtin):
    goal: pm.Spec
    subst: frozendict[pm.Placeholder, ChalkValue] = frozendict()
    evidence: pm.Spec | None = None


class ChalkResult(Builtin, abstract=True):
    goal: pm.Spec


class Blocker(Builtin, abstract=True):
    pass


class StratumPending(Blocker):
    target_stratum: int
    blocked_on: pm.Spec


class NonGroundNegation(Blocker):
    blocked_on: pm.Spec


class OperatorPending(Blocker):
    blocked_on: pm.Spec
    operator: pm.Placeholder


class DeferredGoal(Builtin):
    goal: pm.Spec
    blocker: Blocker
    evidence: pm.Spec | None = None


class Unique(ChalkResult):
    subst: frozendict[pm.Placeholder, ChalkValue] = frozendict()
    evidence: pm.Spec | None = None


class Ambiguous(ChalkResult):
    subst: frozendict[pm.Placeholder, ChalkValue] = frozendict()
    evidence: pm.Spec | None = None
    reason: str = ""


class NoSolution(ChalkResult):
    reason: str = ""


class Deferred(ChalkResult):
    blocked: tuple[DeferredGoal, ...] = ()
    answers: tuple[Answer, ...] = ()
    reason: str = ""


class Floundered(ChalkResult):
    blocked: tuple[DeferredGoal, ...] = ()
    answers: tuple[Answer, ...] = ()
    reason: str = ""


class MixedCycle(ChalkResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""


class NegativeCycle(ChalkResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""


class SolverOperator(pm.SimpleVar, abstract=True):
    pass


class KeyOfOperator(SolverOperator):
    @classmethod
    def of(cls, target: Any) -> KeyOfOperator:
        return cast(KeyOfOperator, cls(None, f"keyof:{target!r}"))


class ProjectionOperator(SolverOperator):
    trait: pm.Spec
    name: str


class StratificationPlan(Builtin):
    by_anchor: frozendict[str, int] = frozendict()
    negative_cycle_anchors: frozenset[str] = frozenset()

    def stratum_of(self, anchor: str) -> int:
        return self.by_anchor.get(anchor, 0)

    def has_negative_cycle(self, anchor: str) -> bool:
        return anchor in self.negative_cycle_anchors


class ChalkDatabase(Consed, abstract=True):
    @flux.method
    def rules_for_goal(self, goal: pm.Spec) -> tuple[pm.Rule, ...]:
        raise NotImplementedError

    @flux.method
    def is_coinductive(self, goal: pm.Spec) -> bool:
        return False

    @flux.method
    def stratification(self) -> StratificationPlan:
        return StratificationPlan()

    @flux.method
    def operator_result(
        self,
        operator: SolverOperator,
        goal: pm.Spec,
    ) -> tuple[pm.Spec, ...] | DeferredGoal:
        return DeferredGoal(goal, OperatorPending(goal, operator))


class RuleSet(ChalkDatabase):
    rules: tuple[pm.Rule, ...] = ()
    coinductive_anchors: frozenset[str] = frozenset()

    @flux.property
    def rules_by_anchor(self) -> frozendict[str, tuple[pm.Rule, ...]]:
        buckets: dict[str, list[pm.Rule]] = {}
        for rule in self.rules:
            buckets.setdefault(rule.head.anchor, []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.method
    def rules_for_goal(self, goal: pm.Spec) -> tuple[pm.Rule, ...]:
        return self.rules_by_anchor.get(goal.anchor, ())

    @flux.method
    def is_coinductive(self, goal: pm.Spec) -> bool:
        return goal.anchor in self.coinductive_anchors

    @flux.property
    def stratification_plan(self) -> StratificationPlan:
        positive: dict[str, set[str]] = {}
        negative: dict[str, set[str]] = {}
        anchors = {rule.head.anchor for rule in self.rules}

        for rule in self.rules:
            head = rule.head.anchor
            positive.setdefault(head, set())
            negative.setdefault(head, set())
            for item in rule.body:
                if item.anchor == "std.logic.Not":
                    inner = item.args.content[0]
                    if isinstance(inner, pm.Spec):
                        negative[head].add(inner.anchor)
                        anchors.add(inner.anchor)
                    continue
                positive[head].add(item.anchor)
                anchors.add(item.anchor)

        by_anchor = {anchor: 0 for anchor in anchors}
        changed = True
        while changed:
            changed = False
            for head in anchors:
                current = by_anchor[head]
                next_value = current
                for dep in positive.get(head, ()):
                    next_value = max(next_value, by_anchor[dep])
                for dep in negative.get(head, ()):
                    next_value = max(next_value, by_anchor[dep] + 1)
                if next_value != current:
                    by_anchor[head] = next_value
                    changed = True

        negative_cycle_anchors = {
            anchor
            for anchor, deps in negative.items()
            if anchor in deps
        }
        return StratificationPlan(frozendict(by_anchor.items()), frozenset(negative_cycle_anchors))

    @flux.method
    def stratification(self) -> StratificationPlan:
        return self.stratification_plan


class ChalkSolver(Consed):
    db: ChalkDatabase
    max_depth: int = 256

    @flux.method
    def solve(self, goal: pm.Spec) -> ChalkResult:
        return self.session().solve(goal)

    @flux.method
    def answers(self, goal: pm.Spec) -> tuple[Answer, ...]:
        result = self.solve(goal)
        if isinstance(result, Unique):
            return (Answer(goal, result.subst, result.evidence),)
        if isinstance(result, Deferred):
            return result.answers
        if isinstance(result, Floundered):
            return result.answers
        return ()

    @flux.method
    def session(self) -> ChalkSession:
        return ChalkSession(self.db, max_depth=self.max_depth)


class ChalkSession(Builtin):
    db: ChalkDatabase
    max_depth: int = 256

    def solve(self, goal: pm.Spec) -> ChalkResult:
        return _Core(self.db, max_depth=self.max_depth).solve(goal)

    def answers(self, goal: pm.Spec) -> tuple[Answer, ...]:
        result = self.solve(goal)
        if isinstance(result, Unique):
            return (Answer(goal, result.subst, result.evidence),)
        if isinstance(result, Deferred):
            return result.answers
        if isinstance(result, Floundered):
            return result.answers
        return ()


@dataclass(frozen=True, slots=True)
class _TemplateVar:
    slot: int


@dataclass(frozen=True, slots=True)
class _GoalSlot:
    slot: int


@dataclass(frozen=True, slots=True)
class _RuntimeVar:
    kind: str
    owner: int
    slot: int


@dataclass(frozen=True, slots=True)
class _CanonicalGoal:
    key: pm.Spec
    slots: tuple[pm.Carrier, ...]


@dataclass(frozen=True, slots=True)
class _CompiledLiteral:
    kind: Literal["pos", "neg"]
    term: pm.Carrier


@dataclass(frozen=True, slots=True)
class _CompiledRule:
    rule: pm.Rule
    head: pm.Carrier
    body: tuple[_CompiledLiteral, ...]


@dataclass(frozen=True, slots=True)
class _AnswerData:
    subst: tuple[tuple[int, pm.Carrier], ...]
    evidence: pm.Spec | None = None


@dataclass(frozen=True, slots=True)
class _GoalOutcome:
    kind: Literal["failed", "solved", "deferred", "floundered", "mixed_cycle", "negative_cycle"]
    answers: tuple[_AnswerData, ...] = ()
    deferred: tuple[DeferredGoal, ...] = ()
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""

    @classmethod
    def failed(cls, reason: str = "") -> _GoalOutcome:
        return cls("failed", (), (), (), reason)

    @classmethod
    def solved(cls, answers: tuple[_AnswerData, ...], reason: str = "") -> _GoalOutcome:
        return cls("solved", answers, (), (), reason)

    @classmethod
    def deferred_outcome(
        cls,
        answers: tuple[_AnswerData, ...],
        deferred: tuple[DeferredGoal, ...],
        reason: str = "",
    ) -> _GoalOutcome:
        return cls("deferred", answers, deferred, (), reason)

    @classmethod
    def floundered_outcome(
        cls,
        answers: tuple[_AnswerData, ...],
        deferred: tuple[DeferredGoal, ...],
        reason: str = "",
    ) -> _GoalOutcome:
        return cls("floundered", answers, deferred, (), reason)

    @classmethod
    def mixed_cycle_outcome(cls, cycle: tuple[pm.Spec, ...], reason: str = "") -> _GoalOutcome:
        return cls("mixed_cycle", (), (), cycle, reason)

    @classmethod
    def negative_cycle_outcome(cls, cycle: tuple[pm.Spec, ...], reason: str = "") -> _GoalOutcome:
        return cls("negative_cycle", (), (), cycle, reason)


@dataclass(frozen=True, slots=True)
class _SearchNode:
    outcome: _GoalOutcome
    active: bool = False
    coinductive: bool = False


class _Bindings:
    __slots__ = ("_bindings",)

    def __init__(self, bindings: dict[_RuntimeVar, pm.Carrier] | None = None):
        self._bindings = {} if bindings is None else bindings

    def clone(self) -> _Bindings:
        return _Bindings(self._bindings.copy())

    def resolve(self, carrier: pm.Carrier) -> pm.Carrier:
        current = carrier
        while True:
            var = _runtime_var(current)
            if var is None:
                return current
            nxt = self._bindings.get(var)
            if nxt is None or nxt == current:
                return current
            current = nxt

    def bind(self, var_carrier: pm.Carrier, term: pm.Carrier) -> bool:
        left = self.resolve(var_carrier)
        right = self.resolve(term)
        if left == right:
            return True
        left_var = _runtime_var(left)
        if left_var is None:
            raise TypeError("bind() expects a runtime variable on the left")
        if self._occurs(left_var, right):
            return False
        self._bindings[left_var] = right
        return True

    def reify(self, carrier: pm.Carrier) -> pm.Carrier:
        carrier = self.resolve(carrier)
        if carrier.is_leaf:
            return carrier
        children = tuple(self.reify(child) for child in carrier)
        if all(before == after for before, after in zip(carrier, children, strict=True)):
            return carrier
        return carrier.reconstruct(children)

    def _occurs(self, var: _RuntimeVar, carrier: pm.Carrier) -> bool:
        carrier = self.resolve(carrier)
        other = _runtime_var(carrier)
        if other is not None:
            return other == var
        if carrier.is_leaf:
            return False
        return any(self._occurs(var, child) for child in carrier)


class _Core:
    def __init__(self, db: ChalkDatabase, *, max_depth: int):
        self.db = db
        self.max_depth = max_depth
        self._compiled_rules: dict[pm.Rule, _CompiledRule] = {}
        self._nodes: dict[pm.Spec, _SearchNode] = {}
        self._next_owner = 1
        self._stratification = db.stratification()
        self._closed_strata: set[int] = set()
        self._pending: deque[pm.Spec] = deque()
        self._deferred: dict[pm.Spec, DeferredGoal] = {}

    def solve(self, goal: pm.Spec) -> ChalkResult:
        runtime_goal, placeholders = _prepare_query(goal)
        canonical = _canonicalize(runtime_goal, _Bindings())
        outcome = self._solve_goal(canonical, depth=0)
        answers = _public_answers(goal, placeholders, canonical, outcome.answers)

        if outcome.kind == "mixed_cycle":
            return MixedCycle(goal, outcome.cycle, outcome.reason or "mixed inductive/coinductive cycle")
        if outcome.kind == "negative_cycle":
            return NegativeCycle(goal, outcome.cycle, outcome.reason or "negative cycle")
        if outcome.kind == "failed":
            return NoSolution(goal, outcome.reason or "no matching proof")
        if outcome.kind == "floundered":
            return Floundered(goal, outcome.deferred, answers, outcome.reason or "floundered")
        if outcome.kind == "deferred":
            return Deferred(goal, outcome.deferred, answers, outcome.reason or "deferred")

        if len(answers) == 1:
            answer = answers[0]
            return Unique(goal, answer.subst, answer.evidence)
        if len(answers) > 1:
            return Ambiguous(goal, _shared_public_subst(answers), _shared_public_evidence(answers), "multiple answers")
        return NoSolution(goal, outcome.reason or "no matching proof")

    def _solve_goal(self, goal: _CanonicalGoal, *, depth: int) -> _GoalOutcome:
        if depth > self.max_depth:
            return _GoalOutcome.deferred_outcome((), (DeferredGoal(goal.key, StratumPending(0, goal.key)),), "maximum recursion depth reached")

        if self._stratification.has_negative_cycle(goal.key.anchor):
            return _GoalOutcome.negative_cycle_outcome((goal.key,), "negative cycle in stratum")

        node = self._nodes.get(goal.key)
        if node is not None:
            if node.active:
                if not node.coinductive and any(active_node.coinductive for active_node in self._nodes.values() if active_node.active):
                    return _GoalOutcome.mixed_cycle_outcome((goal.key,), "mixed inductive/coinductive cycle")
                if self.db.is_coinductive(goal.key) != node.coinductive:
                    return _GoalOutcome.mixed_cycle_outcome((goal.key,), "mixed inductive/coinductive cycle")
                return node.outcome
            return node.outcome

        coinductive = self.db.is_coinductive(goal.key)
        self._nodes[goal.key] = _SearchNode(_GoalOutcome.failed(), True, coinductive)

        outcomes: list[_GoalOutcome] = []
        for rule in self.db.rules_for_goal(goal.key):
            compiled = self._compile_rule(rule)
            outcome = self._apply_rule(goal, compiled, depth=depth)
            outcomes.append(outcome)

        if any(outcome.kind == "mixed_cycle" for outcome in outcomes):
            combined = _GoalOutcome.mixed_cycle_outcome((goal.key,), "mixed inductive/coinductive cycle")
            self._nodes[goal.key] = _SearchNode(combined, False, coinductive)
            return combined

        combined = _combine_outcomes(goal.key, outcomes)
        self._nodes[goal.key] = _SearchNode(combined, False, coinductive)
        return combined

    def _apply_rule(self, goal: _CanonicalGoal, rule: _CompiledRule, *, depth: int) -> _GoalOutcome:
        owner = self._new_owner()
        bindings = _Bindings()
        goal_runtime = _instantiate_goal_term(pm.wrap(goal.key), goal.slots)
        head = _instantiate_rule_template(rule.head, owner)
        if not _unify(bindings, goal_runtime, head):
            return _GoalOutcome.failed()

        if _contains_solver_operator(goal_runtime) or _contains_solver_operator(head):
            deferred_goal = _operator_deferred(self.db, goal.key)
            if deferred_goal is not None:
                return _GoalOutcome.deferred_outcome((), (deferred_goal,), "deferred")

        evidence: list[pm.Spec] = []
        deferred: list[DeferredGoal] = []

        for literal in rule.body:
            literal_term = bindings.reify(_instantiate_rule_template(literal.term, owner))
            literal_goal = _canonicalize(literal_term, bindings)

            operator_deferred = _operator_deferred(self.db, literal_goal.key)
            if operator_deferred is not None:
                deferred.append(operator_deferred)
                continue

            if literal.kind == "neg":
                if _contains_goal_slots(pm.wrap(literal_goal.key)):
                    deferred.append(DeferredGoal(literal_goal.key, NonGroundNegation(literal_goal.key)))
                    continue

                blocked_stratum = self._negation_blocker(literal_goal.key)
                if blocked_stratum is not None:
                    deferred.append(DeferredGoal(literal_goal.key, blocked_stratum))
                    continue

                outcome = self._solve_goal(literal_goal, depth=depth + 1)
                if outcome.kind == "solved" and outcome.answers:
                    return _GoalOutcome.failed("negative goal disproved")
                if outcome.kind in {"mixed_cycle", "negative_cycle"}:
                    return outcome
                evidence.append(_evidence_negation(literal_goal.key))
                continue

            outcome = self._solve_goal(literal_goal, depth=depth + 1)
            if outcome.kind == "failed":
                return outcome
            if outcome.kind in {"mixed_cycle", "negative_cycle"}:
                return outcome
            if outcome.kind in {"deferred", "floundered"}:
                deferred.extend(outcome.deferred)
                continue
            if not outcome.answers:
                return _GoalOutcome.failed("subgoal produced no answers")
            evidence.append(outcome.answers[0].evidence or _evidence_unknown(literal_goal.key))

        answer = _extract_answer(goal, bindings, rule.rule, tuple(evidence))
        if deferred:
            if any(isinstance(item.blocker, NonGroundNegation) for item in deferred):
                return _GoalOutcome.floundered_outcome((answer,), tuple(deferred), "floundered")
            return _GoalOutcome.deferred_outcome((answer,), tuple(deferred), "deferred")
        return _GoalOutcome.solved((answer,))

    def _negation_blocker(self, goal: pm.Spec) -> StratumPending | None:
        stratum = self._stratification.stratum_of(goal.anchor)
        if stratum in self._closed_strata:
            return None
        return StratumPending(stratum, goal)

    def _compile_rule(self, rule: pm.Rule) -> _CompiledRule:
        cached = self._compiled_rules.get(rule)
        if cached is not None:
            return cached
        slot_by_placeholder: dict[pm.Placeholder, int] = {}
        head = _compile_template(pm.wrap(rule.head), slot_by_placeholder)
        body = tuple(_compile_literal(item, slot_by_placeholder) for item in rule.body)
        compiled = _CompiledRule(rule, head, body)
        self._compiled_rules[rule] = compiled
        return compiled

    def _new_owner(self) -> int:
        owner = self._next_owner
        self._next_owner += 1
        return owner


def _combine_outcomes(goal: pm.Spec, outcomes: list[_GoalOutcome]) -> _GoalOutcome:
    if any(outcome.kind == "negative_cycle" for outcome in outcomes):
        return _GoalOutcome.negative_cycle_outcome((goal,), "negative cycle")
    if any(outcome.kind == "mixed_cycle" for outcome in outcomes):
        return _GoalOutcome.mixed_cycle_outcome((goal,), "mixed inductive/coinductive cycle")

    answers: list[_AnswerData] = []
    deferred: list[DeferredGoal] = []
    kinds = {outcome.kind for outcome in outcomes}
    for outcome in outcomes:
        answers.extend(outcome.answers)
        deferred.extend(outcome.deferred)

    deduped = _dedupe_answers(tuple(answers))
    if deferred:
        if any(isinstance(item.blocker, NonGroundNegation) for item in deferred):
            return _GoalOutcome.floundered_outcome(deduped, tuple(_dedupe_deferred(deferred)), "floundered")
        return _GoalOutcome.deferred_outcome(deduped, tuple(_dedupe_deferred(deferred)), "deferred")
    if deduped:
        return _GoalOutcome.solved(deduped)
    if "failed" in kinds:
        return _GoalOutcome.failed()
    return _GoalOutcome.failed()


def _dedupe_deferred(items: list[DeferredGoal]) -> list[DeferredGoal]:
    seen: dict[tuple[str, str], DeferredGoal] = {}
    for item in items:
        key = (repr(item.goal), repr(item.blocker))
        seen[key] = item
    return list(seen.values())


def _prepare_query(goal: pm.Spec) -> tuple[pm.Carrier, tuple[pm.Placeholder, ...]]:
    placeholder_by_value: dict[pm.Placeholder, int] = {}
    placeholders: list[pm.Placeholder] = []
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in pm.wrap(goal).deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        slot = placeholder_by_value.get(value)
        if slot is None:
            slot = len(placeholders)
            placeholder_by_value[value] = slot
            placeholders.append(value)
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _RuntimeVar("goal", 0, slot))
    carrier = pm.wrap(goal) if not mapping else pm.wrap(goal).subst(mapping)
    return carrier, tuple(placeholders)


def _compile_template(carrier: pm.Carrier, slot_by_placeholder: dict[pm.Placeholder, int]) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if isinstance(value, SolverOperator):
            continue
        if not isinstance(value, pm.Placeholder):
            continue
        slot = slot_by_placeholder.get(value)
        if slot is None:
            slot = len(slot_by_placeholder)
            slot_by_placeholder[value] = slot
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _TemplateVar(slot))
    return carrier if not mapping else carrier.subst(mapping)


def _compile_literal(spec: pm.Spec, slot_by_placeholder: dict[pm.Placeholder, int]) -> _CompiledLiteral:
    if spec.anchor == "std.logic.Not":
        inner = spec.args.content[0]
        if not isinstance(inner, pm.Spec):
            raise TypeError("std.logic.Not expects a Spec argument")
        return _CompiledLiteral("neg", _compile_template(pm.wrap(inner), slot_by_placeholder))
    return _CompiledLiteral("pos", _compile_template(pm.wrap(spec), slot_by_placeholder))


def _instantiate_rule_template(carrier: pm.Carrier, owner: int) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, _TemplateVar):
            continue
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _RuntimeVar("rule", owner, value.slot))
    return carrier if not mapping else carrier.subst(mapping)


def _instantiate_goal_term(carrier: pm.Carrier, slots: tuple[pm.Carrier, ...]) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if isinstance(value, _GoalSlot):
            mapping[leaf] = slots[value.slot]
    return carrier if not mapping else carrier.subst(mapping)


def _canonicalize(carrier: pm.Carrier, bindings: _Bindings) -> _CanonicalGoal:
    carrier = bindings.reify(carrier)
    slot_by_var: dict[_RuntimeVar, int] = {}
    slots: list[pm.Carrier] = []
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        var = _runtime_var(leaf)
        if var is None:
            continue
        slot = slot_by_var.get(var)
        if slot is None:
            slot = len(slots)
            slot_by_var[var] = slot
            slots.append(leaf)
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _GoalSlot(slot))
    key_carrier = carrier if not mapping else carrier.subst(mapping)
    return _CanonicalGoal(cast(pm.Spec, key_carrier.fetch()), tuple(slots))


def _unify(bindings: _Bindings, left: pm.Carrier, right: pm.Carrier) -> bool:
    stack: list[tuple[pm.Carrier, pm.Carrier]] = [(left, right)]
    while stack:
        left, right = stack.pop()
        left = bindings.resolve(left)
        right = bindings.resolve(right)
        if left == right:
            continue
        left_var = _runtime_var(left)
        right_var = _runtime_var(right)
        if left_var is not None:
            if not bindings.bind(left, right):
                return False
            continue
        if right_var is not None:
            if not bindings.bind(right, left):
                return False
            continue
        if left.is_leaf or right.is_leaf:
            if left.is_leaf != right.is_leaf:
                return False
            if left.descriptor != right.descriptor:
                return False
            if left.fetch() != right.fetch():
                return False
            continue
        left_children = tuple(left)
        right_children = tuple(right)
        if len(left_children) != len(right_children):
            return False
        stack.extend(zip(reversed(left_children), reversed(right_children)))
    return True


def _extract_answer(
    goal: _CanonicalGoal,
    bindings: _Bindings,
    rule: pm.Rule,
    evidence: tuple[pm.Spec, ...],
) -> _AnswerData:
    slot_by_var: dict[_RuntimeVar, int] = {}
    for index, slot in enumerate(goal.slots):
        var = _runtime_var(slot)
        if var is not None:
            slot_by_var[var] = index

    subst: list[tuple[int, pm.Carrier]] = []
    for index, slot in enumerate(goal.slots):
        term = bindings.reify(slot)
        projected, _, has_external = _project_term(term, slot_by_var)
        if has_external:
            continue
        if _is_identity_slot(projected, index):
            continue
        subst.append((index, projected))

    node_evidence = _evidence_fact(rule) if not rule.body else _evidence_rule(rule, evidence)
    return _AnswerData(_normalize_subst(subst), node_evidence)


def _project_term(
    carrier: pm.Carrier,
    slot_by_var: dict[_RuntimeVar, int],
) -> tuple[pm.Carrier, bool, bool]:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    has_goal_refs = False
    has_external = False
    for leaf in carrier.deep_iter():
        var = _runtime_var(leaf)
        if var is None:
            continue
        slot = slot_by_var.get(var)
        if slot is None:
            has_external = True
            continue
        has_goal_refs = True
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _GoalSlot(slot))
    projected = carrier if not mapping else carrier.subst(mapping)
    return projected, has_goal_refs, has_external


def _dedupe_answers(answers: tuple[_AnswerData, ...]) -> tuple[_AnswerData, ...]:
    seen: dict[tuple[tuple[int, str], ...], _AnswerData] = {}
    for answer in answers:
        key = tuple((slot, repr(term.fetch())) for slot, term in answer.subst)
        seen[key] = answer
    return tuple(seen.values())


def _public_answers(
    goal: pm.Spec,
    placeholders: tuple[pm.Placeholder, ...],
    canonical_goal: _CanonicalGoal,
    answers: tuple[_AnswerData, ...],
) -> tuple[Answer, ...]:
    return tuple(
        Answer(goal, _public_subst(placeholders, canonical_goal, answer), answer.evidence)
        for answer in answers
    )


def _public_subst(
    placeholders: tuple[pm.Placeholder, ...],
    canonical_goal: _CanonicalGoal,
    answer: _AnswerData,
) -> frozendict[pm.Placeholder, ChalkValue]:
    replacements: tuple[pm.Carrier, ...] = tuple(
        pm.LeafCarrier(canonical_goal.slots[index].descriptor, placeholder)
        for index, placeholder in enumerate(placeholders)
    )
    items: list[tuple[pm.Placeholder, ChalkValue]] = []
    for slot, carrier in answer.subst:
        if slot >= len(placeholders):
            continue
        instantiated = _instantiate_goal_term(carrier, replacements)
        items.append((placeholders[slot], cast(ChalkValue, instantiated.fetch())))
    return frozendict(items)


def _shared_public_subst(answers: tuple[Answer, ...]) -> frozendict[pm.Placeholder, ChalkValue]:
    if not answers:
        return frozendict()
    shared = dict(answers[0].subst)
    for answer in answers[1:]:
        current = dict(answer.subst)
        for key, value in tuple(shared.items()):
            if key not in current or current[key] != value:
                shared.pop(key)
    return frozendict(shared.items())


def _shared_public_evidence(answers: tuple[Answer, ...]) -> pm.Spec | None:
    if not answers:
        return None
    first = answers[0].evidence
    if all(answer.evidence == first for answer in answers):
        return first
    return None


def _evidence_fact(rule: pm.Rule) -> pm.Spec:
    return pm.Spec.of("std.logic.ByFact", rule.head)


def _evidence_rule(rule: pm.Rule, subproofs: tuple[pm.Spec, ...]) -> pm.Spec:
    descriptor = pm.VaryingType(tuple(item.metatype() for item in subproofs))
    return pm.Spec.of("std.logic.ByRule", rule.head, pm.Tuple(descriptor, subproofs))


def _evidence_negation(goal: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByNegation", goal)


def _evidence_unknown(goal: pm.Spec) -> pm.Spec:
    return pm.Spec.of("std.logic.ByUnknown", goal)


def _runtime_var(carrier: pm.Carrier) -> _RuntimeVar | None:
    if not carrier.is_leaf:
        return None
    value = carrier.fetch()
    return value if isinstance(value, _RuntimeVar) else None


def _is_identity_slot(carrier: pm.Carrier, slot: int) -> bool:
    if not carrier.is_leaf:
        return False
    value = carrier.fetch()
    return isinstance(value, _GoalSlot) and value.slot == slot


def _contains_goal_slots(carrier: pm.Carrier) -> bool:
    for leaf in carrier.deep_iter():
        if leaf.is_leaf and isinstance(leaf.fetch(), _GoalSlot):
            return True
    return False


def _contains_solver_operator(carrier: pm.Carrier) -> bool:
    for leaf in carrier.deep_iter():
        if leaf.is_leaf and isinstance(leaf.fetch(), SolverOperator):
            return True
    return False


def _operator_deferred(db: ChalkDatabase, goal: pm.Spec) -> DeferredGoal | None:
    for leaf in pm.wrap(goal).deep_iter():
        value = leaf.fetch()
        if isinstance(value, SolverOperator):
            return DeferredGoal(goal, OperatorPending(goal, value))
    return None


def _normalize_subst(items: list[tuple[int, pm.Carrier]]) -> tuple[tuple[int, pm.Carrier], ...]:
    deduped: dict[int, pm.Carrier] = {}
    for slot, carrier in items:
        deduped[slot] = carrier
    return tuple(sorted(deduped.items(), key=lambda item: item[0]))
