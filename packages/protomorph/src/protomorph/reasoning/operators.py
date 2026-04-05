from __future__ import annotations

from typing import Any, cast, ClassVar

from protobase import _
import protomorph
from protomorph.native import instantiate_builtin
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


class SolverOperator(protomorph.Builtin, abstract=True):
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
    SPEC_NAME = "std.logic.KeyOf"
    target: protomorph.Carrier = _

    @classmethod
    def of(cls, target: Any) -> KeyOfOperator:
        carrier = target if isinstance(target, protomorph.Carrier) else protomorph.wrap(target)
        return cast(KeyOfOperator, cls(target=carrier))


class ProjectionOperator(SolverOperator):
    SPEC_NAME: ClassVar[str] = "std.logic.Proj"
    target: protomorph.Carrier = _
    trait: protomorph.Spec | None = _
    name: str = _

    @classmethod
    def of(cls, target: Any, trait: protomorph.Spec, name: str) -> ProjectionOperator:
        carrier = target if isinstance(target, protomorph.Carrier) else protomorph.wrap(target)
        return cast(
            ProjectionOperator,
            cls(target=carrier, trait=trait, name=name),
        )


class AttrOperator(SolverOperator):
    SPEC_NAME = "std.logic.Attr"
    of_value: protomorph.Carrier = _
    key: protomorph.Id | int = 0

    @classmethod
    def of(cls, of_value: protomorph.Datum, key: protomorph.Id | int | str) -> AttrOperator:
        key_value = protomorph.Id(key) if isinstance(key, str) else key
        carrier = of_value if isinstance(of_value, protomorph.Carrier) else protomorph.wrap(of_value)
        return cast(AttrOperator, cls(of_value=carrier, key=key_value))


class TypeOfOperator(SolverOperator):
    SPEC_NAME = "std.logic.TypeOf"
    of_value: protomorph.Carrier = _

    @classmethod
    def of(cls, of_value: protomorph.Datum) -> TypeOfOperator:
        carrier = of_value if isinstance(of_value, protomorph.Carrier) else protomorph.wrap(of_value)
        return cast(TypeOfOperator, cls(of_value=carrier))


def logic_operator_for(anchor: protomorph.Anchor, args: protomorph.Tuple | None) -> SolverOperator | None:
    if anchor.parent == protomorph.Anchor("std.logic"):
        if args is None or len(args) == 0:
            op_args = protomorph.Tuple.Empty
        else:
            carriers = tuple(args[i] for i in range(len(args) - 1))
            op_args = protomorph.Tuple.Empty if not carriers else protomorph.VaryingType.new(*carriers)
        builtin = instantiate_builtin(anchor, cast(protomorph.Tuple, op_args))
        if isinstance(builtin, SolverOperator):
            return builtin
        return None
    return None


def relation_operator_for(goal: protomorph.Spec) -> SolverOperator | None:
    logic_operator = logic_operator_for(goal.anchor, goal.args)
    if logic_operator is not None:
        return logic_operator

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
    if anchor.endswith("Attr") and len(args) == 3:
        target, key, _ = args
        return AttrOperator.of(target, key)
    if anchor.endswith("TypeOf") and len(args) == 2:
        return TypeOfOperator.of(args[0])
    return None
