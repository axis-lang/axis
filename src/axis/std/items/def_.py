from protobase import Object, Record, cached_property
from typing import ClassVar, Literal, Optional
from axis.core import syn, sem, log
from .val import Val
from axis.std.expr import Apply, Sym, Tuple


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

    class Kind(syn.MatchClass, abstract=True, frozen=True):
        name: Sym

    class ClassKind(Kind):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.parse("$name@Sym"),
            syn.Expr.parse("$name[..$generics]"),
        )

        generics: Optional[Tuple] = None

    class FunctionKind(Kind):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.parse("$name@Sym(..$arguments)"),
            syn.Expr.parse("$context.$name(..$arguments)"),
        )

        arguments: Optional[Tuple] = None
        context: Optional[syn.Expr] = None

    class Where(syn.Block):
        """
        where:
            val N: Number
        """

        keyword: ClassVar[str] = "where"
        keyword_sep: ClassVar[str] = ": \t"
        grammar: ClassVar[str] = "where: 'where' ':' EOF;"

        @classmethod
        def build(cls, kw: Literal["where"], colon: Literal[':'], *, children: syn.Block.Children):
            return cls(children=children)

    class Takes(syn.Block):
        """
        takes [overload_name]:
            val x: N
            val y: N
        """

        keyword: ClassVar[str] = "takes"
        keyword_sep: ClassVar[str] = ": \t"
        grammar: ClassVar[str] = "takes: 'takes' ID? ':' EOF;"

        name: Optional[str]

        @classmethod
        def build(
            cls,
            kw: Literal["takes"],
            name: Optional[str] = None,
            *,
            children: syn.Block.Children,
        ):
            return cls(name=name, children=children)

    class Returns(syn.Block):
        """ """

        keyword: ClassVar[str] = "returns"
        grammar: ClassVar[str] = "returns: 'returns' expression EOF;"

        expr: syn.Expr

        @classmethod
        def build(cls, kw:Literal['returns'], expr: syn.Expr, *, children: syn.Block.Children):
            return cls(expr=expr, children=children)

    keyword: ClassVar[str] = "def"
    grammar: ClassVar[str] = "def: 'def' expression EOF;"

    expr: syn.Expr

    @classmethod
    def build(
        cls, kw: Literal["def"], expr: syn.Expr, *, children: tuple[syn.Block, ...]
    ):
        return cls(expr=expr, children=children)

    @cached_property
    def kind(self):
        kind = self.Kind.match(self.expr)
        if kind is None:
            log.error(
                f"Definition expression does not match any known kind: {self.expr}"
            ).with_label(self.as_label).emit()
        return kind

    def bind(cls, parent: sem.Binding) -> sem.Binding:
         return sem.Binding(
            parent=parent,
            ref=parent.ref.member(cls.kind.name.name),
            item=cls,
         )
    

Def.add_child_block(Def.Where, must_be_indented=False)
Def.add_child_block(Def.Takes, must_be_indented=False)
Def.add_child_block(Def.Returns, must_be_indented=False)
Def.Where.add_child_block(Val, must_be_indented=True)
Def.Takes.add_child_block(Val, must_be_indented=True)


# @syn.AstBuilder.build.register(syn.AxisParser.DefItemContext)
# def build_def(
#     self,
#     _,
#     expr: syn.Expr,
#     *,
#     children: tuple[syn.Block],
# ):
#     # todo, procesar los childrens para obtener parametros, hiperparametros y return
#     return Def(expr=expr, children=children)


# @syn.AstBuilder.build.register(syn.AxisParser.WhereBlockContext)
# def build_def_where(
#     self, _, _colon, *, children: tuple[syn.Block]
# ):
#     return Def.Where(children=children)


# @syn.AstBuilder.build.register(syn.AxisParser.TakesBlockContext)
# def build_def_takes(
#     self,
#     _,
#     name: Optional[str] = None,
#     *,
#     children: tuple[syn.Block],
# ):
#     return Def.Takes(name=name, children=children)


# @syn.AstBuilder.build.register(syn.AxisParser.ReturnsBlockContext)
# def build_def_returns(
#     self,
#     _,
#     expr: syn.Expr,
#     *,
#     children: tuple[syn.Block],
# ):
#     return Def.Returns(
#         expr=expr,
#         children=children,
#     )

# DEF_MATCH_SYMBOL = syn.Match.from_expr("$nm")
# DEF_MATCH_EXT_SYMBOL = syn.Match.from_expr("$nm: $ext")
# DEF_MATCH_FUNCTION = syn.Match.from_expr("$nm(..$args)")
# DEF_MATCH_METHOD = syn.Match.from_expr("$ctx.$nm(..$args)")


# @sem.Binder.discover.register(Def)
# def bind_def(parent: sem.Binder, def_: Def):

#     if vars := DEF_MATCH_SYMBOL(def_.expr):
#         name = vars.get("$nm")
#         parent.export_item(name, def_)
#     elif vars := DEF_MATCH_FUNCTION(def_.expr):
#         name = vars.get("$nm")
#         parent.export_item(name, def_)
#     elif vars := DEF_MATCH_METHOD(def_.expr):
#         name = vars.get("$nm")
#         parent.export_item(name, def_)
