from enum import Enum
from token import ELLIPSIS
from typing import Optional
from protobase import Metadata, Object, Record

from .abstract import Node

class Location(Metadata):
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"


class Statement(Node): ...


class Expr(Statement): ...


class Suite(Node):
    statements: list[Node]


class Id(Expr):
    symbol: str


class MemberAccess(Expr):
    of: Node
    member: list[str]


class BinaryOperation(Expr):
    class Operator(str, Enum):
        ADD = "+"
        SUB = "-"
        MUL = "*"
        DIV = "/"
        MOD = "%"
        EQ = "=="
        NE = "!="
        LT = "<"
        LE = "<="
        GT = ">"
        GE = ">="
        AND = "&&"
        OR = "||"

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

    op: Operator
    lhs: Expr
    rhs: Expr


class MonaryOperation(Expr):
    class Operator(str, Enum):
        NEG = "-"
        NOT = "!"
        INV = "~"

    op: Operator
    val: Expr


class Call(Expr):
    function: Expr
    argument: Optional[Expr]
    trailing: Optional[Expr]


class Compound(Expr):
    elements: tuple[Expr, ...]

class Special(Expr):
    class Type(str, Enum):
        PLACEHOLDER = "_"
        ELLIPSIS = ".."

class Suite(Expr):
    statements: tuple[Statement, ...]


class Tuple(Expr):

    class Element(Node):
        key: Optional[Expr]
        bound: Optional[Expr]
        value: Optional[Expr]

    elements: tuple[Element]
