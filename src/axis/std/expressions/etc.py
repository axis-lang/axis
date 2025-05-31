from typing import Optional
from axis.core import syn

class Etc(syn.Expr):
    #from_: Optional[syn.Expr] = None
    #to: Optional[syn.Expr] = None
    expr: Optional[syn.Expr]


@syn.AstBuilder.build.register
def build_spread(
    self,
    ctx: syn.AxisParser.EtcContext,
    ellipsis,
    expr: Optional[syn.Expr] = None,
):
    assert ellipsis == '...'
    return Etc(expr=expr)


# @syn.UnifierExprTransformer.transform.register(Spread)
# def visit_sym(self: syn.UnifierExprTransformer, sperad: Spread):

#     if sym.is_wildcard:
#         return sym

#     return self.add_var(sym.name, sym)