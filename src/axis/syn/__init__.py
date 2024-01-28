from __future__ import annotations

from pathlib import Path
from typing import Annotated, Callable, Optional

from lark import Lark, Transformer

# from rich import print

from pure import Pure, Tag


GRAMMAR_PATH = Path(__file__).parent / "grammar"


type Value = str | int | float | bool


class Span(Pure):
    """A span of text in a source file."""

    start: int
    end: int

    @classmethod
    def from_ast(cls, ast):
        return cls(ast.start_pos, ast.end_pos)


class Expr(Pure):
    ...


class Lit[T: Value](Expr):
    """A literal value."""

    value: Value
    span: Annotated[Optional[Span], Tag.EXCLUDE_REPR] = None

    @classmethod
    def from_ast(cls, ast, as_type: type[T]):
        return cls(as_type(ast.value), Span.from_ast(ast))

    def __str__(self):
        return str(self.value)


class Id(Expr):
    """An identifier."""

    name: str
    span: Optional[Span] = None

    @classmethod
    def from_ast(cls, ast):
        return cls(ast.value, Span.from_ast(ast))

    def __str__(self):
        return str(self.name)


class Infix(Expr):
    """An infix operator expression."""

    lhs: Annotated[Expr, Tag.POSITIONAL_ONLY]
    rhs: Annotated[Expr, Tag.POSITIONAL_ONLY]

    class Op(Pure):
        """An infix operator."""

        name: Annotated[str, Tag.POSITIONAL_ONLY]
        symbol: Annotated[str, Tag.EXCLUDE_REPR]
        eval: Annotated[Callable[[Value, Value], Value], Tag.EXCLUDE_REPR]

    # logical
    LOGICAL_AND = Op("logical_and", "&&", lambda a, b: a and b)
    LOGICAL_OR = Op("logical_or", "||", lambda a, b: a or b)

    # aithmetic
    ADD = Op("add", "+", lambda a, b: a + b)
    SUB = Op("sub", "-", lambda a, b: a - b)
    MUL = Op("mul", "*", lambda a, b: a * b)
    DIV = Op("div", "/", lambda a, b: a / b)
    MOD = Op("mod", "%", lambda a, b: a % b)
    POW = Op("pow", "**", lambda a, b: a**b)

    # bitwise
    BITWISE_AND = Op("bitwise_and", "&", lambda a, b: a & b)
    BITWISE_OR = Op("bitwise_or", "|", lambda a, b: a | b)
    BITWISE_XOR = Op("bitwise_xor", "^", lambda a, b: a ^ b)
    BITWISE_LSHIFT = Op("bitwise_lshift", "<<", lambda a, b: a << b)
    BITWISE_RSHIFT = Op("bitwise_rshift", ">>", lambda a, b: a >> b)

    op: Annotated[Op, Tag.POSITIONAL_ONLY]

    def __str__(self):
        return f"{self.lhs} {self.op.symbol} {self.rhs}"


class Prefix(Expr):
    """A prefix operator expression."""

    rhs: Annotated[Expr, Tag.POSITIONAL_ONLY]

    class Op(Pure):
        name: Annotated[str, Tag.POSITIONAL_ONLY]
        symbol: Annotated[str, Tag.EXCLUDE_REPR]
        eval: Annotated[Callable[[Value, Value], Value], Tag.EXCLUDE_REPR]

    NOT = Op("not", "!", lambda a: not a)
    NEG = Op("neg", "-", lambda a: -a)
    BITWISE_NOT = Op("bitwise_not", "~", lambda a: ~a)

    op: Annotated[Op, Tag.POSITIONAL_ONLY]

    def __str__(self):
        return f"{self.op.symbol}{self.rhs}"


class Apply(Expr):
    qual: Expr
    next: Expr

    def __str__(self):
        return f"{str(self.qual)} {str(self.next)}"


class Call(Expr):
    function: Expr
    argument: tuple[Item, ...]

    def __str__(self) -> str:
        return f"{str(self.function)}({', '.join(map(str, self.argument))})"


class Method(Expr):
    self: Expr
    method: Id
    argument: tuple[Item, ...]


class Index(Expr):
    expr: Expr
    index: tuple[Item, ...]


class Field(Expr):
    expr: Expr
    field: Id


class Member(Expr):
    expr: Expr
    field: Id


class Range(Expr):
    """A range expression."""

    start: Expr
    end: Expr


class Pair(Pure):
    key: str
    value: Expr


class Spread(Pure):
    expr: Expr


type Item = Expr | Pair | Spread


def _ast_builder_method[T](cls: type[T], **kwargs) -> Callable[[Transformer, list], T]:
    return lambda self, children: cls(*children, **kwargs)


class Parser:
    class SyntaxTreeBuilder(Transformer):
        """Builds a syntax tree from a Lark parse tree."""

        # identifiers
        def id(self, children) -> Id:
            return Id.from_ast(children[0])

        # literals
        def nat(self, children) -> Lit[int]:
            return Lit.from_ast(children[0], as_type=int)

        # items
        pair = _ast_builder_method(Pair)
        spread = _ast_builder_method(Spread)

        # constructions
        tuple = _ast_builder_method(tuple)
        range = _ast_builder_method(Range)

        # primary expressions
        field = _ast_builder_method(Field)
        method = _ast_builder_method(Method)
        call = _ast_builder_method(Call)
        index = _ast_builder_method(Index)

        # operators
        add = _ast_builder_method(Infix, op=Infix.ADD)
        sub = _ast_builder_method(Infix, op=Infix.SUB)
        mul = _ast_builder_method(Infix, op=Infix.MUL)
        div = _ast_builder_method(Infix, op=Infix.DIV)
        mod = _ast_builder_method(Infix, op=Infix.MOD)
        pow = _ast_builder_method(Infix, op=Infix.POW)
        bitwise_and = _ast_builder_method(Infix, op=Infix.BITWISE_AND)
        bitwise_or = _ast_builder_method(Infix, op=Infix.BITWISE_OR)
        bitwise_xor = _ast_builder_method(Infix, op=Infix.BITWISE_XOR)
        bitwise_lshift = _ast_builder_method(Infix, op=Infix.BITWISE_LSHIFT)
        bitwise_rshift = _ast_builder_method(Infix, op=Infix.BITWISE_RSHIFT)
        bitwise_not = _ast_builder_method(Prefix, op=Prefix.BITWISE_NOT)
        neg = _ast_builder_method(Prefix, op=Prefix.NEG)
        not_ = _ast_builder_method(Prefix, op=Prefix.NOT)

    def __init__(self):
        with (GRAMMAR_PATH / "axis.lark").open() as grammar_file:
            self.lark = Lark(
                grammar_file,
                start="expr",
                strict=True,
                parser="lalr",
                propagate_positions=True,
                transformer=self.SyntaxTreeBuilder(),
                import_paths=[str(GRAMMAR_PATH)],
            )

    def expr(self, text: str) -> Expr:
        return self.lark.parse(text, start="expr")
