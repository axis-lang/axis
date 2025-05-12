from typing import ClassVar, Optional
from axis.core import syn

class Val(syn.Item):
    """
    Represents a 'val' item:
    val expr: bound = value
    """

    keyword: ClassVar = "val"
    grammar: ClassVar = "val: 'val' expression ':' expression '=' expression EOF;"


    expr: syn.Expr
    bound: Optional[syn.Expr]
    value: Optional[syn.Expr]

@syn.AstBuilder.build.register
def build_val_ast(
    self, 
    ctx: syn.AxisParser.ValItemContext, 
    expr: syn.Expr, 
    *more
):
    bound = None
    value = None
    for operator, operand in zip(more[::2], more[1::2]):
        if operator == ":":
            bound = operand
        elif operator == "=":
            value = operand
        else:
            raise ValueError(f"Unknown operator {operator}")

    return dict(expr=expr, bound=bound, value=value)
