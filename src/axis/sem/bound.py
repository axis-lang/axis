from __future__ import annotations

import protomorph as pm

from axis import log, syn


def build_bound(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    if bound_expr is None:
        return None

    try:
        return bound_expr.to_bound(scope)
    except syn.BoundLoweringError as exc:
        return (
            log.error("Unsupported bound expression")
            .label(bound_expr, str(exc))
            .tag(pm.Err())
        )


def build_default(default_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return build_bound(default_expr, scope)
