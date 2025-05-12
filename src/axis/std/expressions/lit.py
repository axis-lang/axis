from typing import Any
from axis.core import syn

class Lit(syn.Expr):
    value: Any


@syn.AstBuilder.build.register
def build_lit_ast(
    self: syn.AstBuilder,
    ctx: syn.AxisParser.LiteralContext,
    value: Any,
) -> Lit:
    return Lit(value=value)