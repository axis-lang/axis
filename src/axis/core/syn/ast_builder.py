from decimal import Decimal
from functools import singledispatchmethod
from sys import intern
from typing import Optional, Union

from antlr4 import ParserRuleContext, TerminalNode, Token
from antlr4.tree.Tree import ErrorNodeImpl, TerminalNodeImpl

from axis.core import src, syn

from .node import *
from .block import *
from .expr import *
from .grammar import AxisLexer, AxisParser
from .item import *

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
    "unit",
    "mod",
    "use",
    "val",
    "def",
    "returns",
    "takes",
    "where",
    "suite",
    "fn",
}

IGNORED_CONTEXTS = {
    AxisParser.PassContext,
    AxisParser.PrimaryExprContext,
    AxisParser.ExpressionContext,
    AxisParser.EllipsisContext,
    AxisParser.WildcardContext,
    AxisParser.StatementContext,
}


class AstBuilder(Record):
    source: src.Span

    def __call__(self, ctx: ParserRuleContext | TerminalNode):
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
            result = self.build(ctx)
            
        else:
            start, stop = ctx.start.start, ctx.stop.stop+1
            result = self.build(
                ctx,
                *[
                    param
                    for child in ctx.getChildren()
                    if (param := self(child)) is not IGNORE
                ],
            )

        if isinstance(result, syn.Node):
            self.source[start: stop].tag(result)

        return result

    @singledispatchmethod
    def build(self, ctx: ParserRuleContext, *args):
        if type(ctx) in IGNORED_CONTEXTS:
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
        # if isinstance(ctx, ErrorNodeImpl):
        #     return syn.UnexpectedErr(unexpected=token.text)

        token: Token = ctx.getSymbol()

        match token.type:
            case AxisLexer.DECIMAL:
                return Decimal(token.text)
            case AxisLexer.ID:
                return intern(token.text)
            case AxisLexer.TEXT:
                return token.text
            case AxisLexer.ELLIPSIS:
                return ...
            case AxisLexer.WILDCARD:
                return None
            case (
                AxisLexer.ADD
                | AxisLexer.SUB
                | AxisLexer.MUL
                | AxisLexer.DIV
                | AxisLexer.MOD
                | AxisLexer.EQ
                | AxisLexer.NE
                | AxisLexer.LT
                | AxisLexer.LE
                | AxisLexer.GT
                | AxisLexer.GE
                | AxisLexer.AND
                | AxisLexer.OR
                | AxisLexer.ASSIGN
                | AxisLexer.COLON
            ):
                return intern(token.text)
            case Token.EOF:
                return IGNORE

            case _:
                if token.text in IGNORED_TOKENS:
                    return IGNORE

        raise NotImplementedError(f"Unknown terminal {token.text}")

    #####################################################################
    ## Blocks
    #####################################################################

    @build.register
    def build_unit(self, _: AxisParser.UnitItemContext, expr: syn.Expr):
        return dict(expr=expr)

    @build.register
    def build_mod(self, _: AxisParser.ModItemContext, expr: syn.Expr):
        return dict(expr=expr)

    @build.register
    def build_def(self, _: AxisParser.DefItemContext, expr: syn.Expr):
        return dict(expr=expr)

    @build.register
    def build_use(self, _: AxisParser.UseItemContext, expr: syn.Expr, *more):
        bound = None
        value = None
        for operator, operand in zip(more[::2], more[1::2]):
            if operator == ":":
                bound = operand
            elif operator == "=":
                value = operand
            else:
                raise ValueError(f"Unknown operator {operator}")

        return dict(expr=expr, bound=bound, value=value)

    @build.register
    def build_val(self, _: AxisParser.ValItemContext, expr: syn.Expr, *more):
        bound = None
        value = None
        for operator, operand in zip(more[::2], more[1::2]):
            if operator == ":":
                bound = operand
            elif operator == "=":
                value = operand
            else:
                raise ValueError(f"Unknown operator {operator}")

        return dict(expr=expr, bound=bound, value=value)

    @build.register
    def build_takes(self, _: AxisParser.TakesBlockContext, id: Optional[str] = None):
        return dict(id=id)

    @build.register
    def build_where(self, _: AxisParser.WhereBlockContext, *more):
        return dict()

    @build.register
    def _returns_block(self, _: AxisParser.ReturnsBlockContext, expr: syn.Expr):
        return dict(expr=expr)

    @build.register
    def build_suite(self, _: AxisParser.SuiteBlockContext, *statements: syn.Node):
        return dict(statements=statements)
