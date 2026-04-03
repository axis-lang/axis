from __future__ import annotations

from typing import Any, cast

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Builtin

from .model import DeferredGoal, Judgment, OperatorPending, default_wake_on


class LogicOpStep(Builtin, abstract=True):
    pass


class OpExpand(LogicOpStep):
    goals: tuple[protomorph.Spec, ...] = ()


class OpAnswer(LogicOpStep):
    answers: tuple[urs.Answer, ...] = ()


class OpBind(LogicOpStep):
    subst: tuple[tuple[int, urs.ReasoningValue], ...] = ()
    evidence: protomorph.Spec | None = None


class OpDeferred(LogicOpStep):
    blocked: urs.DeferredGoal


class OpFailed(LogicOpStep):
    reason: str = ""


class SolverOperator(protomorph.Placeholder, abstract=True):
    ctx: Builtin | None
    id: str

    def display_label(self) -> str | None:
        return self.id

    def eval(self, *, goal: protomorph.Spec, session: urs.Session, realm: protomorph.Realm) -> urs.LogicOpStep:
        evaluator = getattr(realm, "eval_logic_op", None)
        if callable(evaluator):
            result = evaluator(self, goal=goal, session=session)
            if isinstance(result, LogicOpStep):
                return result
        blocker = OperatorPending(goal, self)
        evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
        return OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))


class KeyOfOperator(SolverOperator):
    @classmethod
    def of(cls, target: Any) -> KeyOfOperator:
        return cast(KeyOfOperator, cls(None, f"keyof:{target!r}"))


class ProjectionOperator(SolverOperator):
    @classmethod
    def of(cls, target: Any, trait: protomorph.Spec, name: str) -> ProjectionOperator:
        return cast(ProjectionOperator, cls(None, f"proj:{target!r}:{trait!r}:{name}"))


def relation_operator_for(goal: protomorph.Spec) -> SolverOperator | None:
    anchor = goal.anchor
    args = goal.args.content
    if anchor.endswith("KeyOf") and len(args) == 2:
        return KeyOfOperator.of(args[0])
    if anchor.endswith("Proj") and len(args) == 3:
        target, name, _ = args
        if isinstance(name, str):
            return ProjectionOperator.of(target, protomorph.Spec.of("std.logic.UnknownTrait"), name)
    if anchor.endswith("Proj") and len(args) == 4:
        target, trait, name, _ = args
        if isinstance(trait, protomorph.Spec) and isinstance(name, str):
            return ProjectionOperator.of(target, trait, name)
    return None
