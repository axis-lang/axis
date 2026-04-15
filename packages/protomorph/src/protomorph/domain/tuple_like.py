from __future__ import annotations

from .type_ import Type as _Type


class TupleLikeType(_Type[tuple], abstract=True):
    def __len__(self) -> int:
        return super().__len__()

    def splice(self) -> TupleLikeType:
        return self
