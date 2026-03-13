from __future__ import annotations

import protomorph as pm

from axis import syn
from axis.log import report as log

from ..member import Member
from ..sym import Sym


def as_anchor(ast: syn.Expr, scope_ref: pm.Anchor | None) -> pm.Anchor:
    """Resolve an anchor path from a simple name/member expression."""
    match ast:
        case Sym(name=name, at=at):
            if at is not None:
                log.warn("Anchor cannot @-qualify a symbol").label(ast).emit()
            return pm.Anchor.from_root(name) if scope_ref is None else scope_ref.child(name)
        case Member(of=of, name=name):
            return as_anchor(of, scope_ref).child(name)
        case _:
            log.error(f"Unsupported anchor expression type ({type(ast)})").label(
                ast
            ).throw()
