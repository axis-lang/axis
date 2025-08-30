from typing import ClassVar, Optional, Self

from rich import print
from protobase import cached_property
from axis.core import sem, syn
from axis.std.expr import Sym, Tuple
from axis.std.transcriptions.destructuring import reify_destructure


class Use(syn.Block):
    """
    Represents a 'use' entity:
    use x
    """

    keyword: ClassVar[str] = "use"
    grammar: ClassVar[str] = "use: 'use' expression EOF;"


    expr: syn.Expr #

    @classmethod
    def build(cls, kw: str, expr: syn.Expr, *, children: tuple[syn.Block]) -> Self:
        return cls(expr=expr)

    @cached_property
    def flat_expr(self) -> Tuple:
        return reify_destructure(self.expr, from_=Sym.ROOT)


@syn.AstBuilder.build.register(syn.AxisParser.UseBlockContext)
def build_use_ast(
    self,
    _,
    kw: str,
    expr: syn.Expr,
    *,
    children: tuple[syn.Block],
):
    return Use(expr=expr, children=children)


@sem.Binder.discover.register(Use)
def discover_use(self: sem.Binder, use: Use):
    #print(use.flat_expr)

    for elem in use.flat_expr:
        if isinstance(elem, Tuple.NominalElement):
            self.import_ref(elem.key, elem.value)
        elif isinstance(elem, Tuple.SpreadElement):
            self.import_ref(..., elem.etc)

    # TODO: declare binding imports

