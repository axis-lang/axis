from __future__ import annotations

from axis import dom, expr, syn


class Var(dom.Builtin, abstract=True):
    sym: expr.Sym
    bound: syn.Expr
    default: syn.Expr | None = None


class SpecVar(Var):
    pass


class ParamVar(Var):
    pass
