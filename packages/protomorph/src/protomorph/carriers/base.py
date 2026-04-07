from __future__ import annotations

from collections.abc import Mapping as _Mapping
from typing import Any as _Any, Callable as _Callable, Iterator as _Iterator, Self, cast as _cast

from protobase import Consed, slot_cached_property

import protomorph as pm

_RECONSTRUCT = object()


class Carrier[T](Consed, abstract=True):
    descriptor: pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from ..display import repr_any

        return repr_any(self)

    def child(self, tp: pm.Type, dt: _Any) -> Carrier:
        if isinstance(dt, Carrier):
            return dt
        if isinstance(dt, pm.Var | pm.Mark):
            if isinstance(tp, pm.Spec) and pm.REALM.get().schema_for(tp) is not None:
                return pm.carrier(tp, dt)
            return LeafCarrier(tp, dt)
        if isinstance(dt, pm.Type):
            return dt.metatype().make(dt)
        return pm.carrier(tp, dt)

    @property
    def type(self) -> Carrier[pm.Type[T]]:
        return _cast(Carrier[pm.Type[T]], pm.wrap(self.descriptor))

    def fetch(self) -> T:
        return self.content

    def match(self, subject: _Any, **kwargs: _Any):
        from ..match import match

        return match(self, subject, **kwargs)

    def attr(self, id: pm.Id) -> Carrier:
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Carrier:
        raise NotImplementedError(f"__getitem__ not implemented for {type(self).__name__}")

    @property
    def is_leaf(self) -> bool:
        return self.descriptor.arity == 0

    def __len__(self) -> int:
        arity = self.descriptor.arity
        if arity is not None:
            return arity
        raise NotImplementedError(f"__len__ for unbounded type: override in {type(self).__name__}")

    def __iter__(self) -> _Iterator[Carrier]:
        for offset in range(len(self)):
            yield self[offset]

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        raise NotImplementedError(f"reconstruct() not implemented for {type(self).__name__}")

    def deep_iter(self, is_leaf: _Callable[[Carrier], bool] | None = None) -> _Iterator[Carrier]:
        is_leaf_fn = is_leaf or (lambda carrier: carrier.is_leaf)
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if is_leaf_fn(node):
                yield node
                continue
            children = list(node)
            stack.extend(reversed(children))

    def deep_map(
        self,
        f: _Callable[[Carrier], Carrier],
        is_leaf: _Callable[[Carrier], bool] | None = None,
    ) -> Carrier:
        is_leaf_fn = is_leaf or (lambda carrier: carrier.is_leaf)
        stack: list[_Any] = [self]
        results: list[Carrier] = []
        while stack:
            item = stack.pop()
            if item is _RECONSTRUCT:
                node, size = stack.pop()
                new_children = tuple(results[len(results) - size :])
                del results[len(results) - size :]
                results.append(node.reconstruct(new_children))
                continue
            if is_leaf_fn(item):
                results.append(f(item))
                continue
            children = list(item)
            stack.append((item, len(children)))
            stack.append(_RECONSTRUCT)
            stack.extend(reversed(children))
        return results[0]

    def subst(self, mapping: _Mapping[Carrier, Carrier]) -> Carrier:
        return self.deep_map(lambda carrier: mapping.get(carrier, carrier), is_leaf=lambda carrier: carrier in mapping or carrier.is_leaf)

    def subst_where(
        self,
        pred: _Callable[[Carrier], bool],
        replace: _Callable[[Carrier], Carrier],
    ) -> Carrier:
        mapping: dict[Carrier, Carrier] = {}
        for leaf in self.deep_iter():
            if pred(leaf):
                mapping[leaf] = replace(leaf)
        return self if not mapping else self.subst(mapping)

    def subst_marks(self, mapping: _Mapping[pm.Mark, Carrier | pm.Datum]) -> Carrier:
        def pred(leaf: Carrier) -> bool:
            value = leaf.fetch()
            return isinstance(value, pm.Mark) and value in mapping

        def replace(leaf: Carrier) -> Carrier:
            value = _cast(pm.Mark, leaf.fetch())
            replacement = mapping[value]
            if isinstance(replacement, Carrier):
                return replacement
            return pm.wrap(replacement)

        return self.subst_where(pred, replace)

    def subst_self(self, subject: Carrier | pm.Datum) -> Carrier:
        replacement = subject if isinstance(subject, Carrier) else pm.wrap(subject)
        return self.subst_marks({pm.SELF: replacement})

    def search(self, target: Carrier) -> bool:
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False

    @slot_cached_property
    def is_pattern(self) -> bool:
        from ..match import Node

        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            value = node.fetch()
            if isinstance(value, Node | pm.Placeholder | pm.Var):
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False


class NativeObjectCarrier[T](Carrier[T]):
    def attr(self, id: pm.Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, getattr(self.content, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        assert field.key is not None
        return self.child(field.value, getattr(self.content, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values: dict[str, _Any] = {}
        for item, child in zip(self.descriptor.items(), children):
            assert item.key is not None
            original = getattr(self.content, item.key)
            values[str(item.key)] = child if isinstance(original, Carrier) else child.fetch()
        return _cast(Self, type(self)(self.descriptor, type(self.content)(**values)))


class LeafCarrier[T](Carrier[T]):
    @property
    def is_leaf(self) -> bool:
        return True

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class UnwrapError(Exception):
    def __init__(self, payload: _Any = None, message: str | None = None) -> None:
        self.payload = payload
        self.message = message
        if payload is None:
            super().__init__(message or "called unwrap on empty carrier")
            return
        if message is None:
            super().__init__(repr(payload))
            return
        super().__init__(f"{message}: {payload!r}")


ResultUnwrapError = UnwrapError
OptionUnwrapError = UnwrapError
