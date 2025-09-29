from decimal import Decimal
from typing import Any, Self
from axis import syn

class Lit(syn.Expr, frozen=True):
    type Value = Decimal | int | str | bool
    value: Value

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)


# @syn.AstBuilder.build.register(syn.AxisParser.LitContext)
# def build_lit_ast(
#     self: syn.AstBuilder,
#     ctx: syn.AxisParser.LitContext,
#     value: Any,
# ) -> Lit:
#     assert isinstance(value, (Decimal, int, str, bool)), "Invalid literal type"
#     return Lit(value=value)