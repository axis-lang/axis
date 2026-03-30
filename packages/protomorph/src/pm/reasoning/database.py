from __future__ import annotations

from protobase import Consed, flux, frozendict

import pm
from pm import reasoning as urs
from pm.hosted import Host

from .model import DeferredGoal, Judgment, OperatorPending, ProjectionBlocked, TypeFunctionBlocked, default_wake_on


class Database(Consed, abstract=True):
    @flux.property
    def anchors(self) -> frozenset[str]:
        raise NotImplementedError

    @flux.method
    def rules_for_anchor(self, anchor: str) -> tuple[urs.Rule, ...]:
        raise NotImplementedError

    @flux.method
    def facts_by_anchor(self, anchor: str) -> tuple[pm.Spec, ...]:
        raise NotImplementedError

    @flux.method
    def is_coinductive_anchor(self, anchor: str) -> bool:
        return False

    @flux.method
    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        raise NotImplementedError

    @flux.method
    def eval_logic_op(
        self,
        operator: pm.Placeholder,
        *,
        goal: pm.Spec,
        session: urs.Session,
    ) -> urs.LogicOpStep | None:
        raise NotImplementedError


class RuleSetDatabase(Database):
    rules: tuple[urs.Rule, ...] = ()
    facts: tuple[pm.Spec, ...] = ()
    coinductive_anchors: frozenset[str] = frozenset()
    host: Host = pm.NATIVE_HOST

    @flux.property
    def rule_index(self) -> frozendict[str, tuple[urs.Rule, ...]]:
        buckets: dict[str, list[urs.Rule]] = {}
        for rule in self.rules:
            buckets.setdefault(str(rule.head.anchor), []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def fact_index(self) -> frozendict[str, tuple[pm.Spec, ...]]:
        buckets: dict[str, list[pm.Spec]] = {}
        for fact in self.facts:
            buckets.setdefault(str(fact.anchor), []).append(fact)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def anchors(self) -> frozenset[str]:
        return frozenset((*self.rule_index.keys(), *self.fact_index.keys()))

    @flux.method
    def rules_for_anchor(self, anchor: str) -> tuple[urs.Rule, ...]:
        return self.rule_index.get(anchor, ())

    @flux.method
    def facts_by_anchor(self, anchor: str) -> tuple[pm.Spec, ...]:
        return self.fact_index.get(anchor, ())

    @flux.method
    def is_coinductive_anchor(self, anchor: str) -> bool:
        return anchor in self.coinductive_anchors

    @flux.method
    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        return self.host.schema_for(spec)

    @flux.method
    def eval_logic_op(
        self,
        operator: pm.Placeholder,
        *,
        goal: pm.Spec,
        session: urs.Session,
    ) -> urs.LogicOpStep | None:
        result = self.host.eval_logic_op(operator, goal=goal, session=session)
        if result is not None:
            return result

        args = goal.args.content
        if isinstance(operator, urs.KeyOfOperator) and len(args) == 2:
            target, result = args
            slot = urs.goal_slot_index_of(result)
            if slot is None:
                return urs.OpFailed("keyof result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = TypeFunctionBlocked(goal, "keyof")
                evidence = pm.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if not isinstance(target, pm.Spec):
                if isinstance(target, urs.SolverOperator):
                    blocker = OperatorPending(goal, target)
                    evidence = pm.Spec.of("std.logic.ByDeferred", goal, blocker)
                    return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
                return urs.OpFailed("keyof target must be a hosted spec")
            schema = self.schema_for(target)
            if schema is None:
                return urs.OpFailed("keyof target has no schema")
            keys = tuple(item.key for item in schema.items() if item.key is not None)
            return urs.OpBind(((slot, keys),), pm.Spec.of("std.logic.ByBuiltin", goal))

        if isinstance(operator, urs.ProjectionOperator) and len(args) in {3, 4}:
            if len(args) == 3:
                target, name, result = args
            else:
                target, _, name, result = args
            slot = urs.goal_slot_index_of(result)
            if slot is None or not isinstance(name, str):
                return urs.OpFailed("projection result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = ProjectionBlocked(goal, goal)
                evidence = pm.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if not isinstance(target, pm.Spec):
                if isinstance(target, urs.SolverOperator):
                    blocker = OperatorPending(goal, target)
                    evidence = pm.Spec.of("std.logic.ByDeferred", goal, blocker)
                    return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
                return urs.OpFailed("projection target must be a hosted spec")
            schema = self.schema_for(target)
            if schema is None:
                return urs.OpFailed("projection target has no schema")
            try:
                item = schema.item(pm.Id(name))
            except Exception:
                return urs.OpFailed(f"projection field {name!r} not found")
            return urs.OpBind(((slot, item.value),), pm.Spec.of("std.logic.ByBuiltin", goal))

        return None
