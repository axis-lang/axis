from __future__ import annotations

from collections.abc import Iterator as _Iterator
from typing import Self, cast as _cast

import protomorph as pm
from protobase import frozendict, slot_cached_property

from .base import Val


_MAP_QUALIFIER = pm.Anchor("std.qualifiers.Map")


def _map_value_descriptor_of(qual: pm.Qual) -> pm.Type:
    return qual.qualified


def _map_key_descriptor_of(qual: pm.Qual) -> pm.Type:
    if len(qual.qualifier.args) == 0:
        raise TypeError("Map carrier requires a key type")
    return _cast(pm.Type, qual.qualifier.args[0].fetch())


class Map[K, V](Val[frozendict[K, V]]):
    descriptor: pm.Qual
    content: frozendict[K, V]

    @slot_cached_property
    def ordered_items(self) -> tuple[tuple[K, V], ...]:
        return tuple(self.content.items())

    def __len__(self) -> int:
        raise TypeError("Map structural traversal is not implemented yet")

    def __iter__(self) -> _Iterator[Val]:
        raise TypeError("Map structural traversal is not implemented yet")

    def _structural_child_count(self) -> int:
        return len(self.content)

    def _structural_children(self) -> tuple[Val, ...]:
        return tuple(self.elements())

    def elements(self) -> _Iterator[Val]:
        value_descriptor = _map_value_descriptor_of(self.descriptor)
        for value in self.content.values():
            yield self.child(value_descriptor, value)

    def __getitem__(self, offset: int) -> Val:
        raise TypeError("Map structural traversal is not implemented yet")

    def payload_item_at(self, offset: int) -> pm.Item:
        raise TypeError("Map structural traversal is not implemented yet")

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        keys = tuple(key for key, _ in self.ordered_items)
        values = (child.fetch() for child in children)
        return _cast(Self, type(self)(self.descriptor, frozendict(zip(keys, values, strict=True))))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual)
        qualifier = self.descriptor.qualifier
        assert qualifier is not None and qualifier.anchor == _MAP_QUALIFIER
        assert isinstance(self.content, frozendict)

        key_descriptor = _map_key_descriptor_of(self.descriptor)
        value_descriptor = _map_value_descriptor_of(self.descriptor)
        for key, value in self.content.items():
            self.child(key_descriptor, key)
            self.child(value_descriptor, value)
