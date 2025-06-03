from __future__ import annotations
from pathlib import Path
from axis.core import src
from .building import AstBuilder
from .node import Node


class Statement(Node, abstract=True): 
    ...

    @classmethod
    def parse(cls, buffer: str | src.Span, **opts) -> Statement:
        from antlr4 import CommonTokenStream, InputStream

        from .grammar import AxisLexer, AxisParser
        
        if isinstance(buffer, str):
            buffer = src.Span(src.File(Path('<unnamed>.ax'), buffer), 0, len(buffer))

        lexer = AxisLexer(InputStream(buffer.content))
        parser = AxisParser(CommonTokenStream(lexer))

        tree = parser.statement()

        if parser.getNumberOfSyntaxErrors() > 0:
            print(buffer.content)

        ast_builder = AstBuilder(buffer, **opts)

        return ast_builder(tree)



