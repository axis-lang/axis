from typing import ClassVar, Optional
from axis.core import syn, sem


class Def(syn.Item):
    """
    Represents a 'def' entity:

    def Vector(..)
    takes:
        val x: N
        val y: N
    where:
        val N: Number
    """

    keyword: ClassVar[str] = "def"
    grammar: ClassVar[str] = "def: 'def' expression EOF;"

    expr: syn.Expr

    class Where(syn.Block):
        """
        where:
            val N: Number
        """

        keyword: ClassVar[str] = "where"
        keyword_sep: ClassVar[str] = ": \t"
        grammar: ClassVar[str] = "where: 'where' ':' EOF;"

    class Takes(syn.Block):
        """
        takes [overload_name]:
            val x: N
            val y: N
        """

        keyword: ClassVar[str] = "takes"
        keyword_sep: ClassVar[str] = ": \t"
        grammar: ClassVar[str] = "takes: 'takes' ID? ':' EOF;"

        id: Optional[str]

    class Returns(syn.Block):
        """ """

        keyword: ClassVar[str] = "returns"
        grammar: ClassVar[str] = "returns: 'returns' expression EOF;"

        expr: syn.Expr


@syn.AstBuilder.build.register
def build_def_ast(self, _: syn.AxisParser.DefItemContext, expr: syn.Expr):
    return dict(expr=expr)

@syn.AstBuilder.build.register
def build_def_where_ast(self, _: syn.AxisParser.WhereBlockContext):
    return dict()

@syn.AstBuilder.build.register
def build_def_takes_ast(self, _: syn.AxisParser.TakesBlockContext, id: Optional[str]=None):
    return dict(id=id)

@syn.AstBuilder.build.register
def build_def_returns_ast(self, _: syn.AxisParser.ReturnsBlockContext, expr: syn.Expr):
    return dict(expr=expr)


@sem.ScopingPass.process_item.register
def def_scoping(self: sem.ScopingPass, def_ast: Def):
    # evaluar el path

    # extrae el nombre desde def_ast.expr

    # extrae hiperparametros desde def_ast.children Where
    # extrae parametros desde def_ast.chidlren Takes

    # como exportar los Parametros

    # mod_path_expr = sem.transform_sym_to_member(mod_ast.path, member_of=self.path_prefix)

    # child_scoping = self.child_scoping(path_prefix=mod_path_expr, ast=mod_ast)
    # for item in mod_ast.iter(syn.Item):
    #     grandchild_scoping = child_scoping.process_item(item)
    #     # we have 3 levels of scoping access here, this is useful?

    # return child_scoping
    pass
