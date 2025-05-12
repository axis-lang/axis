from typing import ClassVar
from axis.core import syn, sem
from .mod import Mod


class Unit(Mod):
    """ """

    keyword: ClassVar = "unit"
    grammar: ClassVar = "unit: 'unit' expression ':' EOF;"


@syn.AstBuilder.build.register(syn.AxisParser.UnitItemContext)
def build_ast(
    self,
    _,
    path: syn.Expr,
    *,
    children: tuple[syn.Block],
):
    return Unit(path=path, children=children)
