from __future__ import annotations

from protobase import frozendict

import pm
from pm.foundation import Builtin

NEGATION_ANCHOR = "std.logic.Not"

type ReasoningValue = pm.Carrier | pm.Builtin | tuple | frozenset | bool | int | float | str | bytes | None


def is_negation(goal: pm.Spec) -> bool:
    return str(goal.anchor) == NEGATION_ANCHOR


def unwrap_negation(goal: pm.Spec) -> pm.Spec:
    if not is_negation(goal):
        raise ValueError(f"Expected {NEGATION_ANCHOR}, got {goal.anchor!r}")
    if len(goal.args.content) != 1:
        raise ValueError(f"{NEGATION_ANCHOR} expects exactly one argument")
    inner = goal.args.content[0]
    if not isinstance(inner, pm.Spec):
        raise TypeError(f"{NEGATION_ANCHOR} expects a Spec argument")
    return inner


class Rule(Builtin):
    head: pm.Spec
    body: tuple[pm.Spec, ...] = ()

    @property
    def positive_goals(self) -> tuple[pm.Spec, ...]:
        return tuple(goal for goal in self.body if not is_negation(goal))

    @property
    def negative_goals(self) -> tuple[pm.Spec, ...]:
        return tuple(unwrap_negation(goal) for goal in self.body if is_negation(goal))


class Answer(Builtin):
    goal: pm.Spec
    subst: frozendict[pm.Placeholder, ReasoningValue] = frozendict()
    evidence: pm.Spec | None = None
    judgment: Judgment | None = None


class Judgment(Builtin):
    rel: pm.Spec
    evidence: pm.Spec | None = None
    subjudgments: tuple[Judgment, ...] = ()
    trace: CycleTrace | None = None


class EqClassInfo(Builtin):
    origins: frozenset[pm.Var] = frozenset()
    source_names: frozenset[str] = frozenset()

    def merge(self, other: EqClassInfo) -> EqClassInfo:
        return EqClassInfo(self.origins | other.origins, self.source_names | other.source_names)


class BranchCompletion(Builtin, abstract=True):
    rel: pm.Spec


class DirectCompletion(BranchCompletion):
    pass


class ExpandCompletion(BranchCompletion):
    subject: pm.Spec


class RuleCompletion(BranchCompletion):
    rule_head: pm.Spec


class PendingBranch(Builtin):
    blocked: DeferredGoal
    remaining_goals: tuple[pm.Spec, ...] = ()
    subst: tuple[tuple[int, pm.Carrier], ...] = ()
    slot_info: tuple[EqClassInfo | None, ...] = ()
    blocked_is_negated: bool = False
    completion: BranchCompletion | None = None
    subjudgments: tuple[Judgment, ...] = ()


class Blocker(Builtin, abstract=True):
    pass


class WakeCondition(Builtin, abstract=True):
    pass


class BindingsChanged(WakeCondition):
    placeholders: tuple[pm.Placeholder, ...] = ()


class LocalFactsChanged(WakeCondition):
    anchors: tuple[str, ...] = ()


class StratumClosed(WakeCondition):
    target_stratum: int


class OperatorRetriable(WakeCondition):
    operator: pm.Placeholder


class StratumPending(Blocker):
    target_stratum: int
    blocked_on: pm.Spec


class NonGroundNegation(Blocker):
    blocked_on: pm.Spec


class OperatorPending(Blocker):
    blocked_on: pm.Spec
    operator: pm.Placeholder


class ProjectionBlocked(Blocker):
    blocked_on: pm.Spec
    projection: pm.Spec


class TypeFunctionBlocked(Blocker):
    blocked_on: pm.Spec
    operation: str


class ImplSelectionBlocked(Blocker):
    blocked_on: pm.Spec
    trait: pm.Spec


class DeferredGoal(Builtin):
    goal: pm.Spec
    blocker: Blocker
    evidence: pm.Spec | None = None
    wake_on: tuple[WakeCondition, ...] = ()
    judgment: Judgment | None = None


class CycleMember(Builtin):
    goal: pm.Spec
    coinductive: bool = False
    via_negation: bool = False


class CycleTrace(Builtin):
    members: tuple[CycleMember, ...] = ()
    kind: str = ""
    reason: str = ""
    closes_via_negation: bool = False


class CycleIssue(Builtin, abstract=True):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""
    trace: CycleTrace | None = None

    @property
    def kind(self) -> str:
        if self.trace is not None and self.trace.kind:
            return self.trace.kind
        if isinstance(self, NegativeCycleIssue):
            return "negative"
        if isinstance(self, MixedCycleIssue):
            return "mixed"
        return "cycle"

    @property
    def is_negative(self) -> bool:
        return self.kind == "negative"


class MixedCycleIssue(CycleIssue):
    pass


class NegativeCycleIssue(CycleIssue):
    pass


def default_wake_on(blocker: Blocker) -> tuple[WakeCondition, ...]:
    if isinstance(blocker, StratumPending):
        return (StratumClosed(blocker.target_stratum),)
    if isinstance(blocker, NonGroundNegation):
        return (BindingsChanged(),)
    if isinstance(blocker, OperatorPending):
        return (OperatorRetriable(blocker.operator), BindingsChanged(), LocalFactsChanged())
    if isinstance(blocker, ProjectionBlocked):
        return (BindingsChanged(), LocalFactsChanged())
    if isinstance(blocker, TypeFunctionBlocked):
        return (BindingsChanged(), LocalFactsChanged())
    if isinstance(blocker, ImplSelectionBlocked):
        return (BindingsChanged(), LocalFactsChanged())
    return ()
