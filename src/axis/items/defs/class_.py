from __future__ import annotations

from typing import ClassVar, Optional, cast

from itertools import product
from protobase import flux, slot_cached_property, _

from axis import expr, log, syn, sem

from .base import SymDef, build_param_bindings, build_spec_bindings


class ClassDef(SymDef):
    """
    Class-like definitions. Always emits OverloadContribution.
    """

    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
        syn.Expr.from_str("$sym[..$spec]"),
        syn.Expr.from_str("$sym(..$args)"),
        syn.Expr.from_str("$sym[..$spec](..$args)"),
    )

    sym: expr.Sym = _
    spec: expr.Tuple | None = None
    args: expr.Tuple | None = None

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        return frozenset(
            sem.Entity.OverloadContribution(
                anchor=self.anchor,
                spec_bindings=build_spec_bindings(self.spec, where),
                param_bindings=build_param_bindings(self.args, takes),
                origin=self.origin, #takes or where or returns,
                ctx=self, # build scope here!
            )
            for where, takes in product(
                self.where or (None,),
                self.takes or (None,),
                #self.returns or (None,),
            )
        )
    
    def __invariant__(self):
        if len(self.returns) > 0:
            log.warn("ClassDef should not have returns").label(self.origin).emit()
