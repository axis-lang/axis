from typing import ClassVar, Literal
from axis import syn


class Where(syn.Block):
    """
    where:
        val N: Number
    """

    keyword: ClassVar[str] = "where"
    keyword_sep: ClassVar[str] = ": \t"
    grammar: ClassVar[str] = "where: 'where' ':' EOF;"

    @classmethod
    def build(
        cls,
        kw: Literal["where"],
        colon: Literal[":"],
        *,
        children: syn.Block.Children,
    ):
        return cls(children=children)
