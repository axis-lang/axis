from __future__ import annotations

from .type_ import Type as _Type


class TupleLikeType(_Type[tuple], abstract=True):
    pass
