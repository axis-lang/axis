from __future__ import annotations

from typing import Callable

import pm
from .traversal import deep_zip


def _default_op(vals: frozenset[pm.Carrier]) -> pm.Carrier | None:
    if len(vals) == 1:
        return next(iter(vals))
    return None


def _capture(
    a: pm.Carrier,
    b: pm.Carrier,
    is_var: Callable[[pm.Carrier], bool],
) -> dict[pm.Carrier, frozenset[pm.Carrier]] | None:
    bindings: dict[pm.Carrier, set[pm.Carrier]] = {}
    for left, right in (walker := deep_zip(a, b)):
        l_var = is_var(left)
        r_var = is_var(right)
        if l_var and r_var:
            bindings.setdefault(left, set()).add(right)
            bindings.setdefault(right, set()).add(left)
            walker.skip()
        elif l_var:
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
            # Both non-leaf, non-var: deep_zip descends if arities match
            if len(left) != len(right):
                return None
    return {k: frozenset(v) for k, v in bindings.items()}


def unify(
    a: pm.Carrier,
    b: pm.Carrier,
    *,
    is_var: Callable[[pm.Carrier], bool],
    op: Callable[[frozenset[pm.Carrier]], pm.Carrier | None] = _default_op,
) -> pm.Carrier | None:
    """Unify two carrier trees.

    1. Capture: walk both trees in parallel, collect bindings for variables
    2. Resolve: apply `op` to resolve each variable's binding set
    3. Reify: substitute resolved bindings into `a`
    """
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
    return a.subst(resolved)
