from axis.core import syn

class Apply(syn.Expr):
    function: syn.Expr
    argument: syn.Expr

@syn.AstBuilder.build.register
def build_apply(
    self,
    ctx: syn.AxisParser.CallContext,
    function: syn.Expr,
    argument: syn.Expr,
):
    return Apply(function, argument, None)
