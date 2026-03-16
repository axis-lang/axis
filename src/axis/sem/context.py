from __future__ import annotations

from types import NotImplementedType
from protobase import flux, _
from protobase.cached_property import slot_cached_property
import protomorph as pm

from axis import syn, sem

from .scope import Scope


class Context[P: "Context"](syn.SegregatedItem[P], abstract=True):

    class Contribution(pm.ContextProto, abstract=True):
        anchor: pm.Anchor = _
        origin: syn.Node = _
        ctx: Context = _

        @flux.method
        def check(self):
            pass

    class NamespaceContribution(Contribution):
        pass

    realm: sem.Realm = _

    @flux.property
    def contributions(self) -> frozenset[Contribution]:
        return frozenset()

    @property
    def parent_scope(self) -> Scope | None:
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
    def scope(self) -> Scope | NotImplementedType:
        builder = Scope.Builder(name=self.name, parent=self.parent_scope)
        self._build_scope(builder)
        return builder.build()

    def _build_scope(self, scope_builder: Scope.Builder): ...

    @flux.method
    def check(self):
        self.scope
        pass
