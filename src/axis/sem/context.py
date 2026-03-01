from __future__ import annotations

from protobase import flux

from axis import syn

from .entity import Entity
from .realm import Realm
from .scope import Scope


class Context(syn.SegregatedItem, abstract=True):
    realm: Realm | None = None

    @flux.property
    def scope(self) -> Scope:
        raise NotImplementedError

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        raise NotImplementedError
