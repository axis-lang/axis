from enum import Enum
from typing import ClassVar
from axis import conf, syn


class Prefix(syn.Expr, abstract=True):
    class Op(syn.Node, abstract=True):
        grammar_context_infix: ClassVar[str] = ""

        class Symbol(str, Enum):
            ...

        symbol: "Symbol"  # type: ignore[override]

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


class Etc(Prefix):
    class Op(Prefix.Op):
        class Symbol(Prefix.Op.Symbol):
            ETC = ".."

        symbol: "Symbol"  # type: ignore[override]

class Sign(Prefix):
    class Op(Prefix.Op):
        class Symbol(Prefix.Op.Symbol):
            POS = "+"
            NEG = "-"
            NOT = "!"
            INV = "~"

        symbol: "Symbol"  # type: ignore[override]
