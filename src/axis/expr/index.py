from axis import syn

class Index(syn.Expr):
    base: syn.Expr
    indice: syn.Expr

@syn.AstBuilder.build.register
def build_index_ast(
    self,
    ctx: syn.AxisParser.IndexContext,
    base: syn.Expr,
    indice: syn.Expr,
):
    return Index(base, indice)