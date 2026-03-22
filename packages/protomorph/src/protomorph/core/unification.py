from __future__ import annotations

from typing import Callable

from protobase import frozendict

from .foundation import Val
from .traversal import deep_zip


def _default_op(vals: frozenset[Val]) -> Val | None:
    if len(vals) == 1:
        return next(iter(vals))
    return None


def _capture(
    a: Val,
    b: Val,
    is_var: Callable[[Val], bool],
) -> dict[Val, frozenset[Val]] | None:
    bindings: dict[Val, set[Val]] = {}
    for left, right in (walker := deep_zip(a, b)):
        l_var = is_var(left)
        r_var = is_var(right)
        if l_var:
            bindings.setdefault(left, set()).add(right)
            walker.skip()
        elif r_var:
            bindings.setdefault(right, set()).add(left)
            walker.skip()
        elif left.is_leaf and right.is_leaf:
            if left != right:
                return None
        elif left.is_leaf != right.is_leaf:
            return None
        else:
            if not left.compatible(right):
                return None
            # both non-leaf, non-var: deep_zip descends if arities match
            if len(left.children()) != len(right.children()):
                return None
    return {k: frozenset(v) for k, v in bindings.items()}


def unify(
    a: Val,
    b: Val,
    *,
    is_var: Callable[[Val], bool],
    op: Callable[[frozenset[Val]], Val | None] = _default_op,
) -> Val | None:
    # Stage 1: capture
    raw = _capture(a, b, is_var)
    if raw is None:
        return None

    # Stage 2: resolve
    resolved = {}
    for var, vals in raw.items():
        result = op(vals)
        if result is None:
            return None
        resolved[var] = result

    # Stage 3: reify
    return a.subst(frozendict(resolved))
