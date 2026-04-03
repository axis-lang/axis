from __future__ import annotations

import protomorph

from axis import syn


def as_anchor(ast: syn.Expr, scope_ref: protomorph.Anchor | None) -> protomorph.Anchor:
    return ast.to_anchor(scope_ref)
