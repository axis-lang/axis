from __future__ import annotations

from typing import Any
from protobase import frozendict
from .foundation import Discriminant, Data, Val, Meta, Omega, OMEGA
from .. import core

type UnionGround = core.Omega | core.Ground


class Union(Meta[UnionGround, frozenset[Meta]], abstract=True):
    @property
    def variants(self) -> frozenset[Meta]:
        return self.__data__

    def __repr__(self):
        return " | ".join(repr(v) for v in self.variants)

    def __invariants__(self):
        assert len(self.variants) > 1, "Union must have at least two variants"

    @classmethod
    def of(cls, *metas: Meta) -> Union:
        return cls(OMEGA, frozenset(metas))

    def contains(self, meta: Meta) -> bool:
        return meta in self.variants

    def wrap(self, data: Data) -> Variant:
        return Variant(self, data)

    def inject(self, val: Val) -> Variant:
        if val.__meta__ not in self.variants:
            raise ValueError(
                f"Value meta {val.__meta__!r} is not a variant of this union: {self.variants!r}"
            )
        return Variant(self, frozendict({val.__meta__: val.__data__}))


class Variant[T: Data](Val[Union, frozendict[Discriminant, T]]):
    def is_(self, meta: Meta) -> bool:
        return meta in self.__data__

    @property
    def active(self) -> Val:
        ((meta, data),) = self.__data__.items()
        return meta.wrap(data)

    @property
    def discriminant(self) -> Meta:
        (meta,) = self.__data__.keys()
        return meta

    def project(self, meta: Meta) -> Val | None:
        if meta in self.__data__:
            return meta.wrap(self.__data__[meta])
        return None

    def map_active(self, f) -> Variant:
        new_val = f(self.active)
        return self.__meta__.inject(new_val)

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Val, ...]:
        return (self.active,)

    def reconstruct(self, children: tuple[Val, ...]) -> Variant:
        (child,) = children
        return self.__meta__.inject(child)

    def __invariants__(self) -> None:
        assert (
            len(self.__data__) == 1
        ), f"Variant must have exactly one active meta: {self.__data__!r}"
        assert all(
            act in self.__meta__.variants for act in self.__data__.keys()
        ), f"Variant meta {self.__meta__!r} must include active meta: {self.__data__.keys()!r}"


