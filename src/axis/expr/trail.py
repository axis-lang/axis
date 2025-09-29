from axis import syn

class Trail(syn.Expr):
    'Represents a trailing lambda expression'
    base: syn.Expr
    suite: syn.Expr

@syn.Builder.build.register
def build_trail_ast(
    self,
    ctx: syn.AxisParser.TrailingLambdaContext,
    base: syn.Expr,
    trailing: syn.Expr = None,
):
    return Trail(base, trailing)
