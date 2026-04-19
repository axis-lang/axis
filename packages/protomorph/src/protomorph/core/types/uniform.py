from __future__ import annotations

import protomorph.core as _pm

from .tuple_like import TupleLike as _TupleLikeType


class Uniform[T](_TupleLikeType):
    element_type: _pm.Type[T]
    unique: bool = False

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of(_pm.anchors.uniform, self.element_type.metatype())

    def __contains__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Uniform):
            return False
        if self.unique and not other.unique:
            return False
        return super().__contains__(other)

    @property
    def schema(self) -> _pm.Schema | None:
        element_schema = self.element_type.schema
        if element_schema is None:
            return None
        return element_schema.map(
            lambda child: _pm.val(type(self)(child.content, unique=False))
        )

    def _contains_slots(self) -> tuple[_pm.Type, ...]:
        return (self.element_type,)
