
from __future__ import annotations

from typing import Iterable, Self

from protobase import derived

from axis.core import src

from .ast_builder import AstBuilder
from .node import Node


def derive_parse_block_content(block_type: type[Block]):
    from antlr4 import CommonTokenStream, InputStream
    from .grammar import AxisLexer, AxisParser
    from .item import Item

    prefix = block_type.__name__.lower()
    postfix = 'Item' if issubclass(block_type, Item) else 'Block'
    item = f"{prefix}{postfix}" # e.g. "unitItem" or "suiteBlock"

    def parser(cls, span: src.Span, children: tuple[Block]) -> dict:
        lexer = AxisLexer(InputStream(span.content))
        parser = AxisParser(CommonTokenStream(lexer))

        item_parser = getattr(parser, item, None)
        if item_parser is None:
            raise ValueError(f"Unknown parser for item {block_type} (search for {item})")

        tree = item_parser()

        if parser.getNumberOfSyntaxErrors() > 0:
            print(span.content)

        ast_builder = AstBuilder(span)
        result = ast_builder(tree, children=children)

        return result

    return parser


class Block(Node, src.Block, abstract=True):
    # todos los derivados de block se autoregistran en el parser
    children: tuple[Block]


    @derived(derive_parse_block_content)
    @classmethod
    def parse_block(cls, content: src.Span, children: tuple[Block]) -> Self:
        ...


    def iter[T: Block](self, *instanceof: type[T]) -> Iterable[T]:
        ''' 
        Iterates over the children of this block, filtering by type if specified.
        '''
        if instanceof == ():
            return iter(self.children)

        for child in self.children:
            if isinstance(child, instanceof):
                yield child

