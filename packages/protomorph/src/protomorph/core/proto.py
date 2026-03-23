from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, NamedTuple, Protocol, runtime_checkable


class Item[K, V](NamedTuple):
    offset: int
    key: K | None
    value: V


@runtime_checkable
class Foundation[T](Protocol):
    def __iter__(self) -> Iterator[T]: ...
    def __len__(self) -> int: ...


@runtime_checkable
class Structural[K, V](Foundation[V], Protocol):
    def items(self) -> Iterable[Item[K, V]]: ...
    def item_at(self, offset: int) -> Item[K, V]: ...
    def item(self, key: K) -> Item[K, V]: ...


@runtime_checkable
class Descriptor[T](Foundation["Descriptor[Any]"], Protocol):
    pass


@runtime_checkable
class StructuralDescriptor[T, K](
    Descriptor[T],
    Structural[K, "Descriptor[Any]"],
    Protocol,
):
    pass


@runtime_checkable
class Carrier[T](Foundation["Carrier[Any]"], Protocol):
    @property
    def descriptor(self) -> Descriptor[T]: ...


@runtime_checkable
class StructuralCarrier[T, K](
    Carrier[T],
    Structural[K, "Carrier[Any]"],
    Protocol,
):
    @property
    def descriptor(self) -> StructuralDescriptor[T, K]: ...


@runtime_checkable
class CarrierDescriptor[T, U](Carrier[T], Descriptor[U], Protocol):
    pass
