from textwrap import dedent
from typing import ClassVar, Self
from axis import syn, src

class Doc(syn.Block, frozen=True):
    outline_keyword: ClassVar[str] = "---"
    outline_keyword_sep: ClassVar[str] = ""

    content: str    
    
    @classmethod
    def parse_block(cls, span: src.Span, children: tuple[syn.Block]) -> Self:
        """
        Parse the tree and return a Doc instance.
        """
        # discard children for now
        return cls(content=dedent(span.content))

syn.Item.register_outline_children(Doc)