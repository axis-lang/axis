from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, cast

import pm
from .foundation import Builtin


# ── Rule ──────────────────────────────────────────────────────────


class Rule(Builtin):
    """A logical rule: *head* holds when every goal in *body* holds."""

    SPEC_NAME = "std.logic.Rule"
    head: pm.Spec
    body: tuple[pm.Spec, ...]


# ── Variable freshening ──────────────────────────────────────────


class _FreshCtx(Builtin):
    """Unique context for per-application variable freshening."""

    SPEC_NAME = "std.logic._FreshCtx"
    tag: int


_fresh_counter: int = 0


def _next_ctx() -> _FreshCtx:
    global _fresh_counter
    _fresh_counter += 1
    return _FreshCtx(_fresh_counter)


def _collect_placeholders(*specs: pm.Spec) -> set[pm.Placeholder]:
    result: set[pm.Placeholder] = set()
    for spec in specs:
        for leaf in pm.wrap(spec).deep_iter():
            data = leaf.fetch()
            if isinstance(data, pm.Placeholder):
                result.add(data)
    return result


def _fresh_placeholder(ph: pm.Placeholder, ctx: _FreshCtx) -> pm.Placeholder:
    """Create a fresh copy of *ph* under a new context."""
    if isinstance(ph, pm.SimpleVar):
        return pm.SimpleVar(ctx, ph.id)
    # Fallback for other Var subtypes: use SimpleVar with fresh ctx.
    if isinstance(ph, pm.Var):
        return pm.SimpleVar(ctx, ph.id)
    return pm.SimpleVar(ctx, "?")


def _freshen_spec(
    spec: pm.Spec,
    rename: dict[pm.Placeholder, pm.Placeholder],
) -> pm.Spec:
    carrier = pm.wrap(spec)
    mapping: dict[pm.Carrier, pm.Carrier] = {}
    for leaf in carrier.deep_iter():
        data = leaf.fetch()
        if isinstance(data, pm.Placeholder) and data in rename:
            mapping[leaf] = pm.LeafCarrier(leaf.descriptor, rename[data])
    if not mapping:
        return spec
    return cast(pm.Spec, carrier.subst(mapping).fetch())


def freshen_rule(rule: Rule) -> tuple[pm.Spec, tuple[pm.Spec, ...]]:
    """Return *(head, body)* with all Placeholders replaced by fresh copies."""
    placeholders = _collect_placeholders(rule.head, *rule.body)
    if not placeholders:
        return rule.head, rule.body
    ctx = _next_ctx()
    rename = {ph: _fresh_placeholder(ph, ctx) for ph in placeholders}
    head = _freshen_spec(rule.head, rename)
    body = tuple(_freshen_spec(s, rename) for s in rule.body)
    return head, body


# ── Step results ─────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Resolved:
    """Goal satisfied."""


@dataclass(frozen=True, slots=True)
class NewGoals:
    """Partial progress — sub-goals must be solved."""

    goals: tuple[pm.Spec, ...]


@dataclass(frozen=True, slots=True)
class Deferred:
    """Blocked on unresolved variables — retry later."""


@dataclass(frozen=True, slots=True)
class Failed:
    """No applicable rule."""

    reason: str = ""


StepResult = Resolved | NewGoals | Deferred | Failed


# ── Solver ───────────────────────────────────────────────────────


class Solver:
    """Goal-directed solver with deferral and backtracking support.

    *rules* are tried in order for each goal.  The first matching rule
    commits its head-bindings into the shared ``UnionFind`` and pushes
    its body as new sub-goals.
    """

    def __init__(
        self,
        rules: list[Rule] | tuple[Rule, ...],
        is_var: Callable[[pm.Carrier], bool],
        *,
        subst: pm.UnionFind | None = None,
        max_iterations: int = 10_000,
    ):
        self.rules = list(rules)
        self.subst = subst or pm.UnionFind(is_var)
        self.pending: deque[pm.Spec] = deque()
        self.deferred: list[pm.Spec] = []
        self._max_iterations = max_iterations
        self._iterations = 0

    # ── public API ────────────────────────────────────────────

    def add_goal(self, *goals: pm.Spec) -> None:
        self.pending.extend(goals)

    def step(self, goal: pm.Spec) -> StepResult:
        """Try to resolve *goal* against the rule set."""
        for rule in self.rules:
            head, body = freshen_rule(rule)
            snap = self.subst.snapshot()

            result = pm.unify(pm.wrap(goal), pm.wrap(head), subst=self.subst)
            if result is None:
                self.subst.rollback(snap)
                continue

            if not body:
                return Resolved()

            sub_goals = tuple(
                cast(pm.Spec, self.subst.reify(pm.wrap(s)).fetch())
                for s in body
            )
            return NewGoals(sub_goals)

        return Failed(f"No rule matches: {goal!r}")

    def solve(self) -> bool:
        """Run the obligation loop to completion.

        Returns ``True`` when all goals (including deferred retries)
        have been resolved.
        """
        while True:
            if not self._drain_pending():
                return False

            if not self.deferred:
                return True

            # Retry deferred goals — must make progress or fail.
            prev_count = len(self.deferred)
            self.pending.extend(self.deferred)
            self.deferred.clear()

            if not self._drain_pending():
                return False

            if not self.deferred:
                return True

            if len(self.deferred) >= prev_count:
                return False  # no progress — ambiguity

            # Made some progress, loop again.

    # ── internals ─────────────────────────────────────────────

    def _drain_pending(self) -> bool:
        """Process all pending goals.  Returns False on failure or limit."""
        while self.pending:
            if self._iterations >= self._max_iterations:
                return False
            self._iterations += 1

            goal = self.pending.popleft()
            goal = cast(pm.Spec, self.subst.reify(pm.wrap(goal)).fetch())

            match self.step(goal):
                case Resolved():
                    pass
                case NewGoals(goals=goals):
                    self.pending.extend(goals)
                case Deferred():
                    self.deferred.append(goal)
                case Failed():
                    return False
        return True
