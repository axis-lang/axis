from __future__ import annotations

from collections.abc import Mapping as _Mapping
from typing import Any as _Any, Callable as _Callable, Iterator as _Iterator, Self, cast as _cast

from protobase import Consed, slot_cached_property

import protomorph as pm

_RECONSTRUCT = object()


class Val[T](Consed, abstract=True):
    descriptor: pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from ..display import repr_any

        return repr_any(self)

    def child(self, tp: pm.Type, dt: _Any) -> Val:
        if isinstance(dt, Val):
            return dt
        if isinstance(dt, pm.Var | pm.Mark):
            if isinstance(tp, pm.Spec) and tp.schema is not None:
                return pm.make_value(tp, dt)
            return LeafCarrier(tp, dt)
        if isinstance(dt, pm.Type):
            return dt.metatype().make(dt)
        return pm.make_value(tp, dt)

    @property
    def type(self) -> Val[pm.Type[T]]:
        return _cast(Val[pm.Type[T]], pm.val(self.descriptor))

    def fetch(self) -> T:
        return self.content

    def match(self, subject: _Any, **kwargs: _Any):
        from ..match import match

        return match(self, subject, **kwargs)

    def attr(self, id: pm.Id) -> Val:
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Val:
        raise NotImplementedError(f"__getitem__ not implemented for {type(self).__name__}")

    def payload_item_at(self, offset: int) -> pm.Item:
        raise NotImplementedError(f"payload_item_at() not implemented for {type(self).__name__}")

    @property
    def is_var(self) -> bool:
        return isinstance(self.content, pm.Var)

    @property
    def is_wildcard(self) -> bool:
        return not self._has_structural_children() and self.content is pm.WILDCARD

    def __len__(self) -> int:
        return len(self._structural_children())

    def __iter__(self) -> _Iterator[Val]:
        yield from self._structural_children()

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        raise NotImplementedError(f"reconstruct() not implemented for {type(self).__name__}")

    def _structural_children(self) -> tuple[Val, ...]:
        return tuple(self[i] for i in range(self._structural_child_count()))

    def _structural_child_count(self) -> int:
        raise NotImplementedError(f"_structural_child_count() not implemented for {type(self).__name__}")

    def _has_structural_children(self) -> bool:
        try:
            return self._structural_child_count() > 0
        except (NotImplementedError, TypeError):
            return False

    def iter(self) -> _Iterator[Val]:
        stack: list[Val] = [self]
        while stack:
            node = stack.pop()
            yield node
            if node._has_structural_children():
                stack.extend(reversed(node._structural_children()))

    def iter_leafs(self) -> _Iterator[Val]:
        return (node for node in self.iter() if not node._has_structural_children())

    def iter_branches(self) -> _Iterator[Val]:
        return (node for node in self.iter() if node._has_structural_children())

    def deep_map(
        self,
        f: _Callable[[Val], Val],
        is_leaf: _Callable[[Val], bool] | None = None,
    ) -> Val:
        is_leaf_fn = is_leaf or (lambda carrier: not carrier._has_structural_children())
        stack: list[_Any] = [self]
        results: list[Val] = []
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
            children = list(item._structural_children())
            stack.append((item, len(children)))
            stack.append(_RECONSTRUCT)
            stack.extend(reversed(children))
        return results[0]

    def subst(self, mapping: _Mapping[Val, Val]) -> Val:
        if not mapping:
            return self
        return self.deep_map(
            lambda carrier: mapping.get(carrier, carrier),
            is_leaf=lambda carrier: carrier in mapping or not carrier._has_structural_children(),
        )

    def subst_where(
        self,
        pred: _Callable[[Val], bool],
        replace: _Callable[[Val], Val],
    ) -> Val:
        mapping: dict[Val, Val] = {}
        for leaf in self.iter_leafs():
            if pred(leaf):
                mapping[leaf] = replace(leaf)
        return self if not mapping else self.subst(mapping)

    def subst_marks(self, mapping: _Mapping[pm.Mark, Val | pm.Datum]) -> Val:
        def pred(leaf: Val) -> bool:
            value = leaf.fetch()
            return isinstance(value, pm.Mark) and value in mapping

        def replace(leaf: Val) -> Val:
            value = _cast(pm.Mark, leaf.fetch())
            replacement = mapping[value]
            if isinstance(replacement, Val):
                return replacement
            return pm.val(replacement)

        return self.subst_where(pred, replace)

    def subst_self(self, subject: Val | pm.Datum) -> Val:
        replacement = subject if isinstance(subject, Val) else pm.val(subject)
        return self.subst_marks({pm.SELF: replacement})

    def search(self, target: Val) -> bool:
        stack: list[Val] = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node._has_structural_children():
                stack.extend(node._structural_children())
        return False

    @slot_cached_property
    def is_pattern(self) -> bool:
        from ..match import Node

        stack: list[Val] = [self]
        while stack:
            node = stack.pop()
            value = node.fetch()
            if isinstance(value, Node | pm.Placeholder | pm.Var):
                return True
            if node._has_structural_children():
                stack.extend(node._structural_children())
        return False


class NativeObjectCarrier[T](Val[T]):
    def _schema(self) -> pm.Schema:
        structure = self.descriptor.schema
        if structure is None:
            raise TypeError(f"{type(self).__name__} requires a structured descriptor")
        return structure

    def _structural_child_count(self) -> int:
        return len(self._schema())

    def payload_item_at(self, offset: int) -> pm.Item:
        schema = self._schema()
        child = schema[offset]
        key = None
        if isinstance(schema.descriptor, pm.IndexedType):
            key = schema.descriptor.index.key_at(offset)
        return pm.Item(offset, key, child.fetch())

    def attr(self, id: pm.Id) -> Val:
        schema = self._schema()
        return self.child(_schema_attr(schema, id).fetch(), getattr(self.content, id))

    def __getitem__(self, offset: int) -> Val:
        item = self.payload_item_at(offset)
        assert item.key is not None
        return self.child(item.value, getattr(self.content, item.key))

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        values: dict[str, _Any] = {}
        for item, child in zip(_schema_items(self._schema()), children):
            assert item.key is not None
            original = getattr(self.content, item.key)
            values[str(item.key)] = child if isinstance(original, Val) else child.fetch()
        return _cast(Self, type(self)(self.descriptor, type(self.content)(**values)))


class LeafCarrier[T](Val[T]):
    def _structural_child_count(self) -> int:
        return 0

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        assert not children
        return self


def _schema_items(schema: pm.Schema) -> tuple[pm.Item, ...]:
    keys: tuple[pm.Id | None, ...]
    if isinstance(schema.descriptor, pm.IndexedType):
        keys = tuple(schema.descriptor.index.content)
    else:
        keys = (None,) * len(schema.content)
    return tuple(
        pm.Item(offset, key, child.fetch())
        for offset, (key, child) in enumerate(zip(keys, schema, strict=True))
    )


def _schema_attr(schema: pm.Schema, id: pm.Id) -> pm.Val[pm.Type]:
    if not isinstance(schema.descriptor, pm.IndexedType):
        raise KeyError(id)
    offset = schema.descriptor.index.offset_of(id)
    return _cast(pm.Val[pm.Type], schema[offset])


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
