# %%
from __future__ import annotations
from decimal import Decimal
from typing import NamedTuple, Union
from protobase import Record, frozendict, cached_property


class Value(Record, frozen=True, consed=True, abstract=True):
    class Meta(Record, frozen=True, consed=True, abstract=True):
        def as_value(self) -> Value:
            raise NotImplementedError(f"Cannot convert {self} to Value")

        @classmethod
        def value_of(cls, data: Data) -> Value:
            raise NotImplementedError(f"Cannot create Value from data {data}")

    __meta__: Meta
    __data__: Data

    @property
    def meta(self) -> Value:
        return self.__meta__.as_value()


type Data = Union[
    None,
    bool,
    int,
    float,
    Decimal,
    str, 
    bytes,
    tuple[Data, ...],
    frozenset[Data],
    frozendict[Data, Data],
]

class KeyIndex[K: Data = Data](Value, frozen=True):
    'like Map[K] Natural'
    class Meta(Value.Meta, frozen=True):
        key_bound: Value.Meta

    __meta__: Meta
    __data__: tuple[K | None, ...]

    @property
    def keys(self):
        return self.__data__

    @cached_property
    def indices(self) -> frozendict[K, int]:
        return frozendict((k, i) for i, k in enumerate(self.__data__) if k is not None)

    def __len__(self):
        return len(self.__data__)

    def __iter__(self):
        return iter(self.__data__)

    def __contains__(self, key: K) -> bool:
        return key in self.indices

    def __getitem__(self, index: int):
        return self.__data__[index]

    def get(self, key: K) -> int | None:
        return self.indices.get(key, None)


class Tuple[V: Data = Data, K: Data = Data](Value, frozen=True):
    "(..(K|None)=..V)"
    class Meta(Value.Meta, frozen=True):
        key_index: KeyIndex[K]
        bounds: tuple[Value.Meta, ...]

    __meta__: Meta
    __data__: tuple[V, ...]

    def __len__(self):
        return len(self.__data__)

    def __iter__(self):
        return iter(
            bound.value_of(v) for v, bound in zip(self.__data__, self.__meta__.bounds)
        )

    def __getitem__(self, offset: int) -> tuple[K | None, Value]:
        return self.__meta__.key_index[offset], self.__meta__.bounds[offset].value_of(
            self.__data__[offset]
        )

    def get(self, key: K) -> Value | None:
        offset = self.__meta__.key_index.get(key)
        if offset is None:
            return None
        return self.__meta__.bounds[offset].value_of(self.__data__[offset])

 
