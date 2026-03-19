from __future__ import annotations

from collections.abc import Callable

import protomorph as pm

from axis import expr, log, sem, syn


def constraint_goal_for(
    subject: pm.Val,
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> pm.Spec | pm.Err | None:
    if bound_expr is None:
        return None

    term = expr.build_term(bound_expr, scope)
    if term is None or isinstance(term, pm.Err):
        return pm.Err() if term is None else term

    return pm.spec_ref(
        expr.CONFORMS_FACT,
        pm.struct(subject, to=_constraint_target_term(term)),
    )


def binding_constraint_goals(
    bindings: sem.BindingStruct,
    scope: sem.Scope,
    *,
    subject_for_binding: Callable[[sem.BindingStruct.Field], pm.Val | None],
    origin_label: str = "constraint",
) -> tuple[pm.Spec, ...] | pm.Err:
    goals: list[pm.Spec] = []
    for binding in bindings:
        if binding.default_expr is not None:
            return log.error(f"Claim {origin_label} bindings do not support defaults yet").label(
                binding.origin
            ).tag(pm.Err())

        subject = subject_for_binding(binding)
        if subject is None:
            continue

        goal = constraint_goal_for(subject, binding.bound_expr, scope)
        if goal is None:
            continue
        if isinstance(goal, pm.Err):
            return goal
        goals.append(goal)
    return tuple(goals)


def _constraint_target_term(term: pm.Val) -> pm.Val:
    type_ = term.as_type()
    if type_ is None:
        return term
    if isinstance(type_, pm.Val):
        return type_
    return pm.val(type_)
