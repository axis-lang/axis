from __future__ import annotations

from typing import Self, cast as _cast

import protomorph as pm
from protobase import slot_cached_property

from .base import Val


_SET_QUALIFIER = pm.Anchor("std.qualifiers.Set")


def _set_element_descriptor_of(qual: pm.Qual) -> pm.Type:
    qualifier = qual.last_qualifier
    if qualifier is None or qualifier.anchor != _SET_QUALIFIER:
        raise TypeError("Set carrier requires std.qualifiers.Set")
    return qual.unwrap


class Set[T](Val[frozenset[T]]):
    descriptor: pm.Qual
    content: frozenset[T]

    @property
    def is_leaf(self) -> bool:
        return False

    @slot_cached_property
    def ordered(self) -> tuple[T, ...]:
        return tuple(self.content)

    def __len__(self) -> int:
        return len(self.ordered)

    def __getitem__(self, offset: int) -> Val:
        return self.child(_set_element_descriptor_of(self.descriptor), self.ordered[offset])

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, type(self)(self.descriptor, frozenset(child.fetch() for child in children)))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, pm.Qual)
        qualifier = self.descriptor.last_qualifier
        assert qualifier is not None and qualifier.anchor == _SET_QUALIFIER
        assert isinstance(self.content, frozenset)
        element_descriptor = _set_element_descriptor_of(self.descriptor)
        for value in self.content:
            self.child(element_descriptor, value)
