# %%
from __future__ import annotations

from typing import Callable, Iterable, Optional, overload

from protobase import Record

from .index import Index


class Tuple[V, K=str](Record, frozen=True, consed=True):
    _key_index: Index[K] # Index[L] K
    _values: tuple[V, ...] # inner representation

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        def repr_element(k, v):
            if k is None:
                return repr(v)
            else:
                return f"{k}={repr(v)}"

        return (
            "("
            + ", ".join(repr_element(k, v) for k, v in zip(self._key_index, self._values))
            + ")"
        )

    @classmethod
    def from_iter(cls, items: Iterable[tuple[K, V]]) -> Tuple[V, K]:
        return cls(
            _key_index=Index.from_iter(k for k, v in items),
            _values=tuple(v for k, v in items),
        )
    
    @classmethod
    def from_dict(cls, d: dict[K, V]) -> Tuple[V, K]:
        return cls.from_iter(d.items())

    def __getitem__(self, offset: int) -> V:
        if offset < 0 or offset >= len(self._values):
            raise IndexError(f"Index out of range: {offset}")
        return self._values[offset]

    @overload
    def get(self, key: K) -> V: ...

    @overload
    def get[D](self, key: K, *, default: D) -> V | D: ...

    @overload
    def get[D](self, key: K, *, fallback: Callable[[], D]) -> V | D: ...

    def get(self, key: K, **kwargs):
        if not self._key_index.has(key):
            if 'default' in kwargs:
                return kwargs['default']
            if 'fallback' in kwargs:
                return kwargs['fallback']()
            raise KeyError(f"Key not found: {key}")
        offset = self._key_index.get(key)
        return self._values[offset]

    def has(self, key: K) -> bool:
        return self._key_index.has(key)
   
    def map[R](self, func: Callable[[V], R]) -> Tuple[R, K]:
        return Tuple(_key_index=self._key_index, _values=tuple(func(v) for v in self._values))

    