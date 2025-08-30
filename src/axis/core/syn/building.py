from decimal import Decimal
from functools import singledispatchmethod
from sys import intern
from typing import ClassVar

from antlr4 import ParserRuleContext, TerminalNode, Token
from antlr4.tree.Tree import ErrorNodeImpl, TerminalNodeImpl

from axis.core import src, syn

from .grammar import AxisLexer, AxisParser
from protobase import Object

IGNORE = object()

IGNORED_TOKENS = {
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ";",
    ".",
    ",",
}


class AstBuilder(Object):

    pass_contexts: ClassVar[set[type[ParserRuleContext]]] = {
        AxisParser.PrimaryContext,
        AxisParser.PostfixPassContext,
        AxisParser.PostfixContext,
        AxisParser.PrefixPassContext,
        AxisParser.PrefixContext,
        AxisParser.ExpressionContext,
        AxisParser.StatementContext,
    }

    source: src.Span

    @classmethod
    def decl_pass_context(cls, ctx_type: type[ParserRuleContext]):
        cls.pass_contexts.add(ctx_type)

    def __call__(self, ctx: ParserRuleContext | TerminalNode, **kwargs):
        if not isinstance(ctx, (ParserRuleContext | TerminalNode)):
            raise ValueError(
                f"Expected ParserRuleContext or TerminalNode, got {type(ctx)}"
            )

        if isinstance(ctx, ErrorNodeImpl):
            token = ctx.getSymbol()
            raise ValueError(
                f"Unexpected error node '{token}' {token.source}"
            )  # TODO: generar ast con Errs

        if isinstance(ctx, (TerminalNodeImpl, TerminalNode)):
            token = ctx.getSymbol()
            start, stop = token.start, token.stop
            result = self.build(ctx, **kwargs)

        else:
            start, stop = ctx.start.start, ctx.stop.stop + 1

            params = [
                param
                for child in ctx.getChildren()
                if (param := self(child)) is not IGNORE
            ]

            try:
                result = self.build(ctx, *params, **kwargs)
            except Exception as e:
                e.add_note(f"Error building AST for {type(ctx)}: with params: {params}")
                raise

        if isinstance(result, syn.Node):
            self.source[start:stop].tag(result)

        return result

    @singledispatchmethod
    def build(self, ctx: ParserRuleContext, *args):
        if type(ctx) in self.pass_contexts:
            if len(args) != 1:
                raise ValueError(
                    f"Expected 1 argument for {type(ctx)}, got {len(args)}"
                )

            return args[0]

        raise NotImplementedError(f"No AST builder for {type(ctx)}")

    #####################################################################
    ## TERMINALS
    #####################################################################

    @build.register
    def build_terminal(self, ctx: TerminalNodeImpl):
        token: Token = ctx.getSymbol()
        match token.type:
            case AxisLexer.DECIMAL:
                return Decimal(token.text)
            case AxisLexer.ID:
                return intern(token.text)
            case AxisLexer.TEXT:
                return token.text
            # case AxisLexer.ELLIPSIS:
            #     return ...
            # case AxisLexer.WILDCARD:
            #     return None
            # case (
            #     AxisLexer.ADD
            #     | AxisLexer.SUB
            #     | AxisLexer.MUL
            #     | AxisLexer.DIV
            #     | AxisLexer.MOD
            #     | AxisLexer.EQ
            #     | AxisLexer.NE
            #     | AxisLexer.LT
            #     | AxisLexer.LE
            #     | AxisLexer.GT
            #     | AxisLexer.GE
            #     | AxisLexer.AND
            #     | AxisLexer.OR
            #     | AxisLexer.ASSIGN
            #     | AxisLexer.COLON
            # ):
            #     return intern(token.text)
            case Token.EOF:
                return IGNORE

            # case _:
        if token.text in IGNORED_TOKENS:
            return IGNORE

        return intern(token.text)

        # raise NotImplementedError(f"Unknown terminal {token.text}")
