from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
import weakref
from typing import cast


_MISSING = object()


class WeakKeyIdDictionary[K: object, V: object]:
    """Map values to objects by identity with weak keys."""

    __slots__ = ("_data", "__weakref__")

    def __init__(
        self,
        items: Iterable[tuple[K, V]] | Mapping[K, V] | None = None,
    ) -> None:
        self._data: dict[int, tuple[weakref.ref[K], V]] = {}
        if items is not None:
            self.update(items)

    def _remove_if_match(self, key_id: int, ref: weakref.ref[K]) -> None:
        current = self._data.get(key_id)
        if current is None:
            return
        if current[0] is ref:
            del self._data[key_id]

    def _make_ref(self, key: K, key_id: int) -> weakref.ref[K]:
        selfref = weakref.ref(self)

        def _remove(ref: weakref.ref[K], key_id=key_id, selfref=selfref) -> None:
            self_obj = selfref()
            if self_obj is not None:
                self_obj._remove_if_match(key_id, ref)

        return weakref.ref(key, _remove)

    def _lookup(self, key: K) -> tuple[weakref.ref[K], V] | None:
        key_id = id(key)
        entry = self._data.get(key_id)
        if entry is None:
            return None
        ref, value = entry
        obj = ref()
        if obj is None or obj is not key:
            if self._data.get(key_id) is entry:
                del self._data[key_id]
            return None
        return entry

    def __setitem__(self, key: K, value: V) -> None:
        key_id = id(key)
        ref = self._make_ref(key, key_id)
        self._data[key_id] = (ref, value)

    def __getitem__(self, key: K) -> V:
        entry = self._lookup(key)
        if entry is None:
            raise KeyError(key)
        return entry[1]

    def __contains__(self, key: object) -> bool:
        try:
            return self._lookup(key) is not None  # type: ignore[arg-type]
        except TypeError:
            return False

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: K, default: V | None = None) -> V | None:
        entry = self._lookup(key)
        if entry is None:
            return default
        return entry[1]

    def pop(self, key: K, default=_MISSING) -> V:
        entry = self._lookup(key)
        if entry is None:
            if default is _MISSING:
                raise KeyError(key)
            return cast(V, default)
        del self._data[id(key)]
        return entry[1]

    def clear(self) -> None:
        self._data.clear()

    def items(self) -> Iterator[tuple[K, V]]:
        for key_id, (ref, value) in list(self._data.items()):
            obj = ref()
            if obj is None:
                current = self._data.get(key_id)
                if current is not None and current[0] is ref:
                    del self._data[key_id]
                continue
            yield obj, value

    def keys(self) -> Iterator[K]:
        for key, _ in self.items():
            yield key

    def values(self) -> Iterator[V]:
        for _, value in self.items():
            yield value

    def update(self, items: Iterable[tuple[K, V]] | Mapping[K, V]) -> None:
        if hasattr(items, "items"):
            iterable: Iterable[tuple[K, V]] = items.items()  # type: ignore[assignment]
        else:
            iterable = cast(Iterable[tuple[K, V]], items)
        for key, value in iterable:
            self[key] = value

    def __iter__(self) -> Iterator[K]:
        return self.keys()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} at {id(self):#x}>"


__all__ = ["WeakKeyIdDictionary"]
