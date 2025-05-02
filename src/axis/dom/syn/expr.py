from decimal import Decimal
from enum import Enum
from functools import singledispatch
from typing import Optional
from protobase import Metadata
from .abstract import Node, Expr
from axis.dom import ref

class Location(Metadata):
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"

class Sym(Expr):
    '''
    Representa un simbolo en el AST que debe ser resuelto semanticamente
    '''
    name: str
    at: Optional[str] = None

class Lit(Expr):
    value: bool | int | Decimal | str


class Tuple(Expr):

    class Element(Node):
        key: Optional[Expr]
        bound: Optional[Expr]
        value: Optional[Expr]

    elements: tuple[Element, ...]


class Member(Expr):
    of: Node
    sym: Sym

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

class Apply(Expr):

    function: Expr
    argument: Optional[Expr]
    trailing: Optional[Expr]

class Index(Expr):
    container: Expr
    indice: Tuple


class Spread(Expr):
    expr: Expr

class Compound(Expr):
    components: tuple[Expr, ...]


