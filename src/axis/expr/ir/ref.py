from __future__ import annotations

import protomorph as pm

from axis import syn


def as_anchor(ast: syn.Expr, scope_ref: pm.Anchor | None) -> pm.Anchor:
    return ast.to_anchor(scope_ref)
