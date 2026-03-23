from __future__ import annotations

from typing import Any, Self, Iterator, NamedTuple

from .. import draft as mp
from .foundation import Builtin, Id


class Field(NamedTuple):
    offset: int
    key: Id | None
    type: mp.Type


class Type[T](Builtin, abstract=True):

    # ── Classification ────────────────────────────────────────────

    def metatype(self) -> Type[Self]:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def carrier(self, data: T) -> mp.Carrier[T]:
        """Create the appropriate carrier for data of this type."""
        raise NotImplementedError(
            f"carrier() not implemented for {type(self).__name__}"
        )

    # ── Structure (defaults: leaf / no children) ──────────────────

    @property
    def arity(self) -> int | None:
        return 0

    def field_at(self, offset: int) -> Field:
        raise IndexError(offset)

    def field(self, id: Id) -> Field:
        raise KeyError(id)

    def iter_fields(self) -> Iterator[Field]:
        a = self.arity
        if a is None:
            return
        for i in range(a):
            yield self.field_at(i)


class Omega(Type["Omega"]):
    """OMEGA.metatype() is OMEGA — terminates the meta chain."""

    def metatype(self) -> Omega:
        return OMEGA

    def carrier(self, data) -> mp.LeafCarrier:
        return mp.LeafCarrier(self, data)


OMEGA = Omega()


class Placeholder(Type):
    """Universal stand-in — can appear as Type, as data, anywhere.

    Behaves as Any: a leaf in traversal, captured/substituted later.
    Identity comes from (context, id) via hash-consing.
    """

    context: Builtin | None
    id: str

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> mp.LeafCarrier:
        return mp.LeafCarrier(self, data)


def placeholder(id: str, context: Any = None) -> Placeholder:
    return Placeholder(context, id)
