from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from protobase import Inmutable

import protomorph as pm

from axis import expr, log, sem, syn


class Constraint(Inmutable):
    subject: pm.Val
    term: pm.Val
    target: pm.Val

    @property
    def goal(self) -> pm.Spec:
        return pm.spec_ref(
            expr.CONFORMS_FACT,
            pm.struct(self.subject, to=self.target),
        )

    @property
    def target_type(self) -> pm.Type | None:
        return sem.bound_as_type(self.term)

    def satisfies(self, value: pm.Val, *, bridge: pm.SemanticBridge | None = None) -> bool:
        bridge = pm.BRIDGE.get(pm.DEFAULT_BRIDGE) if bridge is None else bridge
        candidate: pm.Val | pm.Type = value
        target_type = self.target_type
        if target_type is not None:
            candidate_type = sem.bound_as_type(value, bridge=bridge)
            if candidate_type is None:
                return False
            candidate = candidate_type
        return bool(cast(Any, pm).satisfies(candidate, self.target, bridge=bridge))


def constraint_from_term(subject: pm.Val, term: pm.Val) -> Constraint:
    return Constraint(subject=subject, term=term, target=_constraint_target_term(term))


def constraint_for(
    subject: pm.Val,
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> Constraint | pm.Err | None:
    if bound_expr is None:
        return None

    term = expr.build_bound(bound_expr, scope)
    if term is None or isinstance(term, pm.Err):
        return pm.Err() if term is None else term

    return constraint_from_term(subject, term)


def constraint_goal_for(
    subject: pm.Val,
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> pm.Spec | pm.Err | None:
    constraint = constraint_for(subject, bound_expr, scope)
    if constraint is None or isinstance(constraint, pm.Err):
        return constraint
    return constraint.goal


def binding_constraints(
    bindings: sem.BindingStruct,
    scope: sem.Scope,
    *,
    subject_for_binding: Callable[[sem.BindingStruct.Field], pm.Val | None],
    origin_label: str = "constraint",
    allow_defaults: bool = False,
) -> tuple[Constraint, ...] | pm.Err:
    constraints: list[Constraint] = []
    for binding in bindings:
        if binding.default_expr is not None and not allow_defaults:
            return log.error(f"Claim {origin_label} bindings do not support defaults yet").label(
                binding.origin
            ).tag(pm.Err())

        subject = subject_for_binding(binding)
        if subject is None:
            continue

        constraint = constraint_for(subject, binding.bound_expr, scope)
        if constraint is None:
            continue
        if isinstance(constraint, pm.Err):
            return constraint
        constraints.append(constraint)
    return tuple(constraints)


def binding_constraint_goals(
    bindings: sem.BindingStruct,
    scope: sem.Scope,
    *,
    subject_for_binding: Callable[[sem.BindingStruct.Field], pm.Val | None],
    origin_label: str = "constraint",
    allow_defaults: bool = False,
) -> tuple[pm.Spec, ...] | pm.Err:
    constraints = binding_constraints(
        bindings,
        scope,
        subject_for_binding=subject_for_binding,
        origin_label=origin_label,
        allow_defaults=allow_defaults,
    )
    if isinstance(constraints, pm.Err):
        return constraints
    return tuple(constraint.goal for constraint in constraints)


def _constraint_target_term(term: pm.Val) -> pm.Val:
    type_ = term.as_type()
    if type_ is None:
        return term
    if isinstance(type_, pm.Val):
        return type_
    return pm.val(type_)
