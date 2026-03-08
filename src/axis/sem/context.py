from __future__ import annotations

from types import NotImplementedType
from protobase import Consed, flux, _
from protobase.cached_property import slot_cached_property

from axis import dom, syn, sem


class Context[P: Context](syn.SegregatedItem[P], abstract=True):

    class Binding(Consed, abstract=True):
        key: syn.Expr = _
        bound: syn.Expr | None = None
        default: syn.Expr | None = None

    class Contribution(dom.ContributionBase, abstract=True):
        origin: syn.Node = _
        ctx: Context = _

        @flux.method
        def check(self):
            pass

    realm: sem.Realm = _

    @flux.property
    def contributions(self) -> frozenset[Contribution]:
        return frozenset()

    @property
    def parent_scope(self) -> sem.Scope | None:
        parent = self.parent
        while parent is not None:
            if parent.scope is not NotImplemented:
                return parent.scope
            parent = parent.parent
        return None

    @slot_cached_property
    def name(self) -> str | None:
        return None

    @flux.property
    def scope(self) -> sem.Scope | NotImplementedType:
        builder = sem.Scope.Builder(name=self.name, parent=self.parent_scope)
        self._build_scope(builder)
        return builder.build()


    def _build_scope(self, scope_builder: sem.Scope.Builder): ...

    @flux.method
    def check(self):
        self.scope
        pass