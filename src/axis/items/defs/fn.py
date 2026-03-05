from __future__ import annotations

from typing import ClassVar, Optional

from protobase import flux

from axis import dom, expr, syn
from axis.log import report as log
from axis.sem import Entity

from .base import Def, unify_args_takes, unify_spec_where


class FnDef(Def):
    """
    Function definitions. Always emits ImplContribution.
    """

    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym(..args) -> $ret"),
        syn.Expr.from_str("$sym[..$spec](..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym(..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym[..$spec](..args) -> $ret"),
    )

    sym: expr.Sym | None = None
    ret: syn.Expr | None = None
    args: expr.Tuple | None = None
    spec: Optional[expr.Tuple] = None
    ctx: Optional[syn.Expr] = None

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        if self.origin is None:
            return frozenset()

        anchor: dom.Anchor | None
        if self.ctx is not None:
            base = expr.to_anchor_ref(self.ctx, self.anchor)
            if base is None or self.sym is None:
                return frozenset()
            anchor = base.child(self.sym.name)
        else:
            base_expr = self.sym if self.sym is not None else self.origin
            anchor = expr.to_anchor_ref(base_expr, self.anchor)

        if anchor is None:
            return frozenset()

        contributions: list[Entity.Contribution] = []
        if self.anchor is not None:
            contributions.append(
                Entity.Member(
                    anchor=self.anchor,
                    name=expr.to_name(self.origin),
                    target=anchor,
                    origin=self.origin,
                    ctx=self,
                )
            )

        spec_struct = unify_spec_where(self.spec, self.where)

        returns: list[syn.Expr] = []
        if self.ret is not None:
            returns.append(self.ret)
        for ret in self.returns:
            if ret.expr is not None:
                returns.append(ret.expr)

        if not returns:
            report = log.error("FnDef requires a return expression").label(
                self.origin, "missing return"
            )
            report.emit()
            return frozenset()

        if self.takes:
            for takes in self.takes:
                params_struct = unify_args_takes(self.args, takes)
                for ret in returns:
                    contributions.append(
                        Entity.ImplContribution(
                            anchor=anchor,
                            spec=spec_struct,
                            params=params_struct,
                            returns=ret,
                            origin=ret,
                            ctx=self,
                        )
                    )
        else:
            params_struct = unify_args_takes(self.args, None)
            for ret in returns:
                contributions.append(
                    Entity.ImplContribution(
                        anchor=anchor,
                        spec=spec_struct,
                        params=params_struct,
                        returns=ret,
                        origin=ret,
                        ctx=self,
                    )
                )

        return frozenset(contributions)
