from __future__ import annotations

from enum import Enum
from types import EllipsisType


__all__ = ["WildcardType", "Wildcard", "EllipsisType"]


class WildcardType(Enum):
    VALUE = "_"


Wildcard = WildcardType.VALUE
