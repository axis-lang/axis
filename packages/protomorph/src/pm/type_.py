from __future__ import annotations

from typing import Any, Iterator

from .abstract.contract import Item

import pm
from .foundation import Builtin, Id

Field = Item


class Type[T](Builtin, abstract=True):

    # ── Classification ────────────────────────────────────────────

    def metatype(self) -> Type:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def make(self, data: T):
        carrier_fact = pm.carrier_factory_for(self)
        if carrier_fact is None:
            raise NotImplementedError(f"No carrier factory for type {type(self).__name__}")
        return carrier_fact(self, data)

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
        return self

    def display_label(self) -> str | None:
        return None


class Var(Placeholder, abstract=True):
    pass


class SimpleVar(Var):
    ctx: Builtin | None
    id: str

    def display_label(self) -> str | None:
        return self.id


def placeholder(id: str, context: Any = None) -> Placeholder:
    return SimpleVar(context, id)


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
    "Var",
    "SimpleVar",
    "placeholder",
    "placeholder_name",
    "placeholder_context",
    "placeholder_slot",
    "placeholder_label",
    "Field",
]
