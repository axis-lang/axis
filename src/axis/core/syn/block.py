
from __future__ import annotations
from typing import ClassVar, Iterable, Optional, Self
from axis.core import src
from .node import Node

class Block(Node, src.Block, abstract=True):
    # todos los derivados de block se autoregistran en el parser
    children: tuple[Block]


    @classmethod
    def parse_block(cls, content: src.Span, children: tuple[Block]) -> Self:
        return cls(
            children=children,
            **cls.parse_block_content(content),
        )

    @classmethod
    def parse_block_content(cls, content: src.Span) -> dict:
        raise NotImplementedError(
            f"Block {cls.__qualname__} does not implement parse_block_content()"
        )

    def iter[T: Block](self, *instanceof: type[T]) -> Iterable[T]:
        ''' 
        Iterates over the children of this block, filtering by type if specified.
        '''
        if instanceof == ():
            return iter(self.children)

        for child in self.children:
            if isinstance(child, instanceof):
                yield child

