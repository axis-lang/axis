from __future__ import annotations

from typing import Any as _Any

import protomorph.core as _pm
from protobase import _

from protomorph.core.foundation import Builtin as _Builtin, AnyData as _AnyData
from .type_ import Type as _Type


class Placeholder(_Type, abstract=True):
    def metatype(self) -> _Type:
        return PlaceholderMetatype(self, 1)

    def display_label(self) -> str | None:
        return None


class Var(Placeholder, abstract=True):
    pass


class Mark(Placeholder, abstract=True):
    pass


class Op(Placeholder, abstract=True):
    pass


class WildcardMark(Mark):
    def display_label(self) -> str | None:
        return "_"


class EllipsisMark(Mark):
    def display_label(self) -> str | None:
        return "..."


class SelfMark(Mark):
    def display_label(self) -> str | None:
        return "self"


class PlaceholderMetatype(Placeholder):
    of: Placeholder
    level: int

    def metatype(self) -> _Type:
        return type(self)(self.of, self.level + 1)

    def display_label(self) -> str | None:
        base = self.of.display_label()
        if base is None:
            ident = getattr(self.of, "id", None)
            if isinstance(ident, str):
                base = ident
            else:
                slot = getattr(self.of, "slot", None)
                base = str(slot) if isinstance(slot, int) else type(self.of).__name__
        if self.level <= 3:
            return base + ("'" * self.level)
        return f"{base}^{self.level}"


class SimpleVar[C: _Builtin, I: _AnyData = str](Var):
    ctx: C | None = None
    id: I = _
    bound: _Type = _
    implicit_bound: bool = False

    def metatype(self):
        if self.implicit_bound:
            return PlaceholderMetatype(self, 1)
        return self.bound

    def display_label(self) -> str:
        return str(self.id)


def var[C: _Builtin, I: _AnyData](
    id: I, bound: _Type | _Any = None, ctx: C | None = None
) -> SimpleVar[C, I]:
    implicit_bound = bound is None
    if bound is None:
        bound = _pm.Spec.Any
    elif not isinstance(bound, _Type):
        bound = _pm.project_type(bound)
    return SimpleVar(id=id, bound=bound, ctx=ctx, implicit_bound=implicit_bound)


WILDCARD = WildcardMark()
ELLIPSIS = EllipsisMark()
SELF = SelfMark()
