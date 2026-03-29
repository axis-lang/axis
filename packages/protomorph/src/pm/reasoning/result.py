from __future__ import annotations

from protobase import frozendict

import pm
from pm.foundation import Builtin

from .model import Answer, CycleTrace, DeferredGoal, Judgment, ReasoningValue


class SolverResult(Builtin, abstract=True):
    goal: pm.Spec


class Unique(SolverResult):
    subst: frozendict[pm.Placeholder, ReasoningValue] = frozendict()
    evidence: pm.Spec | None = None
    judgment: Judgment | None = None


class Ambiguous(SolverResult):
    subst: frozendict[pm.Placeholder, ReasoningValue] = frozendict()
    evidence: pm.Spec | None = None
    answers: tuple[Answer, ...] = ()
    judgments: tuple[Judgment, ...] = ()
    reason: str = ""


class NoSolution(SolverResult):
    reason: str = ""
    judgment: Judgment | None = None
    trace: CycleTrace | None = None


class Deferred(SolverResult):
    blocked: tuple[DeferredGoal, ...] = ()
    answers: tuple[Answer, ...] = ()
    judgments: tuple[Judgment, ...] = ()
    reason: str = ""


class Floundered(SolverResult):
    blocked: tuple[DeferredGoal, ...] = ()
    answers: tuple[Answer, ...] = ()
    judgments: tuple[Judgment, ...] = ()
    reason: str = ""


class MixedCycle(SolverResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""
    trace: CycleTrace | None = None
    judgment: Judgment | None = None


class NegativeCycle(SolverResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""
    trace: CycleTrace | None = None
    judgment: Judgment | None = None
