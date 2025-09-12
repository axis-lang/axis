# %%
from __future__ import annotations
from itertools import chain, groupby
from typing import Any, Callable, Self, Sequence, Union, overload
from frozendict import frozendict


class Map[K, V](Record, consed=True):
    _map: frozendict[K, V]

    def __init__(self, map: dict[K, V]):
        super().__init__(frozendict(map))

    def __rich_repr__(self):
        for entry in self.entries:
            yield entry

    def __len__(self):
        return len(self._map)

    def __getitem__(self, item: K) -> V:
        return self._map[item]

    def __setitem__(self, key, val):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item " "assignment"
        )

    def __delitem__(self, key):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item " "deletion"
        )

    def __iter__(self):
        return iter(self.values)

    @property
    def values(self):
        return self._map.values()

    @property
    def keys(self):
        return self._map.keys()

    @property
    def entries(self):
        return self._map.items()

    @classmethod
    def key_offsets_from_entries[
        K
    ](cls, entries: tuple[Tuple.Entry[K, Any]],) -> Map[K, int]:
        index = {}
        for i, (k, _) in enumerate(entries):
            if k is not None:
                if k in index:
                    raise ValueError(f"Duplicate key: {k}")
                index[k] = i
        return cls(index)


class Set[V](Consed):
    _set: frozenset[V]

    def __init__(self, values: Sequence[V]):
        super().__init__(_set=frozenset(values))

    def __getnewargs_ex__(self):
        return (tuple(self._set),), {}

    def __iter__(self):
        return iter(self._set)
    
    def __len__(self):
        return len(self._set)
    
    def __contains__(self, value):
        return value in self._set

    def __rich_repr__(self):
        for value in self._set:
            yield None, value


class Tuple[K, V](Consed):
    type Entry[K, V] = tuple[K | None, V]

    entries: tuple[Entry[K, V]]
    index: Map[K, int]
    # max_positional_offset: int

    @cached_property
    def min_nominal_offset(self):
        return min(self.index)

    @property
    def max_positional_offset(self):
        return len(self.entries)

    @cached_property
    def key_offsets(self):
        return Tuple(self.index.entries)

    @property
    def keys(self):
        return Tuple.from_seq(self.index.keys)

    @cached_property
    def keyset(self):
        return Set(self.index.keys)

    @cached_property
    def values(self):
        return Tuple.from_seq(self)

    class Struct[K](Consed):
        length: int
        index: Map[K, int]

    @property
    def struct(self) -> Struct[K]:
        return self.Struct(len(self), self.index)

    @classmethod
    def of[V](cls, *args: V, **kwargs: V) -> Tuple[str, V]:
        mno = len(args)  # min nominal offset
        entries = [(None, v) for v in chain(args, kwargs.values())]
        for i, k in enumerate(kwargs.keys()):
            p = mno + i
            entries[p] = (k, entries[p][1])
        return cls(entries)

    @classmethod
    def from_seq[V](cls, seq: Sequence[V]) -> Tuple[None, V]:
        return cls((None, v) for v in seq)

    @classmethod
    def from_dict(cls, dct: dict[K, V]) -> Tuple[K, V]:
        return cls(dct.items())

    def __init__(
        self,
        entries: Sequence[Entry[K, V]] = (),
        # *,
        # index: Optional[Map[K, int]] = None,
    ):
        entries = tuple(entries)
        index = Map.key_offsets_from_entries(entries)
        super().__init__(
            entries=entries,
            index=index,
            # max_positional_offset=len(entries),
        )

    def __getnewargs_ex__(self):
        return self.entries, {}

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return (v for _, v in self.entries)

    def __rich_repr__(self):
        return self.entries

    @overload
    def __getitem__(self, index: int) -> V: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    @overload
    def __getitem__[L](self, index: Tuple[L, K]) -> Self: ...

    @overload
    def __getitem__(self, index: K) -> V: ...

    def __getitem__(self, index: Union[int, K, slice]) -> V | Self:
        if isinstance(index, int):
            if index < 0:
                index = len(self) + index
            if index < 0 or index > self.max_positional_offset:
                raise IndexError
            return self.entries[index][1]
        elif isinstance(index, slice):
            return type(self)(self.entries[index])
        else:
            return self.entries[self.index[index]][1]

    # Definir, indexar un tuple con un tuple da un tuple con la estructura del primero

    def map[R](self, fn: Callable[[V], R]) -> Self[K, R]:
        return type(self)((k, fn(v)) for k, v in self.entries)

    def filter(self, fn: Callable[[V], bool]) -> Self:
        return type(self)((k, v) for k, v in self.entries if fn(v))

    def split(self, fn: Callable[[V], bool]) -> tuple[Tuple[K, V], Tuple[K, V]]:
        true, false = [], []
        for k, v in self.entries:
            if fn(v):
                true.append((k, v))
            else:
                false.append((k, v))

        return type(self)(true), type(self)(false)


    def restruct(self, struct: Struct, strict: bool = False) -> tuple[V]:
        """
        Reestructura el tuple segun la estructura dada, si strict=True, se
        lanzara un error si la estructura no es compatible.

        Todas las claves de la estructura deben estar presentes en el tuple.

        La reestructuracion se efectua de forma nominal y posicional.

        

    
        
        """
        if strict and len(self) != struct.length:
            raise ValueError("Incompatible tuple structure")


if __name__ == "__main__":
    t = Tuple.of(1, 2, z=3)
