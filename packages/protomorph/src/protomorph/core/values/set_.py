from __future__ import annotations

from collections.abc import Iterator as _Iterator
from typing import Any as _Any, Self, cast as _cast

import protomorph.core as _pm
from protobase import slot_cached_property

from .base import Val


class Set[T](Val[frozenset[T]]):
    descriptor: _pm.Qual
    content: frozenset[T]

    @slot_cached_property
    def ordered(self) -> tuple[T, ...]:
        try:
            return tuple(sorted(_cast(tuple[_Any, ...], tuple(self.content))))
        except TypeError:
            return tuple(sorted(_cast(tuple[_Any, ...], tuple(self.content)), key=repr))

    @property
    def children(self) -> _pm.Tuple:
        raise NotImplementedError("Set logical children are not implemented yet")

    def values(self) -> _Iterator[Val]:
        for value in self.ordered:
            yield _pm.make_value(self.descriptor.qualified, value)

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, type(self)(self.descriptor, frozenset(child.content for child in children)))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, _pm.Qual)
        qualifier = self.descriptor.qualifier
        assert qualifier is not None and qualifier.anchor == _pm.anchors.set
        assert isinstance(self.content, frozenset)
        for value in self.content:
            _pm.make_value(self.descriptor.qualified, value)
