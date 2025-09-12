from __future__ import annotations
from protobase import Object, Record, cached_property
from typing import ClassVar, Literal, Optional
from axis import items, syn, sem, log, expr, val


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
        name: expr.Sym

    class ClassKind(Kind):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.parse("$name@Sym"),
            syn.Expr.parse("$name[..$generics]"),
        )

        generics: Optional[expr.Tuple] = None

    class FunctionKind(Kind):
        match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
            syn.Expr.parse("$name@Sym(..$arguments)"),
            syn.Expr.parse("$context.$name(..$arguments)"),
        )

        arguments: Optional[expr.Tuple] = None
        context: Optional[syn.Expr] = None


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

    class Binding(sem.Binding):
        item: Def

        @property
        def ref(self):
            return self.parent.ref.member(self.item.kind.name.name)



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
