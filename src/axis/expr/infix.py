from enum import Enum
from typing import ClassVar, Union
from axis import syn, cfg
from rich.text import Text

class Infix(syn.Expr, frozen=True, abstract=True):
    class Op(syn.Node, frozen=True, abstract=True):
        grammar_context_infix: ClassVar[str] = ""

        class Symbol(str, Enum): ...

        symbol: Symbol

        @classmethod
        def build(cls, s: str):
            try:
                return cls(symbol=cls.Symbol(s))
            except ValueError:
                raise ValueError(f"Unknown binary operator: {s}")

    precedence: ClassVar[int] = 0  # to be overridden in subclasses
    op: Op
    lhs: syn.Expr
    rhs: syn.Expr

    @classmethod
    def build(cls, lhs: syn.Expr, *ops) -> syn.Expr:

        for operator, operand in zip(ops[::2], ops[1::2]):
            lhs = cls(
                op=operator,
                lhs=lhs,
                rhs=operand,
            )

        return lhs

    def __str__(self):
        
        return f"{self.lhs} {self.op.symbol.value} {self.rhs}"
        

class Productive(Infix, frozen=True):
    class Op(Infix.Op, frozen=True):
        class Symbol(Infix.Op.Symbol):
            MUL = "*"
            DOT = "·"
            DIV = "/"
            MOD = "%"
            POW = "**"

        symbol: Symbol

    precedence: ClassVar[int] = 1

class Additive(Infix, frozen=True):
    class Op(Infix.Op, frozen=True):
        class Symbol(Infix.Op.Symbol):
            ADD = "+"
            SUB = "-"

        symbol: Symbol

    precedence: ClassVar[int] = 2

class Comparison(Infix, frozen=True):
    class Op(Infix.Op, frozen=True):
        class Symbol(Infix.Op.Symbol):
            EQ = "=="
            NEQ = "!="
            LT = "<"
            LTE = "<="
            GT = ">"
            GTE = ">="

        symbol: Symbol

    precedence: ClassVar[int] = 3

class Logic(Infix, frozen=True):
    class Op(Infix.Op, frozen=True):
        class Symbol(Infix.Op.Symbol):
            AND = "&&"
            OR = "||"

        symbol: Symbol

    precedence: ClassVar[int] = 4

class Range(Infix, frozen=True):
    class Op(Infix.Op, frozen=True):
        class Symbol(Infix.Op.Symbol):
            RANGE_INCL = "..="
            RANGE_EXCL = "..<"

        symbol: Symbol

    precedence: ClassVar[int] = 5