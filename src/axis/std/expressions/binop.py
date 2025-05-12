from enum import Enum
from typing import Union
from axis.core import syn

class BinOp(syn.Expr):
    # TODO: operator como syn node tendrá span
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
    lhs: syn.Expr
    rhs: syn.Expr


@syn.AstBuilder.build.register
def build_binop_ast(
    self,
    ctx: Union[
        syn.AxisParser.ProductContext,
        syn.AxisParser.AdditionContext,
        syn.AxisParser.ComparisonExprContext,
        syn.AxisParser.LogicalExprContext,
    ],
    lhs,
    *vals,
):
    for operator, operand in zip(vals[::2], vals[1::2]):
        lhs = BinOp(
            op=BinOp.Operator(operator),
            lhs=lhs,
            rhs=operand,
        )
    return lhs