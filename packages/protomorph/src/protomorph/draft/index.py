from __future__ import annotations

from typing import Iterator

from .. import draft as mp
from .foundation import Builtin, Id


class Index[K](Builtin):

    keys: tuple[K, ...]

    def __len__(self) -> int:
        return len(self.keys)

    def __getitem__(self, offset: int) -> K:
        return self.keys[offset]

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys)

    def __contains__(self, id: K) -> bool:
        return id in self.keys

    def offset_of(self, id: K) -> int:
        return self.keys.index(id)

    @classmethod
    def make(cls, *keys: K) -> Index[K]:
        return cls(keys)


EMPTY_INDEX: Index = Index(())


class Spread[V](Builtin):
    """Sentinel: wraps a tuple of values to be spliced into a parent Tuple.

    Like Python's *iterable unpacking — the parent Tuple's splice() method
    flattens Spread entries into its own values sequence.
    """

    values: tuple[V, ...]


class Tuple[K, V](Builtin):

    index: Index[K]
    values: tuple[V, ...]

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, key: int | K) -> V:
        if isinstance(key, int):
            return self.values[key]
        return self.values[self.index.offset_of(key)]

    def __iter__(self) -> Iterator[V]:
        return iter(self.values)

    def __contains__(self, value: V) -> bool:
        return value in self.values

    def items(self) -> Iterator[tuple[K, V]]:
        for k, v in zip(self.index, self.values):
            yield k, v

    def splice(self) -> Tuple[K, V]:
        """Flatten any Spread entries in values, expanding them in-place.

        (a, Spread(x, y), b) → (a, x, y, b)
        Index keys for spread positions are dropped; surrounding keys are preserved.
        """
        has_spread = any(isinstance(v, Spread) for v in self.values)
        if not has_spread:
            return self
        new_keys: list[K] = []
        new_values: list[V] = []
        keys = self.index.keys if self.index is not EMPTY_INDEX else (None,) * len(self.values)
        for key, val in zip(keys, self.values):
            if isinstance(val, Spread):
                for sv in val.values:
                    new_values.append(sv)
                    new_keys.append(None)
            else:
                new_values.append(val)
                new_keys.append(key)
        has_keys = any(k is not None for k in new_keys)
        idx = Index(tuple(new_keys)) if has_keys else EMPTY_INDEX
        return type(self)(idx, tuple(new_values))

    @classmethod
    def make[T](cls, *args: T, **kwargs: T) -> Tuple[Id, T]:
        keys = [None] * len(args) + [Id(k) for k in kwargs]
        values = args + tuple(kwargs.values())
        has_keys = any(k is not None for k in keys)
        idx = Index(tuple(keys)) if has_keys else EMPTY_INDEX
        return cls(idx, values)
