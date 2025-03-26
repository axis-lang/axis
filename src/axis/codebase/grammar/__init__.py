# %%
from functools import singledispatch
from typing import Union
from antlr4 import *
from antlr4.tree.Tree import TerminalNodeImpl
from .AxisLexer import AxisLexer
from .AxisParser import AxisParser
from rich import print
from decimal import Decimal

from ..ast import expr

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


def dump(ctx, *vals):
    print(type(ctx), ctx.getText(), *vals)


@singledispatch
def ast_builder(ctx, *values):
    raise NotImplementedError(f"No AST builder for {type(ctx)}")


@ast_builder.register
def _terminal(ctx: TerminalNodeImpl, token: Token):
    match token.type:
        case AxisLexer.DECIMAL:
            return Decimal(token.text)
        case AxisLexer.ID:
            return expr.Id(token.text)
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
            return token.text
        case _:
            match token.text:
                case "(" | ")" | "[" | "]" | "{" | "}" | ":" | ";" | "." | "," | "=":
                    return IGNORE
                case _:
                    pass

    raise NotImplementedError(f"Unknown terminal {token.text}")


@ast_builder.register
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


@ast_builder.register
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
        lhs = expr.BinaryOperation(
            op=expr.BinaryOperation.Operator(operator),
            lhs=lhs,
            rhs=operand,
        )
    return lhs


@ast_builder.register
def _call(
    _: AxisParser.CallContext,
    function: expr.Expr,
    argument: expr.Tuple,
):
    return expr.Call(function, argument, None)


@ast_builder.register
def _trailing_call(
    _: AxisParser.TrailingCallContext,
    base: expr.Expr,
    trailing: expr.Expr = None,
):
    if isinstance(base, expr.Call):
        return expr.Call(base.function, base.argument, trailing)

    return expr.Call(base, None, trailing)


@ast_builder.register
def _compound(
    ctx: AxisParser.JuxtapositionExprContext,
    *params,
):

    if len(params) == 1:
        return params[0]
    return expr.Compound(params)


@ast_builder.register
def _suite(
    ctx: AxisParser.SuiteContext,
    *statements,
):
    if len(statements) == 1 and isinstance(statements[0], expr.Expr):
        return statements[0]
    return expr.Suite(statements=statements)


@ast_builder.register
def _tuple(
    ctx: AxisParser.TupleContext,
    *elements,
):
    return expr.Tuple(elements)


@ast_builder.register
def _unnamed_tuple_element(
    _: AxisParser.UnnamedTupleElementContext,
    value: expr.Expr,
):
    return expr.Tuple.UnnamedElement(value)


@ast_builder.register
def _named_tuple_element(
    _: AxisParser.NamedTupleElementContext,
    key: expr.Id,
    value: expr.Expr,
):
    return expr.Tuple.NamedElement(key=key, value=value)


@ast_builder.register
def _dynamic_tuple_element(
    _: AxisParser.DynamicTupleElementContext,
    dynkey: expr.Expr,
    value: expr.Expr,
):
    return expr.Tuple.DynamicElement(dynkey=dynkey, value=value)

#  { x: Number -> Number }
@ast_builder.register
def _spread_tuple_element(
    _: AxisParser.NamedTupleElementContext,
    spread: expr.Expr,
):
    return expr.Tuple.SpreadElement(spread=spread)


def parse(item: str, source: str ):
    lexer = AxisLexer(InputStream(source))
    stream = CommonTokenStream(lexer)
    parser = AxisParser(stream)

    item_parser = getattr(parser, item, None)

    if item_parser is None:
        raise ValueError(f"Unknown parser item {item}")

    tree = item_parser()

    return itertree(tree, ast_builder)


source = "a(1,2,3) {3} ese { 4 }"
lexer = AxisLexer(InputStream(source))
stream = CommonTokenStream(lexer)
parser = AxisParser(stream)
tree = parser.expression()

a = itertree(tree, ast_builder)
a
# {1,2,3}
