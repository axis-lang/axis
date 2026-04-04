from __future__ import annotations

from decimal import Decimal
from types import EllipsisType
from typing import Any, ClassVar, Self

import protomorph as pm

from axis.literals import WildcardType, Wildcard
from axis import log, syn

from .lowering import literal_to_bound


class Lit(syn.Expr):
    type Value = int | float | str | bool | None | EllipsisType | WildcardType

    @classmethod
    def build(cls, value: Value) -> Self:
        return cls(value=value)

    value: Value

    @property
    def is_wildcard(self) -> bool:
        return self.value is Wildcard

    @property
    def is_ellipsis(self) -> bool:
        return self.value is Ellipsis

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        _ = scope
        return literal_to_bound(self.value, self)


#Special -> Wildcard, Ellipsis
