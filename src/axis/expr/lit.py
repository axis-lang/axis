from decimal import Decimal
from types import EllipsisType
from typing import ClassVar, Self

import protomorph as pm

from axis.literals import WildcardType, Wildcard
from axis import syn

from .bound_support import literal_to_bound


class Lit(syn.Expr):
    type Value = pm.Literal | EllipsisType | WildcardType

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

    def to_bound(self, scope: syn.ScopeLike) -> pm.Val:
        _ = scope
        return literal_to_bound(self.value, self)


#Special -> Wildcard, Ellipsis
