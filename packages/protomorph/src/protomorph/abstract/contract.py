"""
Neutral structural contracts used by protomorph core.

Taxonomy
--------
- Domain: a coherent set of descriptors.
- Encoding: a coherent set of carriers for a domain.
- Implementation: a concrete pairing of a domain and an encoding.
- Capability: a transversal operational helper layered on top of the
  structural contracts, such as lazy, remote, materialized, fetchable,
  async, and similar traits.
The current type-algebra work is expected to become one domain. Different
carrier codifications such as native-object, JSON-like, or remote handles
should then appear as different encodings over that same domain.

Structure
---------
- Foundation[V]: minimal structural sweep through ``__iter__`` and ``__len__``.
- Structural[K, V]: stable structural alignment through ``items()``,
  ``item_at()``, and ``item()``.
- Descriptor[T]: role that describes values of ``T``.
- Carrier[T]: role that navigates values of ``T`` under a descriptor.
- CarrierDescriptor[T, U]: object that is both a carrier of ``T`` and a
  descriptor of ``U``. This is a role intersection, not self-description.

Design notes
------------
- ``iter`` can be defined over ``Foundation``.
- ``deep_zip`` requires ``Structural`` because it needs item alignment.
- Concrete families may define descriptors such as ``Type``.
- Concrete encodings may define carriers over native objects, JSON-like
  values, remote handles, or other representations.
"""

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
class Descriptor[T](Foundation[Any], Protocol):
    pass


@runtime_checkable
class StructuralDescriptor[T, K](
    Descriptor[T],
    Structural[K, Any],
    Protocol,
):
    pass


@runtime_checkable
class Carrier[T](Foundation[Any], Protocol):
    @property
    def descriptor(self) -> Descriptor[T]: ...


@runtime_checkable
class StructuralCarrier[T, K](
    Carrier[T],
    Structural[K, Any],
    Protocol,
):
    @property
    def descriptor(self) -> StructuralDescriptor[T, K]: ...


@runtime_checkable
class CarrierDescriptor[T, U](Carrier[T], Descriptor[U], Protocol):
    pass
