
from typing import ClassVar, Optional
from axis.core import syn


class Use(syn.Item):
    """
    Represents a 'use' entity:
    use x
    """

    keyword: ClassVar[str] = "use"
    grammar: ClassVar[str] = "use: 'use' expression EOF;"

    expr: syn.Expr
    bound: Optional[syn.Expr]
    value: Optional[syn.Expr]


@syn.AstBuilder.build.register(syn.AxisParser.UseItemContext)
def build_use_ast(
    self,
    _,
    expr: syn.Expr,
    *more,
    children: tuple[syn.Block],
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

    return Use(expr=expr, bound=bound, value=value, children=children)
