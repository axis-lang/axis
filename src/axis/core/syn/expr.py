from __future__ import annotations
from pathlib import Path
from axis.core import src
from .building import AstBuilder
from .statement import Statement

class Expr(Statement, abstract=True): 
    

    @classmethod
    def parse(cls, buffer: str | src.Span, **opts) -> Expr:
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

        return ast_builder(tree)



