from __future__ import annotations

from typing import TYPE_CHECKING

from protobase import flux

from axis import syn

from .realm import Realm
from .scope_binding import ScopeBinding

if TYPE_CHECKING:
    from .database import Database


class Context(syn.SegregatedItem, abstract=True):
    realm: Realm | None = None

    @flux.property
    def scope(self) -> ScopeBinding:
        raise NotImplementedError

    def contribute(self, builder: "Database.Builder") -> None:
        raise NotImplementedError
