from typing import ClassVar, Literal
from axis import syn


class Where(syn.Block, frozen=True):
    """
    where:
        val N: Number
    """

    outline_keyword: ClassVar[str] = "where"
    outline_keyword_sep: ClassVar[str] = ": \t"
    #keyword_sep: ClassVar[str] = ": \t"
    #grammar: ClassVar[str] = "where: 'where' ':' EOF;"


    @classmethod
    def build(
        cls,
        kw: Literal["where"],
        sep: Literal[":"],
        *,
        pkg: ...,
        children: syn.Block.Children,
    ):
        
        return cls()
