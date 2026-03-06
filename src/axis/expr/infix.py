from enum import Enum
from typing import ClassVar
from axis import syn


class Infix(syn.Expr, abstract=True):
    class Op(syn.Node, abstract=True):
        grammar_context_infix: ClassVar[str] = ""

        class Symbol(str, Enum): ...

        symbol: "Symbol"  # type: ignore[override]

        def __str__(self):
            return self.symbol.value

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

    def __str__(self):
        return f"{self.lhs} {self.op} {self.rhs}"

    @classmethod
    def build(cls, lhs: syn.Expr, *ops) -> syn.Expr:

        for operator, operand in zip(ops[::2], ops[1::2]):
            lhs = cls(
                op=operator,
                lhs=lhs,
                rhs=operand,
            )

        return lhs


class Productive(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            MUL = "*"
            DOT = "·"
            DIV = "/"
            MOD = "%"
            POW = "**"

    precedence: ClassVar[int] = 1


class Additive(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            ADD = "+"
            SUB = "-"

    precedence: ClassVar[int] = 2


class Comparison(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            EQ = "=="
            NEQ = "!="
            LT = "<"
            LTE = "<="
            GT = ">"
            GTE = ">="

    precedence: ClassVar[int] = 3


class Logic(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            AND = "&&"
            OR = "||"

    precedence: ClassVar[int] = 4


class Range(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            RANGE_INCL = "..="
            RANGE_EXCL = "..<"

    precedence: ClassVar[int] = 5


class Cast(Infix):
    class Op(Infix.Op):
        class Symbol(Infix.Op.Symbol):
            CAST = "=>"
            COERCE = "->"

    precedence: ClassVar[int] = 6


# class Cast(Infix): Coherce
#     class Op(Infix.Op):
#         class Symbol(Infix.Op.Symbol):
#             RANGE_INCL = "=>"
#             RANGE_EXCL = "->"
#     precedence: ClassVar[int] = 5
