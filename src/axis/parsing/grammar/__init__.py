from decimal import Decimal
from functools import singledispatch
from sys import intern
from typing import Literal, Union

from antlr4 import (CommonTokenStream, InputStream, ParserRuleContext,
                    TerminalNode, Token)
from antlr4.tree.Tree import ErrorNodeImpl, TerminalNodeImpl
from rich import print

from axis.parsing.grammar import AxisLexer, AxisParser
from axis.std import syn

from .AxisLexer import AxisLexer
from .AxisParser import AxisParser

IGNORE = object()


def itertree(ctx: ParserRuleContext, fn):
    assert isinstance(
        ctx, (ParserRuleContext | TerminalNode)
    ), f"Expected ParserRuleContext or TerminalNode, got {type(ctx)}"

    if isinstance(ctx, ErrorNodeImpl):
        raise ValueError(f"Unexpected error node '{ctx.getSymbol()}'") # TODO: generar ast con Errs

    if isinstance(ctx, TerminalNodeImpl):
        return fn(ctx, ctx.getSymbol())

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
    ";",
    ".",
    ",",
    "def",
    "returns",
    "val",
    "fn",
}


@build_ast.register
def _terminal(ctx: TerminalNodeImpl, token: Token):
    if isinstance(ctx, ErrorNodeImpl):
        return syn.UnexpectedErr(unexpected=token.text)

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


@build_ast.register
def _def_item(_: AxisParser.DefItemContext, expr: syn.Expr, *more):
    print(more)
    return dict(expr=expr)


@build_ast.register
def _val_item(_: AxisParser.ValItemContext, as_: syn.Expr, *more):
    bound = None
    value = None
    for operator, operand in zip(more[::2], more[1::2]):
        if operator == ":":
            bound = operand
        elif operator == "=":
            value = operand
        else:
            raise ValueError(f"Unknown operator {operator}")

    return dict(as_=as_, bound=bound, value=value)


@build_ast.register
def _returns_block(_: AxisParser.ReturnsBlockContext, expr: syn.Expr):
    return dict(expr=expr)


@build_ast.register
def _suite_block(_: AxisParser.SuiteBlockContext, *statements: syn.Node):
    return dict(statements=statements)


@build_ast.register
def _ast_pass(
    ctx: Union[
        AxisParser.PassContext,
        AxisParser.DecimalContext,
        AxisParser.IdentifierContext,
        AxisParser.LiteralContext,
        AxisParser.PrimaryExprContext,
        AxisParser.ExpressionContext,
        AxisParser.EllipsisContext,
        AxisParser.WildcardContext,
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
    _: AxisParser.TrailingLambdaContext,
    base: syn.Expr,
    trailing: syn.Expr = None,
):
    if isinstance(base, syn.Call):
        return syn.Call(base.function, base.argument, trailing)
    return syn.Call(base, None, trailing) # try trail sugar node?

@build_ast.register
def _spread(
    _: AxisParser.SpreadContext,
    _ellipsis,
    expr: syn.Expr,
):
    return syn.Spread(expr)


@build_ast.register
def _compound(
    ctx: AxisParser.JuxtapositionExprContext,
    *components,
):
    if len(components) == 1:
        return components[0]
    return syn.Compound(components=tuple(components))


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
    _: AxisParser.TupleElementAssignationContext, key: syn.Expr, _assign, value: syn.Expr
):
    return syn.Tuple.Element(key=key, bound=None, value=value)


@build_ast.register
def _tuple_element_bounded(
    _: AxisParser.TupleElementBoundedContext, key: syn.Expr, _colon, bound: syn.Expr
):
    return syn.Tuple.Element(key=key, bound=bound, value=None)


@build_ast.register
def _tuple_element_bounded_assignation(
    _: AxisParser.TupleElementBoundedAssignationContext,
    key: syn.Expr,
    _colon,
    bound: syn.Expr,
    _assign,
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
