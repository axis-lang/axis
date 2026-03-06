from __future__ import annotations

from typing import ClassVar, Optional, cast

from itertools import product
from protobase import flux, slot_cached_property, _

from axis import dom, expr, syn
from axis.sem import Entity

from .base import SymDef, unify_args_takes, unify_spec_where


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
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset(
            Entity.OverloadContribution(
                anchor=self.anchor,
                spec=unify_spec_where(self.spec, where),
                params=unify_args_takes(self.args, takes),
                origin=self.origin, #takes or where or returns,
                ctx=self, # build scope here!
            )
            for where, takes in product(
                self.where or (None,),
                self.takes or (None,),
                #self.returns or (None,),
            )
        )