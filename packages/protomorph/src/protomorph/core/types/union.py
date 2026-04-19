from __future__ import annotations

from typing import Any as _Any

import protomorph.core as _pm

from .type_ import Type as _Type


class Union[T: tuple[_Any, ...]](_Type[T]):
    variants: frozenset[_pm.Type]

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of(_pm.anchors.union)

    def __contains__(self, other: object) -> bool:
        if self is other:
            return True
        if isinstance(other, Union):
            return all(
                any(variant in option for option in self.variants)
                for variant in other.variants
            )
        if not isinstance(other, _pm.Type):
            return False
        return any(other in option for option in self.variants)

    @property
    def schema(self) -> _pm.Schema | None:
        return None

    @classmethod
    def of(cls, *types: _pm.Type):
        flat: set[_pm.Type] = set()
        for tp in types:
            if isinstance(tp, Union):
                flat.update(tp.variants)
                continue
            flat.add(tp)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))
