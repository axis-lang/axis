from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import ClassVar, Optional

from .abstract import Expr, Node


class Sym(Expr):
    '''
    Representa un simbolo en el AST que debe ser resuelto semanticamente
    '''
    ROOT: ClassVar[Sym]

    name: str
    at: Optional[str] = None

Sym.ROOT = Sym('@root', at='root')

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
    name: str

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
    argument: Tuple
    trailing: Optional[Expr]

class Index(Expr):
    container: Expr
    indice: Tuple


class Spread(Expr):
    expr: Expr

class Compound(Expr):
    components: tuple[Expr, ...]


