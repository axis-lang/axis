# %%
from __future__ import annotations

from typing import Callable, Iterable, Iterator, Optional, Self, overload

from protobase import Record, frozendict



class Map[V, K](Record, frozen=True, consed=True):
    _inner: frozendict[K, V]

    @classmethod
    def from_iter(cls, seq: Iterable[tuple[K, V]]) -> Self:
        return cls(
            _inner=frozendict((k, v) for k, v in seq)
        )

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
            if 'default' in kwargs:
                return kwargs['default']
            if 'fallback' in kwargs:
                return kwargs['fallback']()
            raise

    def has(self, key: K) -> bool:
        return key in self._inner

    def map[R](self, func: Callable[[V], R]) -> Map[R, K]:
        return Map(_inner=frozendict((k, func(v)) for k, v in self._inner.items()))
