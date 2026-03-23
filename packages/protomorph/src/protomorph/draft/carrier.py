from __future__ import annotations

from typing import Any, Self, Iterator

from protobase import Consed

from .. import draft as mp
from .foundation import _RECONSTRUCT, Id


class Carrier[T](Consed, abstract=True):
    """Cursor over typed data.

    Pairs a Type (classifier) with data (payload) and exposes both
    targeted access (attr / item) and generic structural iteration.
    Traversal algorithms operate exclusively through this API.
    """

    __type__: mp.Type[T]
    __data__: T

    # ── Factory ───────────────────────────────────────────────────

    def child(self, meta: mp.Type, data: Any) -> Carrier:
        """Produce a child carrier — the Type decides which carrier to use.
        Exception: if data is a Placeholder, always wrap as leaf."""
        if isinstance(data, mp.Placeholder):
            return LeafCarrier(meta, data)
        return meta.carrier(data)

    # ── Meta navigation ───────────────────────────────────────────

    @property
    def type(self) -> Carrier[mp.Type[T]]:
        """Carrier wrapping this value's type."""
        return NativeObjectCarrier(self.__type__.metatype(), self.__type__)

    def fetch(self) -> T:
        """Extract the raw data payload."""
        return self.__data__

    # ── Targeted access ───────────────────────────────────────────

    def attr(self, id: Id) -> Carrier:
        """Access a child by name."""
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Carrier:
        """Access a child by positional offset."""
        raise NotImplementedError(
            f"__getitem__ not implemented for {type(self).__name__}"
        )

    # ── Structural algebra ────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return self.__type__.arity == 0

    def __len__(self) -> int:
        a = self.__type__.arity
        if a is not None:
            return a
        raise NotImplementedError(
            f"__len__ for unbounded type: override in {type(self).__name__}"
        )

    def __iter__(self) -> Iterator[Carrier]:
        for i in range(len(self)):
            yield self[i]

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        """Rebuild this carrier with *children* replacing the current ones."""
        raise NotImplementedError(
            f"reconstruct() not implemented for {type(self).__name__}"
        )

    # ── Derived traversals ────────────────────────────────────────

    def deep_iter(self, is_leaf=None) -> Iterator[Carrier]:
        """Depth-first iteration over leaf carriers."""
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack = [self]
        while stack:
            node = stack.pop()
            if _is_leaf(node):
                yield node
            else:
                stack.extend(reversed(list(node)))

    def deep_map(self, f, is_leaf=None) -> Carrier:
        """Bottom-up map: apply *f* to leaves, reconstruct upward."""
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack: list = [self]
        results: list[Carrier] = []
        while stack:
            item = stack.pop()
            if item is _RECONSTRUCT:
                node, n = stack.pop()
                new_children = tuple(results[len(results) - n :])
                del results[len(results) - n :]
                results.append(node.reconstruct(new_children))
            elif _is_leaf(item):
                results.append(f(item))
            else:
                children = list(item)
                stack.append((item, len(children)))
                stack.append(_RECONSTRUCT)
                stack.extend(reversed(children))
        return results[0]

    def subst(self, mapping: dict) -> Carrier:
        """Substitute carriers according to *mapping*."""

        def _is_leaf(c):
            return c in mapping or c.is_leaf

        return self.deep_map(lambda c: mapping.get(c, c), is_leaf=_is_leaf)

    def search(self, target: Carrier) -> bool:
        """Return True if *target* appears anywhere in this structure."""
        stack = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(node)
        return False


class NativeObjectCarrier[T](Carrier[T]):
    """Carrier for Builtin / native Python objects with named fields."""

    def attr(self, id: Id) -> Carrier:
        field = self.__type__.field(id)
        return self.child(field.type, getattr(self.__data__, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.__type__.field_at(offset)
        assert (
            field.key is not None
        ), f"NativeObjectCarrier requires named fields (offset {offset})"
        return self.child(field.type, getattr(self.__data__, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        new_data = type(self.__data__)(*(c.fetch() for c in children))
        return type(self)(self.__type__, new_data)


class LeafCarrier[T](Carrier[T]):
    """Carrier for leaf values — scalars, placeholders, etc.
    Always a leaf (arity=0), never traversed into."""

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class TupleCarrier(Carrier[tuple]):
    """Carrier for raw Python tuples (both uniform and varying)."""

    def __getitem__(self, offset: int) -> Carrier:
        field = self.__type__.field_at(offset)
        return self.child(field.type, self.__data__[offset])

    def attr(self, id: Id) -> Carrier:
        field = self.__type__.field(id)
        return self.child(field.type, self.__data__[field.offset])

    def __len__(self) -> int:
        a = self.__type__.arity
        return a if a is not None else len(self.__data__)

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        return type(self)(self.__type__, tuple(c.fetch() for c in children))
