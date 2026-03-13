from __future__ import annotations

from typing import ClassVar, Optional
from itertools import product

from protobase import flux, _
import protomorph as pm

from axis import expr, syn, sem
from axis.log import report as log

from .base import SymDef, build_param_bindings, build_spec_bindings


class FnDef(SymDef):
    """
    Function definitions. Always emits ImplContribution.
    """

    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym(..args) -> $ret"),
        syn.Expr.from_str("$sym[..$spec](..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym(..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym[..$spec](..args) -> $ret"),
    )

    sym: expr.Sym = _
    spec: expr.Tuple | None = None
    args: expr.Tuple = _
    ret: syn.Expr = _
    ctx: syn.Expr | None = None

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        return frozenset(
            sem.Entity.ImplContribution(
                anchor=self.anchor,
                spec_bindings=build_spec_bindings(self.spec, where),
                param_bindings=build_param_bindings(self.args, takes),
                origin=self.origin,  # takes or where or returns,
                returns=merge_returns(self.ret, returns, self),
                ctx=self,  # build scope here!
            )
            for where, takes, returns in product(
                self.where or (None,),
                self.takes or (None,),
                self.returns or (None,),
            )
        )
    


def merge_returns(
    inline_expr: syn.Expr | None,
    block: FnDef.Returns | None,
    def_: FnDef,
) -> syn.Expr | None:
    if block is not None and block.expr is not None:
        if inline_expr is None:
            return block.expr
        else:
            (
                log.error("FnDef cannot have both inline and block returns")
                .label(inline_expr, "inline return")
                .label(block.expr, "block return")
                .emit()
            )
    elif inline_expr is not None:
        return inline_expr

    ( 
        log.error("FnDef requires a return expression")
        .label(def_.origin, "missing return")
        .emit()
    )
