from __future__ import annotations

from .type_ import Type as _Type


class TupleLike(_Type[tuple], abstract=True):
    def _contains_slots(self) -> tuple[_Type, ...]:
        raise NotImplementedError(
            f"{type(self).__name__} must define logical containment slots"
        )

    def __contains__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, TupleLike) or type(self) is not type(other):
            return False

        left_slots = self._contains_slots()
        right_slots = other._contains_slots()
        return len(left_slots) == len(right_slots) and all(
            right in left
            for left, right in zip(left_slots, right_slots, strict=True)
        )
