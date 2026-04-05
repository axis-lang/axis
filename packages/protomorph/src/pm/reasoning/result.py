from __future__ import annotations

from protobase import frozendict

import pm
from pm import reasoning as urs
from pm.foundation import Builtin


class SolverResult(Builtin, abstract=True):
    goal: pm.Spec


class Unique(SolverResult):
    subst: frozendict[pm.Placeholder, urs.ReasoningValue] = frozendict()
    evidence: pm.Spec | None = None
    judgment: urs.Judgment | None = None


class Ambiguous(SolverResult):
    subst: frozendict[pm.Placeholder, urs.ReasoningValue] = frozendict()
    evidence: pm.Spec | None = None
    answers: tuple[urs.Answer, ...] = ()
    judgments: tuple[urs.Judgment, ...] = ()
    reason: str = ""


class NoSolution(SolverResult):
    reason: str = ""
    judgment: urs.Judgment | None = None
    trace: urs.CycleTrace | None = None


class Deferred(SolverResult):
    blocked: tuple[urs.DeferredGoal, ...] = ()
    answers: tuple[urs.Answer, ...] = ()
    judgments: tuple[urs.Judgment, ...] = ()
    reason: str = ""


class Floundered(SolverResult):
    blocked: tuple[urs.DeferredGoal, ...] = ()
    answers: tuple[urs.Answer, ...] = ()
    judgments: tuple[urs.Judgment, ...] = ()
    reason: str = ""


class MixedCycle(SolverResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""
    trace: urs.CycleTrace | None = None
    judgment: urs.Judgment | None = None


class NegativeCycle(SolverResult):
    cycle: tuple[pm.Spec, ...] = ()
    reason: str = ""
    trace: urs.CycleTrace | None = None
    judgment: urs.Judgment | None = None
