from typing import Self
from axis import syn
from .sym import Sym
from .tuple import Tuple

class Apply(syn.Expr):
    function: syn.Expr
    argument: Tuple

    @classmethod
    def build(cls, function: syn.Expr, argument: Tuple) -> Self:
        assert isinstance(argument, Tuple)
        return cls(function=function, argument=argument)
