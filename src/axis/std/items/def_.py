from typing import ClassVar, Optional
from axis.core import syn, sem
from .val import Val
from axis.std.expressions import Apply


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


Def.child_block_type(Def.Where, must_be_indented=False)
Def.child_block_type(Def.Takes, must_be_indented=False)
Def.child_block_type(Def.Returns, must_be_indented=False)

Def.Where.child_block_type(Val, must_be_indented=True)
Def.Takes.child_block_type(Val, must_be_indented=True)


@syn.AstBuilder.build.register(syn.AxisParser.DefItemContext)
def build_def_ast(
    self,
    _,
    expr: syn.Expr,
    /,
    children: tuple[syn.Block],
):
    # todo, procesar los childrens para obtener parametros, hiperparametros y return
    return Def(expr=expr, children=children)


@syn.AstBuilder.build.register(syn.AxisParser.WhereBlockContext)
def build_def_where_ast(
    self, _, _colon, *, children: tuple[syn.Block]
):
    return Def.Where(children=children)


@syn.AstBuilder.build.register(syn.AxisParser.TakesBlockContext)
def build_def_takes_ast(
    self,
    _,
    *args,
    children: tuple[syn.Block],
):
    id = args[0] if len(args) > 0 else None
    return Def.Takes(id=id, children=children)


@syn.AstBuilder.build.register(syn.AxisParser.ReturnsBlockContext)
def build_def_returns_ast(
    self,
    _,
    expr: syn.Expr,
    *,
    children: tuple[syn.Block],
):
    return Def.Returns(
        expr=expr,
        children=children,
    )




@sem.ScopingPass.process_item.register(Def)
def def_scoping(self: sem.ScopingPass, def_ast: Def):


    def_ast.expr

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


