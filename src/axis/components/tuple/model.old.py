# %%
import inspect
from typing import (
    Callable,
    Generic,
    Iterator,
    Optional,
    Self,
    Sequence,
    TypeAlias,
    TypeVar,
)
from protobase import Object, traits, attr

from types import MappingProxyType


class Element[T, K](
    Object,
    traits.Inmutable,
    traits.Hash,
    traits.Eq,
):
    value: T
    key: Optional[K] = None

    @classmethod
    def parse(cls, value: T | tuple[K, T] | Self) -> Self:
        if isinstance(value, Element):
            return value
        if isinstance(value, tuple):
            return cls(value[1], key=value[0])
        return cls(value)

    def __new__(cls, value: T, *, key: Optional[K] = None) -> Self:
        return super().__new__(cls, value=value, key=key)

    def __repr__(self) -> str:
        if self.key is not None:
            return f"{self.key}: {self.value}"
        return repr(self.value)


class KeyIndex[K](Object, traits.Consed):
    __slots__ = ["_dict"]

    # _dict: Annotated[MappingProxyType[T, int], attr.internal]
    _items: tuple[tuple[K, int]]

    @classmethod
    def from_fn_params(cls, fn: Callable):
        fn_params = inspect.signature(fn).parameters.values()
        return cls((param.name, index) for index, param in enumerate(fn_params))

    def __new__(cls, tup: Sequence[tuple[K, int]]):
        _dict = {}
        for key, index in tup:
            if key is None:
                continue
            if key in _dict:
                raise ValueError(f"Duplicate key '{key}'")
            _dict[key] = index

        _items = sorted(_dict.items(), key=lambda x: x[1])

        self = super().__new__(cls, _items=tuple(_items))

        if not hasattr(self, "_dict"):
            attr.set(self, "_dict", MappingProxyType(_dict))

        return self

    def __repr__(self):
        return f"{type(self).__name__}"

    def __iter__(self) -> Iterator[K]:
        return iter(self._dict)

    def __contains__(self, key: K) -> bool:
        return key in self._dict

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> K:
        return self._dict[index]

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()


class Tuple[T](Object, traits.Consed):
    type K = str
    elements: tuple[Element[T, K]]
    key_index: KeyIndex[K]

    def __new__(cls, elements: Sequence[Element[T, K] | T | tuple[K, T]]):
        elements = tuple(map(Element.parse, elements))
        key_index = KeyIndex(
            (elem.key, n) for n, elem in enumerate(elements) if elem.key is not None
        )

        self = super().__new__(
            cls,
            elements=elements,
            key_index=key_index,
        )

        return self

    @classmethod
    def new[T](cls, *values: T, **named_values: T) -> "Tuple[T]":
        return cls((*values, *named_values.items()))

    @classmethod
    def from_dict(cls, dct: dict[K, T]):
        return cls(dct.items())

    def __repr__(self) -> str:
        return f"({', '.join(map(repr, self.elements))})"

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self) -> Iterator[T]:
        return map(lambda e: e.value, self.elements)

    def __getitem__(self, at: slice | int | K) -> Element[T, K]:
        if isinstance(at, str):
            at = self.key_index[at]
        return self.elements[at].value

    def map[V](self, fn: Callable[[T], V]) -> "Self[V]":
        return type(self)(Element(fn(e.value), key=e.key) for e in self.elements)


Tup: TypeAlias = Tuple


if __name__ == "__main__":
    tup = Tup.new(1, 2, 3, x=4, y=5, z=9)
    print(tup)

    print(list(tup.key_index.items()))

    Element(1, key="x")
