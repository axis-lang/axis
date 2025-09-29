from axis import syn

class Index(syn.Expr):
    origin: syn.Expr
    indice: syn.Expr

@syn.Builder.build.register
def build_index_ast(
    self,
    ctx: syn.AxisParser.IndexContext,
    origin: syn.Expr,
    indice: syn.Expr,
):
    return Index(origin=origin, indice=indice)