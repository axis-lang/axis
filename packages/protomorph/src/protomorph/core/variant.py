from __future__ import annotations

from typing import Any, ClassVar, cast

from protobase import frozendict

from . import display
from .foundation import Discriminant, Data, Val, Meta, Ground, ground


type UnionGround = Ground


class Union(Meta[Ground, frozenset[Meta]], abstract=True):
    Ground: ClassVar[Ground]

    def wrap(self, data: Data) -> Variant:
        assert isinstance(data, frozendict), (
            f"Union data must be a frozendict of active variant data, got {data!r}"
        )
        return Variant(self, cast(frozendict[Discriminant, Data], data))


    @property
    def variants(self) -> frozenset[Meta]:
        return self.__data__

    def __repr__(self):
        return display.repr_union(self)

    def __invariants__(self):
        assert len(self.variants) > 1, "Union must have at least two variants"

    @staticmethod
    def of(*metas: Meta) -> Union:
        return Union(Union.Ground, frozenset(metas))

    def contains(self, meta: Meta) -> bool:
        return meta in self.variants


    def inject(self, val: Val) -> Variant:
        if val.__meta__ not in self.variants:
            raise ValueError(
                f"Value meta {val.__meta__!r} is not a variant of this union: {self.variants!r}"
            )
        return Variant(self, frozendict({val.__meta__: val.__data__}))

Union.Ground = ground(Union)

class Variant[T: Data](Val[Union, frozendict[Discriminant, T]]):
    def __repr__(self) -> str:
        return display.repr_variant(self)

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
