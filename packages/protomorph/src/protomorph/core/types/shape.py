from __future__ import annotations

from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLike as _TupleLike


class Shape(_TupleLike):
    active: _pm.Type
    parts: tuple[Shape, ...] | None

    def metatype(self) -> _pm.Type:
        return _pm.types.named(_pm.anchors.shape, self.active.metatype())

    def __contains__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Shape):
            return False
        if other.active not in self.active:
            return False
        if self.parts is None:
            return True
        if other.parts is None or self.active is not other.active:
            return False
        return all(
            other_part in self_part
            for self_part, other_part in zip(self.parts, other.parts, strict=True)
        )

    @property
    def schema(self) -> _pm.Schema:
        if self.parts is None:
            return _pm.Tuple.new(_pm.val(self.active))
        return _pm.Tuple.extends(*(part.schema for part in self.parts))

    @property
    def is_expanded(self) -> bool:
        return self.parts is not None

    @classmethod
    def collapsed(cls, active: _pm.Type) -> Shape:
        return cls(active, None)

    @classmethod
    def expanded(cls, active: _pm.Type, *parts: Shape) -> Shape:
        return cls(active, parts)

    def __invariants__(self) -> None:
        assert isinstance(self.active, _pm.Type), "Shape.active must be a Type"
        if isinstance(self.active, _pm.Union):
            assert self.parts is None, "Union-backed Shape must stay collapsed"
            return
        if self.parts is None:
            return

        active_schema = self.active.schema
        assert active_schema is not None, "Expanded Shape.active must expose schema"
        assert len(self.parts) == len(active_schema), (
            "Expanded Shape parts must match active schema length"
        )
        for part, expected in zip(self.parts, active_schema, strict=True):
            assert isinstance(part, Shape), "Shape parts must be Shape values"
            assert part.active in _cast(_pm.Type, expected.content), (
                "Shape part active type must be contained in active schema"
            )


def _shape_intersection(left: Shape, right: Shape) -> Shape:
    if right in left:
        return left
    if left in right:
        return right
    if left.parts is not None and right.parts is not None and left.active is right.active:
        return Shape.expanded(
            left.active,
            *(
                _shape_intersection(left_part, right_part)
                for left_part, right_part in zip(left.parts, right.parts, strict=True)
            ),
        )
    return Shape.collapsed(_pm.types.union(left.active, right.active))
