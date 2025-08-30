from textwrap import dedent
from typing import ClassVar, Self
from axis.core import syn, src

class Doc(syn.Block):
    keyword: ClassVar[str] = "---"
    keyword_sep: ClassVar[str] = ""

    content: str    
    
    @classmethod
    def parse_block(cls, span: src.Span, children: tuple[syn.Block]) -> Self:
        """
        Parse the tree and return a Doc instance.
        """
        return cls(
            children=children,
            content=dedent(span.content)
        )

syn.Item.add_child_block(Doc, must_be_indented=None)