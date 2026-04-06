from __future__ import annotations

from typing import Any, Iterator, cast

from protobase import flux

from .abstract.contract import Item

import protomorph
from .foundation import Builtin, Id, Datum

Field = Item


class Type[T](Builtin, abstract=True):

    # ── Classification ────────────────────────────────────────────

    def metatype(self) -> Type:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def make(self, data: T):
        return protomorph._make_carrier(self, data)

    @flux.property
    def schema(self) -> protomorph.TupleLikeType | None:
        tuple_like_type = getattr(protomorph, "TupleLikeType", None)
        if tuple_like_type is not None and isinstance(self, tuple_like_type):
            return cast(protomorph.TupleLikeType, self)
        return None

    # ── Structure (defaults: leaf / no children) ──────────────────

    @property
    def arity(self) -> int | None:
        return 0

    def item_at(self, offset: int) -> Item:
        raise IndexError(offset)

    def item(self, id: Id) -> Item:
        raise KeyError(id)

    def items(self) -> Iterator[Item]:
        a = self.arity
        if a is None:
            return
        for i in range(a):
            yield self.item_at(i)

    # ── Foundation protocol ───────────────────────────────────────

    def __len__(self) -> int:
        a = self.arity
        if a is None:
            raise TypeError(f"Unbounded type has no finite length: {type(self).__name__}")
        return a

    def __iter__(self) -> Iterator:
        for item in self.items():
            yield item.value


class Placeholder(Type, abstract=True):
    """Universal stand-in — can appear as Type, as data, anywhere.

    Behaves as Any: a leaf in traversal, captured/substituted later.
    Concrete variable forms refine identity and meaning.
    """

    def metatype(self) -> Type:
        return PlaceholderMetatype(self, 1)

    def display_label(self) -> str | None:
        return None


class Var(Placeholder, abstract=True):
    pass


class Mark(Placeholder, abstract=True):
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

    def metatype(self) -> Type:
        return type(self)(self.of, self.level + 1)

    def display_label(self) -> str | None:
        base = placeholder_label(self.of)
        if self.level <= 3:
            return base + ("'" * self.level)
        return f"{base}^{self.level}"


class SimpleVar[C: Builtin, I: Datum = str](Var):
    ctx: C
    id: I

    def display_label(self) -> str | None:
        return str(self.id)


def placeholder(id: str, context: Any = None) -> Placeholder:
    return SimpleVar(context, id)


WILDCARD = WildcardMark()
ELLIPSIS = EllipsisMark()
SELF = SelfMark()


def placeholder_name(value: Placeholder) -> str | None:
    ident = getattr(value, "id", None)
    return ident if isinstance(ident, str) else None


def placeholder_context(value: Placeholder) -> Any | None:
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


__all__ = [
    "Type",
    "Placeholder",
    "PlaceholderMetatype",
    "Var",
    "Mark",
    "WildcardMark",
    "EllipsisMark",
    "SelfMark",
    "SimpleVar",
    "WILDCARD",
    "ELLIPSIS",
    "SELF",
    "placeholder",
    "placeholder_name",
    "placeholder_context",
    "placeholder_slot",
    "placeholder_label",
    "Field",
]
