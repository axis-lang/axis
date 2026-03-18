from __future__ import annotations

import protomorph as pm

from axis import syn
from axis.expr import bound_support as expr_bounds
from axis.sem.binding import Binding, BindingStruct


def build_term(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return expr_bounds.build_term(bound_expr, scope)


def build_bound(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return expr_bounds.build_bound(bound_expr, scope)


def build_default(default_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return expr_bounds.build_default(default_expr, scope)


def build_extends_fact(
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> pm.Spec | pm.Err | None:
    return expr_bounds.build_extends_fact(bound_expr, scope)


def build_binding_pattern(
    bindings: BindingStruct[Binding],
    scope: syn.ScopeLike,
) -> pm.Val:
    return expr_bounds.build_binding_pattern(bindings, scope)


def bound_as_type(
    bound: pm.Val | None,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Type | None:
    return expr_bounds.bound_as_type(bound, bridge=bridge)
