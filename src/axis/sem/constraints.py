from __future__ import annotations

from collections.abc import Callable
from typing import cast

import protomorph as pm
from protomorph import reasoning as urs

from axis import expr, log, sem, syn


Constraint = pm.Constraint
type ConstraintResult = pm.Result[log.Report, Constraint]
type GoalResult = pm.Result[log.Report, pm.Spec]
type ConstraintTupleResult = pm.Result[log.Report]
type GoalTupleResult = pm.Result[log.Report]
type ScopeLookupResult = sem.ScopeLookupResult


def constraint_from_term(subject: pm.Val | pm.Datum, term: pm.Val | pm.Datum) -> Constraint:
    subject_carrier = _carrier_of(subject)
    term_carrier = _carrier_of(term)
    target = _constraint_target_term(term_carrier)
    return Constraint(
        subject=_constraint_subject_term(subject_carrier, target),
        term=term_carrier,
        target=target,
    )


def constraint_for(
    subject: pm.Val | pm.Datum,
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> ConstraintResult | None:
    if bound_expr is None:
        return None

    term_result = sem.build_bound(bound_expr, scope)
    if term_result is None:
        return None
    if term_result.is_err:
        return cast(ConstraintResult, term_result)
    return cast(
        ConstraintResult,
        pm.Result.ok(pm.val(constraint_from_term(subject, term_result.unwrap()))),
    )


def constraint_goal_for(
    subject: pm.Val | pm.Datum,
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> GoalResult | None:
    constraint_result = constraint_for(subject, bound_expr, scope)
    if constraint_result is None:
        return None
    if constraint_result.is_err:
        return cast(GoalResult, constraint_result)
    return cast(
        GoalResult,
        pm.Result.ok(pm.val(cast(Constraint, constraint_result.unwrap().fetch()).goal)),
    )


def binding_constraints(
    bindings: sem.BindingStruct,
    scope: sem.Scope,
    *,
    subject_for_binding: Callable[[sem.BindingStruct.Field], ScopeLookupResult | None],
    origin_label: str = "constraint",
    allow_defaults: bool = False,
) -> ConstraintTupleResult:
    constraints: list[Constraint] = []
    for binding in bindings:
        if binding.default_expr is not None and not allow_defaults:
            report = log.error(
                f"Claim {origin_label} bindings do not support defaults yet"
            ).label(binding.origin).build()
            return pm.Result.err(pm.val(report))

        subject_result = subject_for_binding(binding)
        if subject_result is None:
            continue
        if subject_result.is_err:
            return cast(ConstraintTupleResult, subject_result)

        constraint_result = constraint_for(subject_result.unwrap(), binding.bound_expr, scope)
        if constraint_result is None:
            continue
        if constraint_result.is_err:
            return cast(ConstraintTupleResult, constraint_result)
        constraints.append(cast(Constraint, constraint_result.unwrap().fetch()))
    return pm.Result.ok(_tuple_result(*constraints))


def binding_constraint_goals(
    bindings: sem.BindingStruct,
    scope: sem.Scope,
    *,
    subject_for_binding: Callable[[sem.BindingStruct.Field], ScopeLookupResult | None],
    origin_label: str = "constraint",
    allow_defaults: bool = False,
) -> GoalTupleResult:
    constraints_result = binding_constraints(
        bindings,
        scope,
        subject_for_binding=subject_for_binding,
        origin_label=origin_label,
        allow_defaults=allow_defaults,
    )
    if constraints_result.is_err:
        return cast(GoalTupleResult, constraints_result)
    constraints = cast(tuple[Constraint, ...], constraints_result.unwrap().fetch())
    return pm.Result.ok(_tuple_result(*(constraint.goal for constraint in constraints)))


def _tuple_result(*values: object) -> pm.Val:
    if not values:
        return pm.Tuple.Empty
    carriers = tuple(pm.val(value) for value in values)
    return pm.Tuple(
        pm.Varying.of(*(carrier.descriptor for carrier in carriers)),
        tuple(carrier.fetch() for carrier in carriers),
    )


def _carrier_of(value: pm.Val | pm.Datum) -> pm.Val:
    return value if isinstance(value, pm.Val) else pm.val(value)


def _constraint_target_term(term: pm.Val) -> pm.Val:
    type_ = sem.bound_as_type(term)
    return term if type_ is None else pm.val(type_)


def _constraint_subject_term(subject: pm.Val, target: pm.Val) -> pm.Val:
    if isinstance(target.fetch(), pm.Type):
        return pm.val(urs.TypeOfOperator.of(subject))
    return subject
