from __future__ import annotations

from collections.abc import Callable
from typing import cast

from protobase import Inmutable

import protomorph as pm

from axis import expr, log, sem, syn


type ConstraintResult = pm.Result[log.Report, Constraint]
type GoalResult = pm.Result[log.Report, pm.Spec]
type ConstraintTupleResult = pm.Result[log.Report]
type GoalTupleResult = pm.Result[log.Report]
type ScopeLookupResult = sem.ScopeLookupResult


class Constraint(Inmutable):
    subject: pm.Datum
    term: pm.Datum
    target: pm.Datum

    @property
    def goal(self) -> pm.Spec:
        return self.goal_for(self.subject)

    @property
    def template_goal(self) -> pm.Spec:
        return cast(pm.Spec, _goal_carrier(self.target).fetch())

    def goal_for(self, subject: pm.Datum | pm.Carrier) -> pm.Spec:
        return cast(pm.Spec, _goal_carrier(self.target).subst_it(subject).fetch())

    @property
    def target_type(self) -> pm.Type | None:
        return sem.bound_as_type(self.term)


def constraint_from_term(subject: pm.Datum, term: pm.Datum) -> Constraint:
    return Constraint(subject=subject, term=term, target=_constraint_target_term(term))


def constraint_for(
    subject: pm.Datum,
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
        pm.Result.ok(pm.wrap(constraint_from_term(subject, term_result.unwrap().fetch()))),
    )


def constraint_goal_for(
    subject: pm.Datum,
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
        pm.Result.ok(pm.wrap(cast(Constraint, constraint_result.unwrap().fetch()).goal)),
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
            return pm.Result.err(pm.wrap(report))

        subject_result = subject_for_binding(binding)
        if subject_result is None:
            continue
        if subject_result.is_err:
            return cast(ConstraintTupleResult, subject_result)

        constraint_result = constraint_for(subject_result.unwrap().fetch(), binding.bound_expr, scope)
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


def _tuple_result(*values: object) -> pm.Carrier:
    if not values:
        return pm.Tuple.Empty
    carriers = tuple(pm.wrap(value) for value in values)
    return pm.Tuple(pm.VaryingType.of(*(carrier.descriptor for carrier in carriers)), carriers)


def _goal_carrier(target: pm.Datum) -> pm.Carrier:
    return pm.wrap(pm.Spec.of(expr.CONFORMS_FACT, pm.IT, to=target))


def _constraint_target_term(term: pm.Datum) -> pm.Datum:
    type_ = sem.bound_as_type(term)
    return term if type_ is None else type_
