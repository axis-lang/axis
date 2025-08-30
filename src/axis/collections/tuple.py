from __future__ import annotations
from typing import Callable, Iterator, NamedTuple, Optional
from protobase import Record, cached_property, frozendict


class Tuple[V, K=str](Record, consed=True):
    
    class Index[K=str](Record, consed=True):
        # keys: tuple[Optional[K], ...]

        # @property
        # def offset_by_key(self) -> frozendict[K, int]:
        #     return {k: i for i, k in enumerate(self.keys) if k is not None}
        
        def key_by_offset(self, offset: int) -> Optional[K]:
            if 0 <= offset < len(self.keys):
                return self.keys[offset]
            raise IndexError(f"Offset {offset} is out of bounds for Index with length {len(self.keys)}.")

    class Entry[V, K=str](NamedTuple):
        key: Optional[K]
        value: V

    index: Index[K]
    values: tuple[V, ...]

    # def __init__(self, entries: Entry):
    #     ...

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, offset: int) -> V:
        return self.values[offset]
    
    def __iter__(self) -> Iterator[V]:
        return iter(self.values)

    def at(self, offset: int) -> Entry[V, K]:
        return self.Entry(
            key=self.index.key_by_offset(offset),
            value=self.values[offset]
        )

    def get(self, key: K) -> V:
        offset = self.index.offset_by_key.get(key)
        if offset is None:
            raise KeyError(f"Key '{key}' not found in Tuple.")
        return self.values[offset]
    
    #def map[T](self, func: Callable[[V, Optional[K]], T]) -> Tuple[T, K]:



