from __future__ import annotations

from typing import Any

import protomorph as pm

from axis import log, syn

from .lowering import unsupported_bound, val_type_name
from .sym import Sym

__all__ = ["Member"]

class Member(syn.Expr):
    of: syn.Expr
    name: str

    def __str__(self):
        return f'{self.of}.{self.name}'

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'

    @property
    def match_spec(self) -> syn.MatchSpec:
        if self.is_wildcard:
            return syn.MatchSpec(
                capture_name=self.name[1:],
                filter_any=frozenset({"name"}),
            )
        return syn.MatchSpec()
    
    def as_sym(self):
        return Sym(name=self.name).with_span_of(self)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        of_result = self.of.to_bound(scope)
        if of_result.is_err:
            return of_result
        of_val = of_result.unwrap().fetch()
        if isinstance(of_val, pm.Anchor):
            return pm.Result.ok(pm.val(of_val.child(pm.Id(self.name))))
        report = log.error("Unsupported bound expression").label(
            self,
            f"member access requires an Anchor base, got {val_type_name(of_val)}",
        ).build()
        return pm.Result.err(pm.val(report))

    def to_anchor(self, scope_ref: pm.Anchor | None) -> pm.Anchor:
        return self.of.to_anchor(scope_ref).child(pm.Id(self.name))

    @classmethod
    def build(cls, of: syn.Expr, *members):
        result = of
        for member in members:
            result = cls(of=result, name=member)
        return result
@Member.as_impl(str)
def _as_str(self: Member) -> str:
    return self.name


@Member.as_impl(Sym)
def _as_sym(self: Member) -> Sym:
    return self.as_sym()

# @syn.Reifier.impl(Member)
# def _reify(self: syn.Reifier, mem: Member):    
#     if not mem.is_wildcard:
#         return self.reify_node(mem)
    
#     # tail = self.value(mem.name)
#     # si tail es member, path_prefix tail con self.reify(mem.of)
#     # sino:

#     return mem.with_attr(
#         of=self.reify(mem.of),
#         name=self.value(mem.name, expected_type=Sym).name
#     )


        
