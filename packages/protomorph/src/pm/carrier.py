from __future__ import annotations

from typing import Any, Self, Iterator

from protobase import Consed

import pm
from .foundation import _RECONSTRUCT, Id


class Carrier[T](Consed, abstract=True):
    """Cursor over typed data.

    Pairs a descriptor (Type) with data (payload) and exposes both
    targeted access (attr / item) and generic structural iteration.
    Traversal algorithms operate exclusively through this API.
    """

    descriptor: pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from .display import repr_any

        return repr_any(self)

    # ── Factory ───────────────────────────────────────────────────

    def child(self, tp: pm.Type, dt: Any) -> Carrier:
        """Produce a child carrier — the Type decides which carrier to use.
        Exception: if data is a Placeholder, always wrap as leaf."""
        if isinstance(dt, pm.Placeholder):
            return LeafCarrier(tp, dt)
        provider = pm._CARRIER_FACTORIES.get(type(tp), None)
        if provider is None:
            raise NotImplementedError(
                f"Custom carrier provider not implemented for {type(tp).__name__}"
            )
        return provider(tp, dt)

    # ── Meta navigation ───────────────────────────────────────────

    @property
    def type(self) -> Carrier[pm.Type[T]]:
        """Val wrapping this value's type."""
        return NativeObjectCarrier(self.descriptor.metatype(), self.descriptor)

    def fetch(self) -> T:
        """Extract the raw data payload."""
        return self.content

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
        return self.descriptor.arity == 0

    def __len__(self) -> int:
        a = self.descriptor.arity
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
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if _is_leaf(node):
                yield node
            else:
                children = list(node)
                stack.extend(reversed(children))

    def deep_map(self, f, is_leaf=None) -> Carrier:
        """Bottom-up map: apply *f* to leaves, reconstruct upward."""
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack: list[Any] = [self]
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
                children: list[Carrier] = list(item)
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
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False


class NativeObjectCarrier[T](Carrier[T]):
    """Val for Builtin / native Python objects with named fields."""

    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, getattr(self.content, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        assert (
            field.key is not None
        ), f"NativeObjectCarrier requires named fields (offset {offset})"
        return self.child(field.value, getattr(self.content, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        new_data = type(self.content)(*(c.fetch() for c in children))
        return type(self)(self.descriptor, new_data)


class LeafCarrier[T](Carrier[T]):
    """Val for leaf values — scalars, placeholders, etc.
    Always a leaf (arity=0), never traversed into."""

    @property
    def is_leaf(self) -> bool:
        return True

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class TupleCarrier(Carrier[tuple]):
    """Val for raw Python tuples (both uniform and varying)."""

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        return self.child(field.value, self.content[offset])

    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, self.content[field.offset])

    def __len__(self) -> int:
        a = self.descriptor.arity
        return a if a is not None else len(self.content)

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values = []
        for child in children:
            value = child.fetch()
            values.append(value)
        return type(self)(self.descriptor, tuple(values))

    def __invariants__(self):
        assert isinstance(self.descriptor, (pm.UniformType, pm.VaryingType)), "TupleCarrier requires uniform or varying type"
        assert isinstance(self.content, tuple), "TupleCarrier content must be a tuple"
