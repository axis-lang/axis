from __future__ import annotations

from typing import Iterator, ClassVar, Any, cast, Self

from .abstract.contract import Item

from .foundation import Builtin, Id


class Index[K](Builtin):
    Empty: ClassVar[Index[Any]]  # type: ignore[assignment]

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
    def of(cls, *keys: K) -> Index[K]:
        return cls(keys)

class Spread[V](Builtin):
    """Sentinel: wraps a tuple of values to be spliced into a parent Tuple.

    Like Python's *iterable unpacking — the parent Tuple's splice() method
    flattens Spread entries into its own values sequence.
    """

    values: tuple[V, ...]


class Tuple[K, V](Builtin):
    Empty: ClassVar[Tuple[Any, Any]]  # type: ignore[assignment]

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

    # ── Structural protocol ───────────────────────────────────────

    def item_at(self, offset: int) -> Item[K, V]:
        key = self.index[offset] if self.index is not Index.Empty else None
        return Item(offset, key, self.values[offset])

    def item(self, id: K) -> Item[K, V]:
        offset = self.index.offset_of(id)
        return Item(offset, id, self.values[offset])

    def items(self) -> Iterator[Item[K, V]]:
        keys = self.index.keys if self.index is not Index.Empty else (None,) * len(self.values)
        for i, (k, v) in enumerate(zip(keys, self.values)):
            yield Item(i, k, v)

    # ── Head / Tail ───────────────────────────────────────────────

    @property
    def head(self) -> V:
        return self.values[0]

    @property
    def tail(self) -> Tuple[K, V]:
        if len(self.values) <= 1:
            return Tuple.Empty
        new_values = self.values[1:]
        if self.index is not Index.Empty:
            new_keys = self.index.keys[1:]
            has_keys = any(k is not None for k in new_keys)
            new_idx = Index(new_keys) if has_keys else Index.Empty
        else:
            new_idx = Index.Empty
        return type(self)(new_idx, new_values)

    def splice(self) -> Tuple[K, V]:
        """Flatten any Spread entries in values, expanding them in-place.

        (a, Spread(x, y), b) → (a, x, y, b)
        Index keys for spread positions are dropped; surrounding keys are preserved.
        """
        has_spread = any(isinstance(v, Spread) for v in self.values)
        if not has_spread:
            return self
        new_keys: list[K | None] = []
        new_values: list[V] = []
        keys: tuple[K | None, ...] = (
            cast(tuple[K | None, ...], self.index.keys)
            if self.index is not Index.Empty
            else (None,) * len(self.values)
        )
        for key, val in zip(keys, self.values):
            if isinstance(val, Spread):
                for sv in val.values:
                    new_values.append(sv)
                    new_keys.append(None)
            else:
                new_values.append(val)
                new_keys.append(key)
        has_keys = any(k is not None for k in new_keys)
        idx = Index(tuple(new_keys)) if has_keys else Index.Empty
        return type(self)(cast(Index[K], idx), tuple(new_values))

    @classmethod
    def of[T](cls, *args: T, **kwargs: T) -> Self:
        keys: list[Id | None] = [None] * len(args) + [Id(k) for k in kwargs]
        values = args + tuple(kwargs.values())
        has_keys = any(k is not None for k in keys)
        idx = Index(tuple(keys)) if has_keys else Index.Empty
        return cls(cast(Index[K], idx), cast(tuple[V, ...], values))



Index.Empty = Index(())
Tuple.Empty = Tuple(Index.Empty, ())

