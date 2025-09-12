from typing import ClassVar, Literal, Optional
from axis import syn

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
        colon: Literal[":"],
        name: Optional[str] = None,
        *,
        children: syn.Block.Children,
    ):
        return cls(name=name, children=children)
