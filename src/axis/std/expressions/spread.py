from axis.core import syn

class Spread(syn.Expr):
    expr: syn.Expr


@syn.AstBuilder.build.register
def build_spread(
    self,
    ctx: syn.AxisParser.SpreadContext,
    _ellipsis,
    expr: syn.Expr,
):
    return Spread(expr)