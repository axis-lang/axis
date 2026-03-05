from __future__ import annotations

from typing import ClassVar, Optional

from protobase import flux

from axis import dom, expr, syn
from axis.sem import Entity

from .base import Def, unify_args_takes, unify_spec_where


class ClassDef(Def):
    """
    Class-like definitions. Always emits OverloadContribution.
    """

    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
        syn.Expr.from_str("$sym[..$spec]"),
        syn.Expr.from_str("$sym(..args)"),
        syn.Expr.from_str("$sym[..$spec](..args)"),
    )

    sym: expr.Sym | None = None
    spec: Optional[expr.Tuple] = None
    args: Optional[expr.Tuple] = None

    def __invariants__(self):
        assert len(self.returns) == 0, "ClassDef cannot have returns"

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        if self.origin is None:
            return frozenset()

        anchor = expr.to_anchor_ref(self.origin, self.anchor)
        if anchor is None:
            return frozenset()

        contributions: list[Entity.Contribution] = []
        if self.anchor is not None:
            contributions.append(
                Entity.Member(
                    anchor=self.anchor,
                    name=expr.to_name(self.origin),
                    target=anchor,
                    origin=self.origin,
                    ctx=self,
                )
            )

        spec_struct = unify_spec_where(self.spec, self.where)

        if self.takes:
            for takes in self.takes:
                params_struct = unify_args_takes(self.args, takes)
                contributions.append(
                    Entity.OverloadContribution(
                        anchor=anchor,
                        spec=spec_struct,
                        params=params_struct,
                        origin=takes,
                        ctx=self,
                    )
                )
        else:
            params_struct = unify_args_takes(self.args, None)
            contributions.append(
                Entity.OverloadContribution(
                    anchor=anchor,
                    spec=spec_struct,
                    params=params_struct,
                    origin=self.origin,
                    ctx=self,
                )
            )

        return frozenset(contributions)
