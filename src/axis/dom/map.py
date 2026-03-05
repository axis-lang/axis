# %%
from __future__ import annotations

from typing import Callable, Iterable, Iterator, Optional, Self, overload

from protobase import Consed, frozendict


__all__ = ["Map"]

class Map[K, V](Consed):
    "def Map[K] V"

    _inner: frozendict[K, V]

    @property
    def keys(self):
        return self._inner.keys()

    @classmethod
    def new(cls, seq: Iterable[tuple[K, V]]) -> Self:
        return cls(frozendict(seq))

    def __len__(self) -> int:
        return len(self._inner)

    def __iter__(self) -> Iterator[V]:
        return iter(self._inner.values())

    @overload
    def get(self, key: K) -> V: ...

    @overload
    def get[D](self, key: K, *, default: D) -> V | D: ...

    @overload
    def get[D](self, key: K, *, fallback: Callable[[], D]) -> V | D: ...

    def get(self, key: K, **kwargs):
        try:
            return self._inner[key]
        except KeyError:
            if "default" in kwargs:
                return kwargs["default"]
            if "fallback" in kwargs:
                return kwargs["fallback"]()
            raise

    def has(self, key: K) -> bool:
        return key in self._inner

    def apply[R](self, fn: Callable[[V], R]) -> Map[K, R]:
        return Map(frozendict((k, fn(v)) for k, v in self._inner.items()))

    
