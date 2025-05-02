from decimal import Decimal
from functools import singledispatch, singledispatchmethod
from sys import intern
from typing import Optional, Union

from antlr4 import ParserRuleContext, TerminalNode, Token
from antlr4.tree.Tree import ErrorNodeImpl, TerminalNodeImpl

from axis.dom import src, syn

from .abstract import *
from .blocks import *
from .expr import *
from .grammar import AxisLexer, AxisParser
from .items import *

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
            src.Location(self.source[start: stop]).tag(result)

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

    #####################################################################
    ## Expressions
    #####################################################################

    @build.register
    def build_sym(self, ctx: Union[AxisParser.IdentifierContext], val: str):
        return syn.Sym(val)

    @build.register
    def build_literal(
        self,
        ctx: Union[AxisParser.LiteralContext],
        val: str | Decimal | bool | None,
    ):
        return syn.Lit(val)

    @build.register
    def build_tuple(
        self, ctx: AxisParser.TupleContext | AxisParser.ShapeContext, *elements
    ):
        return syn.Tuple(elements=tuple(elements))

    @build.register
    def build_tuple_element_single(
        self, ctx: AxisParser.TupleElementSingleContext, value: syn.Expr
    ):
        return syn.Tuple.Element(key=None, bound=None, value=value)

    @build.register
    def build_tuple_element_assignation(
        self,
        ctx: AxisParser.TupleElementAssignationContext,
        key: syn.Expr,
        _assign,
        value: syn.Expr,
    ):
        return syn.Tuple.Element(key=key, bound=None, value=value)

    @build.register
    def build_tuple_element_bounded(
        self,
        ctx: AxisParser.TupleElementBoundedContext,
        key: syn.Expr,
        _colon,
        bound: syn.Expr,
    ):
        return syn.Tuple.Element(key=key, bound=bound, value=None)

    @build.register
    def build_tuple_element_bounded_assignation(
        self,
        ctx: AxisParser.TupleElementBoundedAssignationContext,
        key: syn.Expr,
        _colon,
        bound: syn.Expr,
        _assign,
        value: syn.Expr,
    ):
        return syn.Tuple.Element(key=key, bound=bound, value=value)

    @build.register
    def build_binary_operation(
        self,
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

    @build.register
    def build_member_access(
        self,
        ctx: AxisParser.MemberAccessContext,
        of,
        *members: str,
    ):
        result = of
        for member in members:
            result = syn.Member(
                of=result,
                sym=member,
            )
        return result

    @build.register
    def build_call(
        self,
        ctx: AxisParser.CallContext,
        function: syn.Expr,
        argument: syn.Tuple,
    ):
        return syn.Apply(function, argument, None)

    @build.register
    def build_trailing_call(
        self,
        ctx: AxisParser.TrailingLambdaContext,
        base: syn.Expr,
        trailing: syn.Expr = None,
    ):
        if isinstance(base, syn.Apply):
            return syn.Apply(base.function, base.argument, trailing)
        return syn.Apply(base, None, trailing)  # try trail sugar node?

    @build.register
    def build_index(
        self,
        ctx: AxisParser.IndexContext,
        container: syn.Expr,
        indice: syn.Tuple,
    ):
        return syn.Index(container, indice)

    @build.register
    def build_spread(
        self,
        ctx: AxisParser.SpreadContext,
        _ellipsis,
        expr: syn.Expr,
    ):
        return syn.Spread(expr)

    @build.register
    def build_compound(
        self,
        ctx: AxisParser.JuxtapositionExprContext,
        *components,
    ):
        if len(components) == 1:
            return components[0]
        return syn.Compound(components=tuple(components))

    @build.register
    def build_expression_suite(
        self,
        ctx: AxisParser.SuiteContext,
        *statements,
    ):
        if len(statements) == 1 and isinstance(statements[0], syn.Expr):
            return statements[0]
        return syn.Suite(statements=statements)
