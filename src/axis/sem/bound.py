from __future__ import annotations

from typing import Any

import protomorph as pm

from axis import log, sem, syn
import axis.expr.lowering as expr_bounds


def build_term(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Result[log.Report, Any] | None:
    return expr_bounds.build_term(bound_expr, scope)


def build_bound(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Result[log.Report, Any] | None:
    return expr_bounds.build_bound(bound_expr, scope)


def build_default(default_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Result[log.Report, Any] | None:
    return expr_bounds.build_default(default_expr, scope)


def build_extends_fact(
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> pm.Result[log.Report, pm.Spec] | None:
    return expr_bounds.build_extends_fact(bound_expr, scope)


def build_binding_pattern(
    bindings: sem.BindingStruct,
    scope: syn.ScopeLike,
) -> pm.Result[log.Report, Any]:
    return expr_bounds.build_binding_pattern(bindings, scope)


def bound_as_type(
    bound: object | None,
    *,
    bridge: object | None = None,
) -> pm.Type | None:
    return expr_bounds.bound_as_type(bound, bridge=bridge)
