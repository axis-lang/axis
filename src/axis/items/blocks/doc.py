from textwrap import dedent
from typing import ClassVar, Self
from axis import syn, src

class Doc(syn.Block, frozen=True):
    outline_keyword: ClassVar[str] = "---"
    outline_keyword_sep: ClassVar[str] = ""

    content: str    
    children: syn.Block.Children
    
    # @classmethod
    # def parse_bloock(cls, span: src.Span, children: tuple[syn.Block]) -> Self:
    #     """
    #     Parse the tree and return a Doc instance.
    #     """
    #     # discard children for now
    #     return cls(content=dedent(span.content), children=children)

    @classmethod
    def from_str(cls, src_span:src.Span|str, *, children, **kwargs) -> Self:
        content = src_span.content if isinstance(src_span, src.Span) else src_span
        return cls(content=content, children=children)

syn.Item.register_outline_children(Doc)