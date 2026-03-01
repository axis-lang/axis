from textwrap import dedent
from typing import ClassVar, Self
from axis import syn, src
from protobase import Inmutable


class Doc(syn.Block, Inmutable):
    outline_keyword: ClassVar[str] = "---"
    outline_keyword_sep: ClassVar[str] = ""

    content: str
    children: syn.Block.Children

    # @classmethod
    # def parse_bloock(cls, span: src.Source.Span, children: tuple[syn.Block]) -> Self:
    #     """
    #     Parse the tree and return a Doc instance.
    #     """
    #     # discard children for now
    #     return cls(content=dedent(span.content), children=children)

    @classmethod
    def from_str(cls, src_span: src.Source.Span | str, *, children, **kwargs) -> Self:
        content = src_span.content if isinstance(src_span, src.Source.Span) else src_span
        return cls(content=content, children=children)


syn.Item.register_outline_children(Doc)
