from decimal import Decimal
from types import EllipsisType
from typing import ClassVar, Self
import protomorph as pm

from axis.literals import WildcardType, Wildcard
from axis import syn


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


#Special -> Wildcard, Ellipsis
