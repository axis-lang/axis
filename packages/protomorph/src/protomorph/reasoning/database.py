from __future__ import annotations

from protobase import Consed, flux, frozendict

import protomorph
from protomorph import reasoning as urs
from protomorph.foundation import Anchor

from .model import DeferredGoal, Judgment, OperatorPending, ProjectionBlocked, TypeFunctionBlocked, default_wake_on


class Database(protomorph.Realm, Consed, abstract=True):
    pass


class RuleSetDatabase(Database):
    rules: tuple[urs.Rule, ...] = ()
    facts: tuple[protomorph.Spec, ...] = ()
    coinductive_anchors: frozenset[Anchor] = frozenset()
    host: protomorph.Realm = protomorph.NATIVE_REALM

    @flux.property
    def rule_index(self) -> frozendict[Anchor, tuple[urs.Rule, ...]]:
        buckets: dict[Anchor, list[urs.Rule]] = {}
        for rule in self.rules:
            buckets.setdefault(rule.head.anchor, []).append(rule)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @flux.property
    def fact_index(self) -> frozendict[Anchor, tuple[protomorph.Spec, ...]]:
        buckets: dict[Anchor, list[protomorph.Spec]] = {}
        for fact in self.facts:
            buckets.setdefault(fact.anchor, []).append(fact)
        return frozendict((anchor, tuple(items)) for anchor, items in buckets.items())

    @property
    def anchors(self) -> frozenset[Anchor]:
        return frozenset((*self.rule_index.keys(), *self.fact_index.keys()))

    def rules_for_anchor(self, anchor: Anchor) -> tuple[urs.Rule, ...]:
        return self.rule_index.get(anchor, ())

    def facts_by_anchor(self, anchor: Anchor) -> tuple[protomorph.Spec, ...]:
        return self.fact_index.get(anchor, ())

    def is_coinductive_anchor(self, anchor: Anchor) -> bool:
        return anchor in self.coinductive_anchors

    def schema_for(self, spec: protomorph.Spec) -> protomorph.TupleLikeType | None:
        return self.host.schema_for(spec)

    def val_is_leaf(self, meta: protomorph.Type, data: object) -> bool:
        return self.host.val_is_leaf(meta, data)

    def val_children(
        self,
        meta: protomorph.Type,
        data: object,
    ) -> tuple[protomorph.Carrier, ...]:
        return self.host.val_children(meta, data)

    def val_reconstruct(
        self,
        meta: protomorph.Type,
        children: tuple[protomorph.Carrier, ...],
    ) -> object:
        return self.host.val_reconstruct(meta, children)

    def eval_logic_op(
        self,
        operator: protomorph.Placeholder,
        *,
        goal: protomorph.Spec,
        session: urs.Session,
    ) -> urs.LogicOpStep | None:
        result = self.host.eval_logic_op(operator, goal=goal, session=session)
        if result is not None:
            return result

        args = goal.args.content
        if isinstance(operator, urs.KeyOfOperator) and len(args) == 2:
            target = operator.target
            result = args[-1]
            slot = urs.goal_slot_index_of(result)
            if slot is None:
                return urs.OpFailed("keyof result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = TypeFunctionBlocked(goal, "keyof")
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), urs.SolverOperator):
                blocker = OperatorPending(goal, cast(protomorph.Builtin, target.fetch()))
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), protomorph.Placeholder):
                blocker = TypeFunctionBlocked(goal, "keyof")
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            target_value = target.fetch()
            if not isinstance(target_value, protomorph.Type):
                return urs.OpFailed("keyof target must be a type")
            schema = target_value.schema
            if schema is None:
                return urs.OpFailed("keyof target has no keys")
            keys = tuple(str(item.key) for item in schema.items() if item.key is not None)
            return urs.OpBind(((slot, keys),), protomorph.Spec.of("std.logic.ByBuiltin", goal))

        if isinstance(operator, urs.ProjectionOperator) and len(args) in {3, 4}:
            target = operator.target
            name = operator.name
            result = args[-1]
            slot = urs.goal_slot_index_of(result)
            if slot is None or not isinstance(name, str):
                return urs.OpFailed("projection result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = ProjectionBlocked(goal, goal)
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), urs.SolverOperator):
                blocker = OperatorPending(goal, cast(protomorph.Builtin, target.fetch()))
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), protomorph.Placeholder):
                blocker = ProjectionBlocked(goal, goal)
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            target_value = target.fetch()
            if not isinstance(target_value, protomorph.Type):
                return urs.OpFailed("projection target must be a type")
            schema = target_value.schema
            if schema is None:
                return urs.OpFailed(f"projection field {name!r} not found")
            try:
                item = schema.item(protomorph.Id(name))
            except (IndexError, KeyError):
                return urs.OpFailed(f"projection field {name!r} not found")
            return urs.OpBind(((slot, item.value),), protomorph.Spec.of("std.logic.ByBuiltin", goal))

        if isinstance(operator, urs.AttrOperator) and len(args) == 3:
            target = operator.of_value
            key = operator.key
            result = args[-1]
            slot = urs.goal_slot_index_of(result)
            if slot is None:
                return urs.OpFailed("attr result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = ProjectionBlocked(goal, goal)
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), urs.SolverOperator):
                blocker = OperatorPending(goal, cast(protomorph.Builtin, target.fetch()))
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), protomorph.Placeholder):
                blocker = ProjectionBlocked(goal, goal)
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            target_value = target.fetch()
            if isinstance(target_value, protomorph.Spec):
                args_carrier = target_value.args
                if args_carrier is None:
                    return urs.OpFailed("attr target has no arguments")
                if isinstance(key, protomorph.Id):
                    try:
                        return urs.OpBind(((slot, args_carrier.attr(key).fetch()),), protomorph.Spec.of("std.logic.ByBuiltin", goal))
                    except KeyError:
                        return urs.OpFailed(f"attr field {key!r} not found")
                if isinstance(key, int):
                    try:
                        return urs.OpBind(((slot, args_carrier[key].fetch()),), protomorph.Spec.of("std.logic.ByBuiltin", goal))
                    except IndexError:
                        return urs.OpFailed(f"attr offset {key!r} out of bounds")
                return urs.OpFailed("attr key must be str or int")
            if isinstance(target_value, protomorph.Tuple):
                if isinstance(key, protomorph.Id):
                    try:
                        return urs.OpBind(((slot, target_value.attr(key).fetch()),), protomorph.Spec.of("std.logic.ByBuiltin", goal))
                    except KeyError:
                        return urs.OpFailed(f"attr field {key!r} not found")
                if isinstance(key, int):
                    try:
                        return urs.OpBind(((slot, target_value[key].fetch()),), protomorph.Spec.of("std.logic.ByBuiltin", goal))
                    except IndexError:
                        return urs.OpFailed(f"attr offset {key!r} out of bounds")
                return urs.OpFailed("attr key must be Id or int")
            return urs.OpFailed("attr target must be Spec or Tuple")

        if isinstance(operator, urs.TypeOfOperator) and len(args) == 2:
            target = operator.of_value
            result = args[-1]
            slot = urs.goal_slot_index_of(result)
            if slot is None:
                return urs.OpFailed("typeof result must be a query slot")
            if urs.contains_goal_slots(target):
                blocker = TypeFunctionBlocked(goal, "typeof")
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), urs.SolverOperator):
                blocker = OperatorPending(goal, cast(protomorph.Builtin, target.fetch()))
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            if isinstance(target.fetch(), protomorph.Placeholder):
                blocker = TypeFunctionBlocked(goal, "typeof")
                evidence = protomorph.Spec.of("std.logic.ByDeferred", goal, blocker)
                return urs.OpDeferred(DeferredGoal(goal, blocker, evidence, default_wake_on(blocker), Judgment(goal, evidence)))
            return urs.OpBind(((slot, target.type.fetch()),), protomorph.Spec.of("std.logic.ByBuiltin", goal))

        return None

    def with_rules(self, *rules: urs.Rule) -> RuleSetDatabase:
        return RuleSetDatabase(
            rules=(*self.rules, *rules),
            facts=self.facts,
            coinductive_anchors=self.coinductive_anchors,
            host=self.host,
        )

    def with_facts(self, *facts: protomorph.Spec) -> RuleSetDatabase:
        return RuleSetDatabase(
            rules=self.rules,
            facts=(*self.facts, *facts),
            coinductive_anchors=self.coinductive_anchors,
            host=self.host,
        )

    def with_impls(self, *_impls: object) -> RuleSetDatabase:
        return self
