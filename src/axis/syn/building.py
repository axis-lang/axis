from __future__ import annotations

from decimal import Decimal
from functools import singledispatchmethod
from sys import intern
from typing import ClassVar, Self
from warnings import warn

from antlr4 import (CommonTokenStream, InputStream, ParserRuleContext,
                    TerminalNode, Token)
from antlr4.tree.Tree import ErrorNodeImpl, TerminalNodeImpl, ParseTree
from protobase import Inmutable, mutate, is_abstract

from axis import src, syn
from ..literals import WILDCARD

from .grammar import AxisLexer, AxisParser

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


class Builder(Inmutable):

    source: src.Source.Span

    def __call__(self, ctx: ParseTree | TerminalNode, kwargs={}):
        if not isinstance(ctx, (ParserRuleContext | TerminalNode)):
            raise ValueError(
                f"Expected ParserRuleContext or TerminalNode, got {type(ctx)}"
            )

        if isinstance(ctx, ErrorNodeImpl):
            token = ctx.getSymbol()
            message = ctx.getText()
            print(type(token), type(ctx))
            #print('>>', ctx.getText())
            start, stop = token.start, token.stop

            try:
                span = self.source[start:stop]
            except Exception:
                span = self.source
            if isinstance(span, src.Source.Position):
                span = span.line

            if isinstance(span, src.Source.Position):
                span = span.line
            src.error("Syntax error").with_label(src.Label(span, message)).throw()

            raise ValueError(
                f"Unexpected error node '{token}' {token.source}"
            )  # TODO: generar ast con Errs

        if isinstance(ctx, (TerminalNodeImpl, TerminalNode)):
            token = ctx.getSymbol() # type: ignore
            start, stop = token.start, token.stop
            result = self.build(ctx, **kwargs)

        else:
            assert ctx.start is not None and ctx.stop is not None, f"Context {ctx} has no start or stop token"
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
            span = self.source[start:stop]
            if isinstance(span, src.Source.Position):
                span = span.line
            span.tag(result)

        return result

    @singledispatchmethod
    def build(self, ctx: ParserRuleContext, *args, **kwargs):
        if len(args) != 1 and len(kwargs) != 0:
            raise NotImplementedError(f"No AST builder for {type(ctx).__name__}, getting {args} and {kwargs}")
        return args[0]

        

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
                return intern(token.text)
            case AxisLexer.ELLIPSIS:
                return ...
            case AxisLexer.WILDCARD:
                return WILDCARD
            case AxisLexer.NONE:
                return None
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


class FromSrcMixin(Inmutable, abstract=True):
    __slots__ = ('__weakref__',)

    grammar_context_infix: ClassVar[str] = ''
    grammar_context_name: ClassVar[str]
    grammar_parser_name: ClassVar[str]

    @classmethod
    def __class_post_build__(cls):
        #super().__class_post_build__()
        if is_abstract(cls):
           return

        name = cls.__qualname__.replace(".", "") 
               
        if 'grammar_parser_name' not in cls.__dict__:
            lname = name[0].lower() + name[1:]
            cls.grammar_parser_name = f'{lname}{cls.grammar_context_infix}'

        if 'grammar_context_name' not in cls.__dict__:
            cls.grammar_context_name = f'{name}{cls.grammar_context_infix}Context'

        #print("Building grammar for", cls.__qualname__, cls.grammar_parser_name, cls.grammar_context_name)

        ctx_class = getattr(AxisParser, cls.grammar_context_name, None)
        if ctx_class is None:
            #warn(f'Grammar context not found for {cls.__qualname__} ({cls.grammar_context_name})', stacklevel=4)
            return

        @Builder.build.register(ctx_class) # type: ignore
        def build_ast(builder, ctx, *args, **kwargs):
            return cls.build(*args, **kwargs)

    @classmethod
    def build(cls, *args, **kwargs) -> Self:
        raise NotImplementedError(f'No build() method for {cls.__qualname__}')

    @classmethod
    def from_str(cls, src_span: src.Source.Span | str, **kwargs) -> Self:
        if isinstance(src_span, str):
            src_span = src.Source.Span.from_str(src_span)

        lexer = AxisLexer(InputStream(src_span.content))
        parser = AxisParser(CommonTokenStream(lexer))
        builder = Builder(src_span)

        parse = getattr(parser, cls.grammar_parser_name, None)
        if parse is None:
            raise ValueError(f"Unknown parser for {cls.__qualname__} (search for {cls.grammar_parser_name})")
        ast_tree = parse()

        if parser.getNumberOfSyntaxErrors() > 0:
            raise SyntaxError(f"{src_span}")# TODO: Only warns
        
        self = builder(ast_tree, kwargs)
        assert isinstance(self, cls), f"Expected {cls.__qualname__}, got {type(self)}, probably build() returned wrong type"
        return self

    def with_span_of(self, other: FromSrcMixin) -> Self:
        src.tag_span_from(other, self)
        return self

    def with_attr(self, **kwargs) -> Self:
        result = mutate(self, **kwargs)
        src.tag_span_from(self, result)
        return result

    @property
    def span(self) -> src.Source.Span | None:
        return src.span_of(self)

    #@property
    def as_label(self, *args, **kwargs):
        assert self.span is not None, f'Node {self!r} has no span'
        return src.Label(self.span, *args, **kwargs)
