
from typing import ClassVar, Optional
from axis.core import syn, sem
from axis.std.transcriptions.destructuring import reify_destructure
from axis.std.expressions.sym import Sym

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


@sem.ScopingPass.process_item.register
def process_use(self, use_ast: Use):
    # evaluate use expression
    elements = reify_destructure(use_ast.expr, from_=Sym.ROOT)

    # register symbols
    for elem in elements:
        self.add_symbol(elem.key.name, elem)
