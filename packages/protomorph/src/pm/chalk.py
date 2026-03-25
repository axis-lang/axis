from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from protobase import Consed, flux, frozendict

import pm
from .foundation import Builtin

__all__ = [
    "ChalkDatabase",
    "RuleSet",
    "ChalkSolver",
    "ChalkResult",
    "Unique",
    "Ambiguous",
    "NoSolution",
]

type ChalkValue = pm.Builtin | tuple | frozenset | bool | int | float | str | bytes | None


class ChalkResult(Builtin, abstract=True):
    goal: pm.Spec


class Unique(ChalkResult):
    subst: frozendict[pm.Placeholder, ChalkValue] = frozendict()


class Ambiguous(ChalkResult):
    subst: frozendict[pm.Placeholder, ChalkValue] = frozendict()
    reason: str = ""


class NoSolution(ChalkResult):
    reason: str = ""


class ChalkDatabase(Consed, abstract=True):
    @flux.method
    def rules_for_goal(self, goal: pm.Spec) -> tuple[pm.Rule, ...]:
        raise NotImplementedError

    @flux.method
    def is_coinductive(self, goal: pm.Spec) -> bool:
        return False


class RuleSet(ChalkDatabase):
    rules: tuple[pm.Rule, ...] = ()

    @flux.property
    def rules_by_anchor(self) -> frozendict[str, tuple[pm.Rule, ...]]:
        buckets: dict[str, list[pm.Rule]] = {}
        for rule in self.rules:
            buckets.setdefault(rule.head.anchor, []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.method
    def rules_for_goal(self, goal: pm.Spec) -> tuple[pm.Rule, ...]:
        return self.rules_by_anchor.get(goal.anchor, ())


class ChalkSolver(Consed):
    db: ChalkDatabase
    max_depth: int = 256

    @flux.method
    def solve(self, goal: pm.Spec) -> ChalkResult:
        return _Core(self.db, max_depth=self.max_depth).solve(goal)


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
class _CompiledRule:
    rule: pm.Rule
    head: pm.Carrier
    body: tuple[pm.Carrier, ...]


@dataclass(frozen=True, slots=True)
class _InternalSolution:
    kind: str
    subst: tuple[tuple[int, pm.Carrier], ...] = ()

    @classmethod
    def none(cls) -> _InternalSolution:
        return cls("none")

    @classmethod
    def unique(cls, subst: tuple[tuple[int, pm.Carrier], ...]) -> _InternalSolution:
        return cls("unique", subst)

    @classmethod
    def ambiguous(cls, subst: tuple[tuple[int, pm.Carrier], ...]) -> _InternalSolution:
        return cls("ambiguous", subst)

    @property
    def is_success(self) -> bool:
        return self.kind != "none"

    @property
    def is_ambiguous(self) -> bool:
        return self.kind == "ambiguous"


@dataclass(slots=True)
class _SearchNode:
    solution: _InternalSolution
    active: bool = False


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

        right_var = _runtime_var(right)
        if right_var is not None:
            if _var_priority(left_var) > _var_priority(right_var):
                self._bindings[right_var] = left
            else:
                self._bindings[left_var] = right
            return True

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

    def solve(self, goal: pm.Spec) -> ChalkResult:
        runtime_goal, placeholders = _prepare_query(goal)
        canonical_goal = _canonicalize(runtime_goal, _Bindings())
        solution, _ = self._solve_goal(canonical_goal, depth=0)
        return _public_result(goal, placeholders, canonical_goal, solution)

    def _solve_goal(
        self,
        goal: _CanonicalGoal,
        *,
        depth: int,
    ) -> tuple[_InternalSolution, bool]:
        if depth > self.max_depth:
            return _InternalSolution.ambiguous(()), False

        node = self._nodes.get(goal.key)
        if node is not None:
            if node.active:
                return node.solution, True
            return node.solution, False

        node = _SearchNode(solution=_InternalSolution.none(), active=True)
        self._nodes[goal.key] = node

        while True:
            solution, saw_cycle = self._evaluate_goal(goal, depth=depth)
            if not saw_cycle or solution == node.solution or solution.is_ambiguous:
                node.solution = solution
                node.active = False
                return solution, saw_cycle
            node.solution = solution

    def _evaluate_goal(
        self,
        goal: _CanonicalGoal,
        *,
        depth: int,
    ) -> tuple[_InternalSolution, bool]:
        goal_runtime = _instantiate_goal_term(pm.wrap(goal.key), goal.slots)
        results: list[_InternalSolution] = []
        saw_cycle = False

        for rule in self.db.rules_for_goal(goal.key):
            compiled = self._compile_rule(rule)
            result, branch_cycle = self._apply_rule(
                goal,
                goal_runtime,
                compiled,
                depth=depth,
            )
            if result.is_success:
                results.append(result)
            saw_cycle = saw_cycle or branch_cycle

        return _combine_solutions(results), saw_cycle

    def _apply_rule(
        self,
        goal: _CanonicalGoal,
        goal_runtime: pm.Carrier,
        rule: _CompiledRule,
        *,
        depth: int,
    ) -> tuple[_InternalSolution, bool]:
        owner = self._new_owner()
        bindings = _Bindings()
        head = _instantiate_rule_template(rule.head, owner)

        if not _unify(bindings, goal_runtime, head):
            return _InternalSolution.none(), False

        branch_ambiguous = False
        saw_cycle = False

        for template in rule.body:
            subgoal_carrier = bindings.reify(_instantiate_rule_template(template, owner))
            subgoal = _canonicalize(subgoal_carrier, bindings)
            subresult, subcycle = self._solve_goal(subgoal, depth=depth + 1)
            saw_cycle = saw_cycle or subcycle
            if not subresult.is_success:
                return _InternalSolution.none(), saw_cycle

            next_bindings = _apply_solution(bindings, subgoal, subresult)
            if next_bindings is None:
                return _InternalSolution.none(), saw_cycle
            bindings = next_bindings
            branch_ambiguous = branch_ambiguous or subresult.is_ambiguous

        return _extract_solution(goal, bindings, force_ambiguous=branch_ambiguous), saw_cycle

    def _compile_rule(self, rule: pm.Rule) -> _CompiledRule:
        cached = self._compiled_rules.get(rule)
        if cached is not None:
            return cached

        slot_by_placeholder: dict[pm.Placeholder, int] = {}
        head = _compile_template(pm.wrap(rule.head), slot_by_placeholder)
        body = tuple(_compile_template(pm.wrap(item), slot_by_placeholder) for item in rule.body)
        compiled = _CompiledRule(rule, head, body)
        self._compiled_rules[rule] = compiled
        return compiled

    def _new_owner(self) -> int:
        owner = self._next_owner
        self._next_owner += 1
        return owner


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


def _compile_template(
    carrier: pm.Carrier,
    slot_by_placeholder: dict[pm.Placeholder, int],
) -> pm.Carrier:
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        value = leaf.fetch()
        if not isinstance(value, pm.Placeholder):
            continue
        slot = slot_by_placeholder.get(value)
        if slot is None:
            slot = len(slot_by_placeholder)
            slot_by_placeholder[value] = slot
        mapping[leaf] = pm.LeafCarrier(leaf.descriptor, _TemplateVar(slot))
    return carrier if not mapping else carrier.subst(mapping)


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
        current_left, current_right = stack.pop()
        current_left = bindings.resolve(current_left)
        current_right = bindings.resolve(current_right)

        if current_left == current_right:
            continue

        left_var = _runtime_var(current_left)
        right_var = _runtime_var(current_right)
        if left_var is not None:
            if not bindings.bind(current_left, current_right):
                return False
            continue
        if right_var is not None:
            if not bindings.bind(current_right, current_left):
                return False
            continue

        if current_left.is_leaf or current_right.is_leaf:
            if current_left.is_leaf != current_right.is_leaf:
                return False
            if current_left.descriptor != current_right.descriptor:
                return False
            if current_left.fetch() != current_right.fetch():
                return False
            continue

        left_children = tuple(current_left)
        right_children = tuple(current_right)
        if len(left_children) != len(right_children):
            return False

        stack.extend(zip(reversed(left_children), reversed(right_children)))

    return True


def _apply_solution(
    bindings: _Bindings,
    goal: _CanonicalGoal,
    solution: _InternalSolution,
) -> _Bindings | None:
    next_bindings = bindings.clone()
    for slot, term in solution.subst:
        left = goal.slots[slot]
        right = _instantiate_goal_term(term, goal.slots)
        if not _unify(next_bindings, left, right):
            return None
    return next_bindings


def _extract_solution(
    goal: _CanonicalGoal,
    bindings: _Bindings,
    *,
    force_ambiguous: bool,
) -> _InternalSolution:
    slot_by_var: dict[_RuntimeVar, int] = {}
    for index, slot in enumerate(goal.slots):
        var = _runtime_var(slot)
        if var is not None:
            slot_by_var[var] = index

    subst: list[tuple[int, pm.Carrier]] = []
    ambiguous = force_ambiguous

    for index, slot in enumerate(goal.slots):
        term = bindings.reify(slot)
        projected, has_goal_refs, has_external = _project_term(term, slot_by_var)
        if has_external:
            ambiguous = True
            continue
        if _is_identity_slot(projected, index):
            ambiguous = True
            continue
        if has_goal_refs:
            ambiguous = True
        subst.append((index, projected))

    normalized = _normalize_subst(subst)
    if ambiguous:
        return _InternalSolution.ambiguous(normalized)
    return _InternalSolution.unique(normalized)


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

    if has_external and not mapping:
        return carrier, has_goal_refs, True

    projected = carrier if not mapping else carrier.subst(mapping)
    return projected, has_goal_refs, has_external


def _combine_solutions(results: list[_InternalSolution]) -> _InternalSolution:
    successful = [result for result in results if result.is_success]
    if not successful:
        return _InternalSolution.none()

    first = successful[0]
    if all(result.kind == "unique" and result.subst == first.subst for result in successful):
        return first

    return _InternalSolution.ambiguous(_shared_subst(successful))


def _shared_subst(results: list[_InternalSolution]) -> tuple[tuple[int, pm.Carrier], ...]:
    shared = dict(results[0].subst)
    for result in results[1:]:
        current = dict(result.subst)
        for slot, carrier in tuple(shared.items()):
            if slot not in current or current[slot] != carrier:
                shared.pop(slot)
    return tuple(sorted(shared.items(), key=lambda item: item[0]))


def _normalize_subst(
    items: list[tuple[int, pm.Carrier]],
) -> tuple[tuple[int, pm.Carrier], ...]:
    deduped: dict[int, pm.Carrier] = {}
    for slot, carrier in items:
        deduped[slot] = carrier
    return tuple(sorted(deduped.items(), key=lambda item: item[0]))


def _public_result(
    goal: pm.Spec,
    placeholders: tuple[pm.Placeholder, ...],
    canonical_goal: _CanonicalGoal,
    solution: _InternalSolution,
) -> ChalkResult:
    if solution.kind == "none":
        return NoSolution(goal, "no matching proof")

    subst = _public_subst(placeholders, canonical_goal, solution)
    if solution.kind == "unique":
        return Unique(goal, subst)
    return Ambiguous(goal, subst, "multiple or underconstrained proofs")


def _public_subst(
    placeholders: tuple[pm.Placeholder, ...],
    canonical_goal: _CanonicalGoal,
    solution: _InternalSolution,
) -> frozendict[pm.Placeholder, ChalkValue]:
    replacements: tuple[pm.Carrier, ...] = tuple(
        pm.LeafCarrier(canonical_goal.slots[index].descriptor, placeholder)
        for index, placeholder in enumerate(placeholders)
    )

    items: list[tuple[pm.Placeholder, ChalkValue]] = []
    for slot, carrier in solution.subst:
        if slot >= len(placeholders):
            continue
        instantiated = _instantiate_goal_term(carrier, replacements)
        items.append((placeholders[slot], cast(ChalkValue, instantiated.fetch())))
    return frozendict(items)


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


def _var_priority(var: _RuntimeVar) -> tuple[int, int, int]:
    kind_rank = 0 if var.kind == "goal" else 1
    return (kind_rank, var.owner, var.slot)
