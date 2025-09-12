from __future__ import annotations
from pathlib import Path
from typing import ClassVar, Self
from axis import src
from .building import AstBuilder
from .node import Node


class Statement(Node, abstract=True): 
    grammar_context_infix: ClassVar[str] = 'Statement'

    @classmethod
    def parse(cls, buffer: str | src.Span, **opts) -> Self:
        from antlr4 import InputStream, CommonTokenStream
        from .grammar import AxisLexer, AxisParser
        
        if isinstance(buffer, str):
            buffer = src.Span(src.File(Path('<unnamed>.ax'), buffer), 0, len(buffer))

        lexer = AxisLexer(InputStream(buffer.content))
        parser = AxisParser(CommonTokenStream(lexer))

        tree = parser.statement()

        if parser.getNumberOfSyntaxErrors() > 0:
            print(buffer.content)

        ast_builder = AstBuilder(buffer, **opts)
        
        expr = ast_builder(tree) 

        assert isinstance(expr, cls), f"Expected {cls}, got {type(expr)}"

        return expr



