from typing import ClassVar, Literal
from axis import syn


class Extends(syn.Block):
    """ """

    keyword: ClassVar[str] = "extends"
    grammar: ClassVar[str] = "extends: 'extends' expression EOF;"

    expr: syn.Expr

    @classmethod
    def build(
        cls,
        kw: Literal["extends"],
        expr: syn.Expr,
        *,
        children: syn.Block.Children,
    ):
        return cls(expr=expr, children=children)
