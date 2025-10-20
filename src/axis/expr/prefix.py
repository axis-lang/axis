from enum import Enum
from typing import ClassVar
from axis import conf, syn


class Prefix(syn.Expr, frozen=True, abstract=True):
    class Op(syn.Node, frozen=True, abstract=True):
        grammar_context_infix: ClassVar[str] = ""

        class Symbol(str, Enum):
            ...

        symbol: Symbol

        @classmethod
        def build(cls, s: str):
            try:
                return cls(symbol=cls.Symbol(s))
            except ValueError:
                raise ValueError(f"Unknown unary operator: {s}")

    op: Op
    rhs: syn.Expr

    @classmethod
    def build(cls, op: Op, rhs: syn.Expr):
        return cls(op=op, rhs=rhs)


class Etc(Prefix, frozen=True):
    class Op(Prefix.Op, frozen=True):
        class Symbol(Prefix.Op.Symbol):
            ETC = ".."

        symbol: Symbol

class Sign(Prefix, frozen=True):
    class Op(Prefix.Op, frozen=True):
        class Symbol(Prefix.Op.Symbol):
            POS = "+"
            NEG = "-"
            NOT = "!"
            INV = "~"

        symbol: Symbol
