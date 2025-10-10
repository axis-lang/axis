# %%
from __future__ import annotations

from typing import Iterable, Iterator, Self

from protobase import Record, frozendict

from .map import Map


class Index[K](Record, frozen=True, consed=True):
    """
    Un indice relaciona univocamente una clave con una posicion (y viceversa).
    cuando un indice es denso, todas las posiciones tienen una clave asociada.

    un Index[tuple[K, ...]] seria un indice aplanado de una estructura anidada de tuples.
    donde una clave podria retornar un slice en vez de un unico offset.

    """

    _length: int  # Natural
    _keys: Map[K, int]  # frozendict[int, K] # Map[Natural] K
    _offsets: Map[int, K]  # frozendict[K, int] # Map[K] Natural

    @classmethod
    def from_iter(cls, seq: Iterable[K | None]) -> Self:
        length, keys, offsets = 0, {}, {}

        for i, key in enumerate(seq):
            length += 1
            if key is None:
                continue
            if key in offsets:
                raise ValueError(f"Duplicate key: {key}")
            keys[i] = key
            offsets[key] = i

        return cls(
            _length=length,
            _keys=Map(frozendict(keys)),
            _offsets=Map(frozendict(offsets)),
        )

    @property
    def is_dense(self) -> bool:
        return len(self._keys) == self._length

    @property
    def is_sparse(self) -> bool:
        return not self.is_dense

    @property
    def is_empty(self) -> bool:
        return len(self._keys) == 0

    # @property
    # def empty(self):
    #     return Index(_length=self._length, _keys)


    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> Iterator[K | None]:
        for i in range(self._length):
            yield self._keys.get(i, default=None)

    def __getitem__(self, offset: int) -> K | None:
        if offset < 0 or offset >= self._length:
            raise IndexError(f"Out of range: {offset}")
        return self._keys.get(offset, default=None)

    # @overload
    # def get(self, key: K) -> V: ...

    # @overload
    # def get[D](self, key: K, *, default: D) -> V | D: ...

    # @overload
    # def get[D](self, key: K, *, fallback: Callable[[], D]) -> V | D: ...


    # def get(self, key: K) -> int:
    #     idx = self._offsets.get(key, None)
    #     if idx is None:
    #         raise KeyError(f"Key not found: {key}")
    #     return idx
    @property
    def get(self):
        return self._offsets.get

    @property
    def has(self):
        return self._offsets.has