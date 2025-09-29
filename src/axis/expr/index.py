from axis import syn
from axis.src import Self

class Index(syn.Expr, frozen=True):
    origin: syn.Expr
    indices: syn.Expr # generalmente sera un Tuple (o shape)

    @classmethod
    def build(cls, origin: syn.Expr, indices: syn.Expr) -> Self:
        return cls(origin=origin, indices=indices)


# @syn.Builder.build.register
# def build_index_ast(
#     self,
#     ctx: syn.AxisParser.IndexContext,
#     origin: syn.Expr,
#     indice: syn.Expr,
# ):
#     return Index(origin=origin, indice=indice)