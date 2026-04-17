from __future__ import annotations

import protomorph.core as _pm

from .tuple_like import TupleLikeType as _TupleLikeType


class UniformType[T](_TupleLikeType):
    element_type: _pm.Type[T]
    unique: bool = False

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of("std.metas.Uniform", self.element_type.metatype())

    @property
    def schema(self) -> _pm.Schema | None:
        element_schema = self.element_type.schema
        if element_schema is None:
            return None
        return element_schema.map(
            lambda child: _pm.val(type(self)(child.content, unique=False))
        )
