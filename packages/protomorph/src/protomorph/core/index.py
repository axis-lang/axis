from __future__ import annotations

from typing import Any, Sequence

from protobase import frozendict, slot_cached_property

from .foundation import Data, Val, Meta, Omega, OMEGA, ground, Ground
from .. import core


class IndexKeyMeta(Meta[Ground, Meta]):
    @property
    def index_key_meta(self) -> Meta:
        return self.__data__


INDEX_GROUND = ground(IndexKeyMeta)


class Index[K: Data](Meta[IndexKeyMeta, tuple[K, ...]]):

    def wrap(self, data: Data) -> Val:
        if isinstance(data, tuple):
            return core.VaryingSchema(self, data)
        else:
            return core.UniformSchema(self, data)

    @property
    def arity(self) -> int:
        return len(self.__data__)

    @slot_cached_property
    def keys(self) -> tuple[K, ...]:
        return tuple(data for data in self.__data__ if data is not None)

    @slot_cached_property
    def key_offsets(self) -> frozendict[K, int]:
        return frozendict(
            {data: i for i, data in enumerate(self.__data__) if data is not None}
        )

    def __invariants__(self) -> None:
        if len(self.keys) != len(self.key_offsets):
            raise AssertionError(f"Index keys must be unique: {self.__data__!r}")

    def __iter__(self):
        return iter(self.__data__)

    @property
    def key_meta(self) -> Meta:
        return self.__meta__.__data__

    def _offset_of(self, key: K) -> int:
        return self.key_offsets[key]

    def offset_of(self, k: Val[Meta, K]) -> int:
        if k.__meta__ != self.__meta__.index_key_meta:
            raise KeyError(
                f"Key meta {k.__meta__!r} does not match index key meta {self.__meta__.index_key_meta!r}"
            )
        return self._offset_of(k.__data__)

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Val, ...]:
        km = self.key_meta
        return tuple(km.wrap(k) for k in self.__data__)

    def reconstruct(self, children: tuple[Val, ...]) -> Index:
        data = tuple(c.__data__ for c in children)
        return Index(self.__meta__, data)

    def concat(self, other: Index) -> Index:
        if self.__meta__ != other.__meta__:
            raise ValueError(
                f"Cannot concat indices with different key metas: "
                f"{self.key_meta!r} vs {other.key_meta!r}"
            )
        return Index(self.__meta__, self.__data__ + other.__data__)

    @classmethod
    def from_vals(cls, vals: Sequence[Val]) -> Index:
        meta = frozenset(val.__meta__ for val in vals)
        if len(meta) == 1:
            key_meta = next(iter(meta))
            data = tuple(val.__data__ for val in vals)
        else:
            key_meta = core.Union(OMEGA, meta)
            data = tuple(key_meta.inject(val).__data__ for val in vals)
        return cls(IndexKeyMeta(INDEX_GROUND, key_meta), data)
