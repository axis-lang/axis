from __future__ import annotations

from typing import Any, cast

import pm
from pm import reasoning as urs
from pm.foundation import Builtin

from .model import DeferredGoal, Judgment, OperatorPending, default_wake_on


class LogicOpStep(Builtin, abstract=True):
    pass


class OpExpand(LogicOpStep):
    goals: tuple[pm.Spec, ...] = ()


class OpAnswer(LogicOpStep):
    answers: tuple[urs.Answer, ...] = ()


class OpBind(LogicOpStep):
    subst: tuple[tuple[int, urs.ReasoningValue], ...] = ()
    evidence: pm.Spec | None = None


class OpDeferred(LogicOpStep):
    blocked: urs.DeferredGoal


class OpFailed(LogicOpStep):
    reason: str = ""


class SolverOperator(pm.SimpleVar, abstract=True):
    def eval(self, *, goal: pm.Spec, session: urs.Session, db: urs.Database) -> urs.LogicOpStep:
        evaluator = getattr(db, "eval_logic_op", None)
        if callable(evaluator):
            result = evaluator(self, goal=goal, session=session)
            if isinstance(result, LogicOpStep):
                return result
        blocker = OperatorPending(goal, self)
        evidence = pm.Spec.of("std.logic.ByDeferred", goal, blocker)
        return OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))


class KeyOfOperator(SolverOperator):
    @classmethod
    def of(cls, target: Any) -> KeyOfOperator:
        return cast(KeyOfOperator, cls(None, f"keyof:{target!r}"))


class ProjectionOperator(SolverOperator):
    @classmethod
    def of(cls, target: Any, trait: pm.Spec, name: str) -> ProjectionOperator:
        return cast(ProjectionOperator, cls(None, f"proj:{target!r}:{trait!r}:{name}"))


def relation_operator_for(goal: pm.Spec) -> SolverOperator | None:
    anchor = str(goal.anchor)
    args = goal.args.content
    if anchor.endswith("KeyOf") and len(args) == 2:
        return KeyOfOperator.of(args[0])
    if anchor.endswith("Proj") and len(args) == 3:
        target, name, _ = args
        if isinstance(name, str):
            return ProjectionOperator.of(target, pm.Spec.of("std.logic.UnknownTrait"), name)
    if anchor.endswith("Proj") and len(args) == 4:
        target, trait, name, _ = args
        if isinstance(trait, pm.Spec) and isinstance(name, str):
            return ProjectionOperator.of(target, trait, name)
    return None
