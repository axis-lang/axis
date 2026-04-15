from __future__ import annotations

from typing import Any as _Any

import protomorph as _pm

from .type_ import Type as _Type


class UnionType[T: tuple[_Any, ...]](_Type[T]):
    variants: frozenset[_pm.Type]

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of("std.metas.Union")

    @property
    def schema(self) -> _pm.Schema | None:
        return None

    @classmethod
    def of(cls, *types: _pm.Type) -> _pm.Type:
        flat: set[_pm.Type] = set()
        for tp in types:
            if isinstance(tp, UnionType):
                flat.update(tp.variants)
                continue
            flat.add(tp)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))
