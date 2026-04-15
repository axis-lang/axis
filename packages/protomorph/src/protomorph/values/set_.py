from __future__ import annotations

from collections.abc import Iterator as _Iterator
from typing import Any as _Any, Self, cast as _cast

import protomorph as pm
from protobase import slot_cached_property

from .base import Val


_SET_QUALIFIER = pm.Anchor("std.qualifiers.Set")


def _set_element_descriptor_of(qual: pm.Qual) -> pm.Type:
    if qual.qualifier.anchor != _SET_QUALIFIER:
        raise TypeError("Set carrier requires std.qualifiers.Set")
    return qual.qualified


class Set[T](Val[frozenset[T]]):
    descriptor: pm.Qual
    content: frozenset[T]

    @slot_cached_property
    def ordered(self) -> tuple[T, ...]:
        try:
            return tuple(sorted(_cast(tuple[_Any, ...], tuple(self.content))))
        except TypeError:
            return tuple(sorted(_cast(tuple[_Any, ...], tuple(self.content)), key=repr))

    def __len__(self) -> int:
        raise TypeError("Set structural traversal is not implemented yet")

    def __iter__(self) -> _Iterator[Val]:
        raise TypeError("Set structural traversal is not implemented yet")

    def _structural_child_count(self) -> int:
        return len(self.content)

    def _structural_children(self) -> tuple[Val, ...]:
        return tuple(self.elements())

    def elements(self) -> _Iterator[Val]:
        element_descriptor = _set_element_descriptor_of(self.descriptor)
        for value in self.ordered:
            yield self.child(element_descriptor, value)

    def __getitem__(self, offset: int) -> Val:
        raise TypeError("Set structural traversal is not implemented yet")

    def payload_item_at(self, offset: int) -> pm.Item:
        raise TypeError("Set structural traversal is not implemented yet")

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, type(self)(self.descriptor, frozenset(child.fetch() for child in children)))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual)
        qualifier = self.descriptor.qualifier
        assert qualifier is not None and qualifier.anchor == _SET_QUALIFIER
        assert isinstance(self.content, frozenset)
        element_descriptor = _set_element_descriptor_of(self.descriptor)
        for value in self.content:
            self.child(element_descriptor, value)
