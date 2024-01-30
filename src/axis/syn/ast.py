from __future__ import annotations

from pathlib import Path
from sys import intern
from typing import Callable, Optional

import lark
from protobase import Base, traits, fields_of

from axis.syn.val import Value
from axis.syn import op


class AST(traits.Cmp, traits.Hash, traits.Inmutable, traits.Repr, traits.Init):
    @classmethod
    def builder(cls, **kwargs):
        fields = dict(fields_of(cls))
        for kw in kwargs:
            fields.pop(kw)
        return lambda _, children: cls(**dict(zip(fields, children)), **kwargs)


class Span(Base, AST):
    start: int
    end: int

    @classmethod
    def from_ast(cls, ast):
        return cls(start=ast.start_pos, end=ast.end_pos)


class Lit(Base, AST):
    value: Value
    span: Optional[Span] = None

    @classmethod
    def from_ast(cls, ast, as_type: type[T]):
        return cls(value=as_type(ast.value), span=Span.from_ast(ast))


class Id(Base, AST):
    name: str
    span: Optional[Span] = None

    @classmethod
    def from_ast(cls, ast):
        return cls(name=intern(ast.value), span=Span.from_ast(ast))


class Infix(Base, AST):
    lhs: Expr
    rhs: Expr
    op: op.Binary


class Prefix(Base, AST):
    rhs: Expr
    op: op.Unary


class Postfix(Base, AST):
    lhs: Expr
    op: op.Unary


class Call(Base, AST):
    function: Expr
    argument: tuple[Item, ...]

    def __str__(self) -> str:
        return f"{str(self.function)}({', '.join(map(str, self.argument))})"


class Method(Base, AST):
    self: Expr
    method: Id
    argument: tuple[Item, ...]


class Index(Base, AST):
    expr: Expr
    index: tuple[Item, ...]


class GetAttr(Base, AST):
    expr: Expr
    attr: Id


class Member(Base, AST):
    expr: Expr
    field: Id


class Range(Base, AST):
    start: Expr
    end: Expr


class Pair(Base, AST):
    key: str
    value: Expr


class Spread(Base, AST):
    expr: Expr


type Expr = Value | Id | Infix | Prefix | Postfix
type Item = Expr | Pair | Spread


def _ast_builder_method[T](cls: type[T], *args, **kwargs) -> Callable[[], T]:
    return lambda _, children: cls(**dict(zip(args, children)), **kwargs)


class Parser:
    GRAMMAR_PATH: Path = Path(__file__).parent / "grammar"
    GRAMMAR_IMPORT_PATHS: Path = [GRAMMAR_PATH]

    class SyntaxTreeBuilder(lark.Transformer):
        """Builds a syntax tree from a Lark parse tree."""

        # identifiers
        def id(self, children) -> Id:
            return Id.from_ast(children[0])

        # literals
        def nat(self, children) -> Lit[int]:
            return Lit.from_ast(children[0], as_type=int)

        # containers
        def tuple(self, children) -> tuple[Item, ...]:
            return tuple(children)

        # items
        pair = Pair.builder()
        spread = Spread.builder()

        # primary expressions
        field = GetAttr.builder()
        method = Method.builder()
        call = Call.builder()
        index = Index.builder()

        # expressions
        range = Range.builder()

        # operators
        add = Infix.builder(op=op.ADD)
        sub = Infix.builder(op=op.SUB)
        mul = Infix.builder(op=op.MUL)
        div = Infix.builder(op=op.DIV)
        mod = Infix.builder(op=op.MOD)
        pow = Infix.builder(op=op.POW)
        bitwise_and = Infix.builder(op=op.BITWISE_AND)
        bitwise_or = Infix.builder(op=op.BITWISE_OR)
        bitwise_xor = Infix.builder(op=op.BITWISE_XOR)
        bitwise_lshift = Infix.builder(op=op.BITWISE_LSHIFT)
        bitwise_rshift = Infix.builder(op=op.BITWISE_RSHIFT)

        bitwise_not = Prefix.builder(op=op.BITWISE_NOT)
        neg = Prefix.builder(op=op.NEG)
        not_ = Prefix.builder(op=op.NOT)

    def __init__(self):
        with (self.GRAMMAR_PATH / "axis.lark").open() as grammar_file:
            self.lark = lark.Lark(
                grammar_file,
                start="expr",
                strict=True,
                parser="lalr",
                propagate_positions=True,
                transformer=self.SyntaxTreeBuilder(),
                import_paths=[str(path) for path in self.GRAMMAR_IMPORT_PATHS],
            )

    def expr(self, text: str) -> Expr:
        return self.lark.parse(text, start="expr")
