from decimal import Decimal
from typing import Any
from axis.core import syn

class Lit(syn.Expr):
    value: Decimal | int | str | bool


@syn.AstBuilder.build.register(syn.AxisParser.LitContext)
def build_lit_ast(
    self: syn.AstBuilder,
    ctx: syn.AxisParser.LitContext,
    value: Any,
) -> Lit:
    assert isinstance(value, (Decimal, int, str, bool)), "Invalid literal type"
    return Lit(value=value)