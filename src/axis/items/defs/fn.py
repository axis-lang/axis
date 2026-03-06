from __future__ import annotations

from typing import ClassVar, Optional
from itertools import product

from protobase import flux, _

from axis import dom, expr, syn
from axis.log import report as log
from axis.sem import Entity

from .base import SymDef, unify_args_takes, unify_spec_where


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
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset(
            Entity.ImplContribution(
                anchor=self.anchor,
                spec=unify_spec_where(self.spec, where),
                params=unify_args_takes(self.args, takes),
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
) -> syn.Expr:
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
    return syn.Expr.from_str("None")

    # @flux.property
    # def contributions(self) -> frozenset[Entity.Contribution]:
    #     if self.origin is None:
    #         return frozenset()

    #     anchor: dom.Anchor | None
    #     if self.ctx is not None:
    #         base = expr.to_anchor_ref(self.ctx, self.anchor)
    #         if base is None or self.sym is None:
    #             return frozenset()
    #         anchor = base.child(self.sym.name)
    #     else:
    #         base_expr = self.sym if self.sym is not None else self.origin
    #         anchor = expr.to_anchor_ref(base_expr, self.anchor)

    #     if anchor is None:
    #         return frozenset()

    #     contributions: list[Entity.Contribution] = []
    #     if self.anchor is not None:
    #         contributions.append(
    #             Entity.Member(
    #                 anchor=self.anchor,
    #                 name=expr.name_of(self.origin),
    #                 target=anchor,
    #                 origin=self.origin,
    #                 ctx=self,
    #             )
    #         )

    #     spec_struct = unify_spec_where(self.spec, self.where)

    #     returns: list[syn.Expr] = []
    #     if self.ret is not None:
    #         returns.append(self.ret)
    #     for ret in self.returns:
    #         if ret.expr is not None:
    #             returns.append(ret.expr)

    #     if not returns:
    #         report = log.error("FnDef requires a return expression").label(
    #             self.origin, "missing return"
    #         )
    #         report.emit()
    #         return frozenset()

    #     if self.takes:
    #         for takes in self.takes:
    #             params_struct = unify_args_takes(self.args, takes)
    #             for ret in returns:
    #                 contributions.append(
    #                     Entity.ImplContribution(
    #                         anchor=anchor,
    #                         spec=spec_struct,
    #                         params=params_struct,
    #                         returns=ret,
    #                         origin=ret,
    #                         ctx=self,
    #                     )
    #                 )
    #     else:
    #         params_struct = unify_args_takes(self.args, None)
    #         for ret in returns:
    #             contributions.append(
    #                 Entity.ImplContribution(
    #                     anchor=anchor,
    #                     spec=spec_struct,
    #                     params=params_struct,
    #                     returns=ret,
    #                     origin=ret,
    #                     ctx=self,
    #                 )
    #             )

    #     return frozenset(contributions)
