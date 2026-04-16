from __future__ import annotations

from collections.abc import Iterator as _Iterator
from typing import Self, cast as _cast

import protomorph.core as _pm
from protobase import frozendict, slot_cached_property

from .base import Val
from ..foundation import Anchor

_MAP_QUALIFIER = Anchor("std.qualifiers.Map")


class Map[K, V](Val[frozendict[K, V]]):
    descriptor: _pm.Qual
    content: frozendict[K, V]

    @slot_cached_property
    def ordered_items(self) -> tuple[tuple[K, V], ...]:
        return tuple(self.content.items())

    @property
    def children(self) -> _pm.Tuple:
        raise NotImplementedError("Map logical children are not implemented yet")

    def values(self) -> _Iterator[Val]:
        for value in self.content.values():
            yield _pm.make_value(self.descriptor.qualified, value)

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        keys = tuple(key for key, _ in self.ordered_items)
        values = (child.fetch() for child in children)
        return _cast(Self, type(self)(self.descriptor, frozendict(zip(keys, values, strict=True))))

    def __invariants__(self) -> None:
        super().__invariants__()
        assert isinstance(self.descriptor, _pm.Qual)
        qualifier = self.descriptor.qualifier
        assert qualifier is not None and qualifier.anchor == _MAP_QUALIFIER
        assert isinstance(self.content, frozendict)

        key_descriptor = _cast(_pm.Type, qualifier.args[0].fetch())
        for key, value in self.content.items():
            _pm.make_value(key_descriptor, key)
            _pm.make_value(self.descriptor.qualified, value)
