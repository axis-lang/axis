from __future__ import annotations

from types import NotImplementedType
from protobase import Consed, flux, _

from axis import dom, expr, syn, sem


class Context[P: syn.OutlineNode](syn.SegregatedItem[P], abstract=True):

    class Binding(Consed, abstract=True):
        sym: expr.Sym = _
        bound: syn.Expr | None = None
        default: syn.Expr | None = None

    class Contribution(Consed, abstract=True):
        anchor: dom.Anchor = _
        origin: syn.Node = _
        ctx: Context = _

    realm: sem.Realm = _

    @flux.property
    def contributions(self) -> frozenset["Context.Contribution"]:
        return frozenset()

    @flux.property
    def scope(self) -> sem.Scope | NotImplementedType:
        raise NotImplementedError
