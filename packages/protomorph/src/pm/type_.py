from __future__ import annotations

from typing import Any, Iterator

from .abstract.contract import Item

import pm
from .foundation import Builtin, Id

Field = Item


class Type[T](Builtin, abstract=True):

    # def __getattribute__(self, name: str):
    #     if name == "make":
    #         return object.__getattribute__(self, "carrier")
    #     return super().__getattribute__(name)

    # ── Classification ────────────────────────────────────────────

    def metatype(self) -> Type:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def make(self, data: T):
        carrier_fact = pm._CARRIER_FACTORIES.get(type(self), None)
        if carrier_fact is None:
            raise NotImplementedError(f"No carrier factory for type {type(self).__name__}")
        return carrier_fact(self, data)

    # def carrier(self, data: T) -> pm.Carrier[T]:
    #     """Create the appropriate carrier for data of this type."""
    #     raise NotImplementedError(
    #         f"carrier() not implemented for {type(self).__name__}"
    #     )

    # ── Structure (defaults: leaf / no children) ──────────────────

    @property
    def arity(self) -> int | None:
        return 0

    def item_at(self, offset: int) -> Item:
        raise IndexError(offset)

    def item(self, id: Id) -> Item:
        raise KeyError(id)

    def items(self) -> Iterator[Item]:
        a = self.arity
        if a is None:
            return
        for i in range(a):
            yield self.item_at(i)

    # ── Foundation protocol ───────────────────────────────────────

    def __len__(self) -> int:
        a = self.arity
        return a if a is not None else 0

    def __iter__(self) -> Iterator:
        for item in self.items():
            yield item.value


class Placeholder(Type):
    """Universal stand-in — can appear as Type, as data, anywhere.

    Behaves as Any: a leaf in traversal, captured/substituted later.
    Identity comes from (context, id) via hash-consing.
    """

    context: Builtin | None
    id: str

    def metatype(self) -> Type:
        return self
        #return pm.Spec.of("std.metas.Placeholder")

    def carrier(self, data) -> pm.LeafCarrier:
        return pm.LeafCarrier(self, data)


def placeholder(id: str, context: Any = None) -> Placeholder:
    return Placeholder(context, id)
