from __future__ import annotations

from protobase import Consed, flux

from .database import Database
from .entity import Entity


class Realm(Consed, abstract=True):
    @property
    def contexts(self) -> tuple[Entity.Context, ...]:
        raise NotImplementedError

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset(
            contribution for ctx in self.contexts for contribution in ctx.contributions
        )

    # @flux.property
    # def contributions_by_ref(self) -> frozendict[dom.Ref, frozensetEntity.Contribution]:
    #     return frozenset(
    #         contribution for ctx in self.contexts for contribution in ctx.contributions
    #     )
    


    @flux.property
    def database(self) -> Database:
        contributions: list[Entity.Contribution] = []
        for ctx in self.contexts:
            contributions.extend(ctx.contributions)
        return Database.from_contributions(contributions)
