from __future__ import annotations

from types import NotImplementedType
from collections.abc import Callable
from typing import cast
from protobase import Inmutable, flux, _
from protobase.cached_property import slot_cached_property
import protomorph as pm
from protomorph import reasoning as urs

from axis import log, syn, sem

from .scope import Scope


class Context[P: "Context"](syn.SegregatedItem[P], abstract=True):

    class LogicVar(pm.SimpleVar):
        ctx: Context
        id: str

    class Contribution(pm.Builtin, abstract=True):
        anchor: pm.Anchor = _
        origin: syn.Node = _
        ctx: Context = _

        @flux.property
        def facts(self) -> frozenset[pm.Spec]:
            return frozenset()

        @flux.property
        def rules(self) -> frozenset[urs.Rule]:
            return frozenset()

        def _check(self) -> None:
            pass

        @flux.property
        def status(self) -> sem.Status:
            return _status_from_check(self._check)

    class EntityContribution(Contribution):
        pass

    class NamespaceContribution(EntityContribution):
        pass

    class ClaimContribution(EntityContribution):
        _facts: frozenset[pm.Spec] = frozenset()
        _rules: frozenset[urs.Rule] = frozenset()

        @flux.property
        def facts(self) -> frozenset[pm.Spec]:
            return self._facts

        @flux.property
        def rules(self) -> frozenset[urs.Rule]:
            return self._rules

        def _check(self) -> None:
            from axis import log, sem

            heads = tuple(self._facts) + tuple(rule.head for rule in self._rules)
            body_goals = tuple(
                cast(pm.Spec, goal.fetch()) if isinstance(goal, pm.Carrier) else cast(pm.Spec, goal)
                for rule in self._rules
                for goal in rule.body
            )
            if not heads and not body_goals:
                return

            realm = cast(sem.Realm, pm.current_realm())
            for head in heads:
                _check_goal_admission(
                    realm,
                    head,
                    origin=self.origin,
                    missing_message="Claim target must have fact facet",
                    mismatch_message="Claim head is not admitted by any declared fact spec",
                )
            for goal in body_goals:
                _check_goal_admission(
                    realm,
                    goal,
                    origin=self.origin,
                    missing_message="Claim body target must have fact facet",
                    mismatch_message="Claim body goal is not admitted by any declared fact spec",
                )

    @flux.property
    def contributions(self) -> frozenset[Context.Contribution]:
        return frozenset()

    @property
    def parent_scope(self) -> Scope | None:
        parent = self.parent
        while parent is not None:
            if parent.scope is not NotImplemented:
                return parent.scope
            parent = parent.parent
        return None

    @slot_cached_property
    def name(self) -> str | None:
        return None

    @flux.property
    def scope(self) -> Scope | NotImplementedType:
        builder = Scope.Builder(name=self.name, parent=self.parent_scope)
        self._build_scope(builder)
        return builder.build()

    def _build_scope(self, scope_builder: Scope.Builder): ...

    def _check(self) -> None:
        pass

    @flux.property
    def status(self) -> sem.Status:
        self.scope
        return _status_from_check(self._check)


def _check_goal_admission(
    realm: "sem.Realm",
    goal: pm.Spec,
    *,
    origin: syn.Node,
    missing_message: str,
    mismatch_message: str,
) -> None:
    from axis import log, sem

    entity = realm.entities_by_anchor.get(goal.anchor)
    if entity is None:
        log.error(missing_message).label(origin).throw()

    pattern = entity.spec_pattern_for(sem.Entity.FactFacet)
    if pattern is None:
        log.error(missing_message).label(origin).throw()

    args = goal.args
    if args is None or pattern.match(args) is None:
        log.error(mismatch_message).label(origin).throw()


def _status_from_check(check: Callable[[], None]) -> sem.Status:
    try:
        check()
    except log.Report.Exception as raised:
        return sem.Status(reports=(raised.report,))
    return sem.Status()
