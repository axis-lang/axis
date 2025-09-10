from __future__ import annotations

from typing import ClassVar, Iterable, Self

from protobase import derived

from axis.core import src, sem

from .building import AstBuilder
from .node import Node


def impl_parse_block_content(block_type: type[Block]):
    from antlr4 import CommonTokenStream, InputStream

    from .grammar import AxisLexer, AxisParser
    from .item import Item

    prefix = block_type.__name__.lower()
    postfix = 'Item' if issubclass(block_type, Item) else 'Block'
    item = f"{prefix}{postfix}" # e.g. "unitItem" or "suiteBlock"

    def parser(cls, span: src.Span, children: tuple[Block], **opts) -> dict:
        lexer = AxisLexer(InputStream(span.content))
        parser = AxisParser(CommonTokenStream(lexer))

        item_parser = getattr(parser, item, None)
        if item_parser is None:
            raise ValueError(f"Unknown parser for item {block_type} (search for {item})")

        tree = item_parser()

        if parser.getNumberOfSyntaxErrors() > 0:
            print(span.content)

        ast_builder = AstBuilder(span, **opts)
        
        result = ast_builder(tree, children=children)

        return result

    return parser



class Block(Node, src.Block, abstract=True):
    # todos los derivados de block se autoregistran en el parser
    type Children = tuple[Block, ...]
    grammar_context_infix: ClassVar[str] = 'Block'
    children: Children


    @derived(impl_parse_block_content)
    @classmethod
    def parse_block(cls, content: src.Span, children: Children) -> Self:
        ...

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)

    def contribute_to_scope(self, scope: sem.Scope.Builder) -> None:
        for child in self.children:
            child.contribute_to_scope(scope)
