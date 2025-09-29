from typing import ClassVar, Literal
from axis import syn


class Returns(syn.Block, frozen=True):
    """ """

    outline_keyword: ClassVar[str] = "returns"
    grammar: ClassVar[str] = "returns: 'returns' expression EOF;"

    return_type_expr: syn.Expr

    @classmethod
    def build(
        cls,
        kw: Literal["returns"],
        expr: syn.Expr,
        *,
        pkg: ...,
        children: syn.Block.Children,
    ):
        return cls(return_type_expr=expr)
