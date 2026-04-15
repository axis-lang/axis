from __future__ import annotations

from typing import Any as _Any

import protomorph as _pm
from protobase import _

from .builtin import Builtin as _Builtin
from .type_ import Datum as _Datum
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
        base = placeholder_label(self.of)
        if self.level <= 3:
            return base + ("'" * self.level)
        return f"{base}^{self.level}"


class SimpleVar[C: _Builtin, I: _Datum = str](Var):
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


def var[C: _Builtin, I: _Datum](
    id: I, bound: _Type | _Any = None, ctx: C | None = None
) -> SimpleVar[C, I]:
    implicit_bound = bound is None
    if bound is None:
        bound = _pm.Spec.of("std.types.Any")
    elif not isinstance(bound, _Type):
        bound = _pm.project_type(bound)
    return SimpleVar(id=id, bound=bound, ctx=ctx, implicit_bound=implicit_bound)


WILDCARD = WildcardMark()
ELLIPSIS = EllipsisMark()
SELF = SelfMark()


def placeholder_name(value: Placeholder) -> str | None:
    ident = getattr(value, "id", None)
    return ident if isinstance(ident, str) else None


def placeholder_context(value: Placeholder) -> _Any | None:
    return getattr(value, "ctx", None)


def placeholder_slot(value: Placeholder) -> int | None:
    slot = getattr(value, "slot", None)
    return slot if isinstance(slot, int) else None


def placeholder_label(value: Placeholder) -> str:
    label_fn = getattr(value, "display_label", None)
    if callable(label_fn):
        label = label_fn()
        if isinstance(label, str):
            return label
    ident = placeholder_name(value)
    if ident is not None:
        return ident
    slot = placeholder_slot(value)
    if slot is not None:
        return str(slot)
    return type(value).__name__
