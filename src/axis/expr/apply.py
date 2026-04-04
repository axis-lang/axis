from __future__ import annotations

from typing import Any, Self

import protomorph as pm

from axis import log, syn

from .lowering import unsupported_bound
from .tuple_ import Tuple

class Apply(syn.Expr):
    function: syn.Expr
    argument: Tuple

    @classmethod
    def build(cls, function: syn.Expr, argument: Tuple) -> Self:
        assert isinstance(argument, Tuple)
        return cls(function=function, argument=argument)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        _ = scope
        return unsupported_bound(
            self,
            "function application cannot be used to construct bounds yet",
        )
