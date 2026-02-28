from __future__ import annotations

from typing import TYPE_CHECKING

from protobase import Consed, flux

from .database import Database

if TYPE_CHECKING:
    from .context import Context


class Realm(Consed, abstract=True):
    __slots__ = ("__weakref__",)

    @property
    def contexts(self) -> tuple["Context", ...]:
        raise NotImplementedError

    @flux.property
    def database(self) -> Database:
        contributions: list[Database.Contribution] = []
        for ctx in self.contexts:
            contributions.extend(ctx.contributions)
        return Database.from_contributions(contributions)
