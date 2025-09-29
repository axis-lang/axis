from typing import Self
from axis import syn
from .sym import Sym
from .tuple import Tuple

class Apply(syn.Expr, frozen=True):
    function: syn.Expr
    argument: syn.Expr

    @classmethod
    def build(cls, function: syn.Expr, argument: syn.Expr) -> Self:
        return cls(function=function, argument=argument)

# @syn.AstBuilder.build.register
# def build_apply(
#     self,
#     ctx: syn.AxisParser.CallContext,
#     function: syn.Expr,
#     argument: syn.Expr,
# ):
#     return Apply(function, argument)

# @syn.UnifierExprTransformer.transform.register(Apply)
# def visit_apply(self: syn.UnifierExprTransformer, apply: Apply):
#     apply = super(syn.UnifierExprTransformer, self).transform(apply)
#     fn = apply.function
#     if not isinstance(fn, Sym) or not self.is_varname(fn.name):
#         return apply
#     arg = apply.argument
#     if not isinstance(arg, Tuple):
#         raise TypeError(f"Expected a tuple, got {type(arg)}")
#     if len(arg) != 1:
#         raise TypeError(f"Expected a single argument, got {len(arg)}")
#     elem = arg[0]
#     if elem.bound is not None or elem.key is not None:
#         raise TypeError(f"Expected a siple element, got {elem}")
#     self.add_var(fn.name, elem)
#     return elem
