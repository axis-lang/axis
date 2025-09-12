from typing import ClassVar, Literal
from axis import syn


class Returns(syn.Block):
    """ """

    keyword: ClassVar[str] = "returns"
    grammar: ClassVar[str] = "returns: 'returns' expression EOF;"

    expr: syn.Expr

    @classmethod
    def build(
        cls,
        kw: Literal["returns"],
        expr: syn.Expr,
        *,
        children: syn.Block.Children,
    ):
        return cls(expr=expr, children=children)
