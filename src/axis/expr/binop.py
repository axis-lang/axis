from enum import Enum
from typing import Union
from axis import syn

class BinOp(syn.Expr):
    class Operator(syn.Node):
        symbol: str

    op: Operator
    lhs: syn.Expr
    rhs: syn.Expr

@syn.AstBuilder.build.register
def build_binop_ast(
    self,
    ctx: Union[
        syn.AxisParser.ProductContext,
        syn.AxisParser.AdditionContext,
        syn.AxisParser.ComparisonContext,
        syn.AxisParser.LogicalContext,
        syn.AxisParser.RangeContext,
    ],
    lhs,
    *vals,
):
    for operator, operand in zip(vals[::2], vals[1::2]):
        lhs = BinOp(
            op=operator,
            lhs=lhs,
            rhs=operand,
        )
    return lhs

@syn.AstBuilder.build.register
def build_binary_operator_ast(
    self,
    ctx: Union[
        syn.AxisParser.LogicalOpContext,
        syn.AxisParser.AdditiveOpContext,
        syn.AxisParser.ProductiveOpContext,
        syn.AxisParser.ComparisonOpContext,
    ],
    symbol: str,
):
    return BinOp.Operator(symbol=symbol)