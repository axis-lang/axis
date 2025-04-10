from decimal import Decimal
from functools import singledispatch
from pathlib import Path
from sys import intern
from typing import Literal, Optional, Union

from antlr4 import (CommonTokenStream, InputStream, ParserRuleContext,
                    TerminalNode, Token)
from antlr4.tree.Tree import TerminalNodeImpl
from protobase import Object, litdispatch
from rich import print

from axis.parsing.grammar import AxisLexer, AxisParser
from axis.parsing.srcblock import Parser as OutlineParser
from axis.parsing.srcblock import SrcBlock
from axis.std import syn

from .AxisLexer import AxisLexer
from .AxisParser import AxisParser

IGNORE = object()


def itertree(ctx: ParserRuleContext, fn):
    assert isinstance(
        ctx, (ParserRuleContext | TerminalNode)
    ), f"Expected ParserRuleContext or TerminalNode, got {type(ctx)}"

    if isinstance(ctx, TerminalNodeImpl):
        return fn(ctx, ctx.getSymbol())
    else:
        return fn(
            ctx,
            *[
                param
                for child in ctx.getChildren()
                if (param := itertree(child, fn)) is not IGNORE
            ],
        )

@singledispatch
def build_ast(ctx, *values):
    raise NotImplementedError(f"No AST builder for {type(ctx)}")


IGNORED_TOKENS = {
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    ";",
    ".",
    ",",
    "=",
    "def",
    "var",
    "fn",
}


@build_ast.register
def _terminal(ctx: TerminalNodeImpl, token: Token):
    match token.type:
        case AxisLexer.DECIMAL:
            return Decimal(token.text)
        case AxisLexer.ID:
            return intern(token.text)
        case AxisLexer.TEXT:
            return token.text
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
        ):
            return intern(token.text)
        case _:
            if token.text in IGNORED_TOKENS:
                return IGNORE

    raise NotImplementedError(f"Unknown terminal {token.text}")


@build_ast.register
def _def_item(_: AxisParser.DefItemContext, expr: syn.Expr):
    return dict(expr=expr)


@build_ast.register
def _ast_pass(
    ctx: Union[
        AxisParser.PassContext,
        AxisParser.DecimalContext,
        AxisParser.IdentifierContext,
        AxisParser.LiteralContext,
        AxisParser.PrimaryExprContext,
        AxisParser.ExpressionContext,
    ],
    val,
):
    return val


@build_ast.register
def _binary_operation(
    ctx: Union[
        AxisParser.ProductContext,
        AxisParser.AdditionContext,
        AxisParser.ComparisonExprContext,
        AxisParser.LogicalExprContext,
    ],
    lhs,
    *vals,
):
    for operator, operand in zip(vals[::2], vals[1::2]):
        lhs = syn.BinaryOperation(
            op=syn.BinaryOperation.Operator(operator),
            lhs=lhs,
            rhs=operand,
        )
    return lhs


@build_ast.register
def _call(
    _: AxisParser.CallContext,
    function: syn.Expr,
    argument: syn.Tuple,
):
    return syn.Call(function, argument, None)


@build_ast.register
def _trailing_call(
    _: AxisParser.TrailingCallContext,
    base: syn.Expr,
    trailing: syn.Expr = None,
):
    if isinstance(base, syn.Call):
        return syn.Call(base.function, base.argument, trailing)

    return syn.Call(base, None, trailing)


@build_ast.register
def _compound(
    ctx: AxisParser.JuxtapositionExprContext,
    *params,
):

    if len(params) == 1:
        return params[0]
    return syn.Compound(params)


@build_ast.register
def _suite(
    ctx: AxisParser.SuiteContext,
    *statements,
):
    if len(statements) == 1 and isinstance(statements[0], syn.Expr):
        return statements[0]
    return syn.Suite(statements=statements)


@build_ast.register
def _tuple(_: AxisParser.TupleContext, *elements):
    return syn.Tuple(elements=tuple(elements))


@build_ast.register
def _tuple_element_single(_: AxisParser.TupleElementSingleContext, value: syn.Expr):
    return syn.Tuple.Element(key=None, bound=None, value=value)


@build_ast.register
def _tuple_element_assignation(
    _: AxisParser.TupleElementAssignationContext, key: syn.Expr, value: syn.Expr
):
    return syn.Tuple.Element(key=key, value=value)


@build_ast.register
def _tuple_element_bounded(
    _: AxisParser.TupleElementBoundedContext, key: syn.Expr, bound: syn.Expr
):
    return syn.Tuple.Element(key=key, bound=bound)


@build_ast.register
def _tuple_element_bounded_assignation(
    _: AxisParser.TupleElementBoundedAssignationContext,
    key: syn.Expr,
    bound: syn.Expr,
    value: syn.Expr,
):
    return syn.Tuple.Element(key=key, bound=bound, value=value)

def ast_parser_for(item: Literal["def", "val", "fn"]):

    def parser(source: str) -> dict:
        lexer = AxisLexer(InputStream(source))
        stream = CommonTokenStream(lexer)
        parser = AxisParser(stream)

        item_parser = getattr(parser, item, None)

        if item_parser is None:
            raise ValueError(f"Unknown parser for item {item}")

        tree = item_parser()

        return itertree(tree, build_ast)

    return parser

