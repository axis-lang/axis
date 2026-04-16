from __future__ import annotations

from collections.abc import Mapping as _Mapping
from typing import Any as _Any, Callable as _Callable, Iterator as _Iterator, Self, cast as _cast

from protobase import Consed

import protomorph.core as _pm


class Val[T](Consed, abstract=True):
    descriptor: _pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from ..display import repr_any

        return repr_any(self)

    @property
    def type(self) -> Val[_pm.Type[T]]:
        return _cast(Val[_pm.Type[T]], _pm.val(self.descriptor))

    def fetch(self) -> T:
        return self.content

    def attr(self, id: _pm.Id) -> Val:
        return self.children.attr(id)

    @property
    def children(self) -> _pm.Tuple:
        raise NotImplementedError(f"children not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Val:
        return self.children[offset]

    def payload_item_at(self, offset: int) -> _pm.Item:
        return self.children.payload_item_at(offset)

    @property
    def is_var(self) -> bool:
        return isinstance(self.content, _pm.Var)

    @property
    def is_wildcard(self) -> bool:
        return len(self.children) == 0 and self.content is _pm.WILDCARD

    def __len__(self) -> int:
        return len(self.children)

    def __iter__(self) -> _Iterator[Val]:
        yield from self.children

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        raise NotImplementedError(f"reconstruct() not implemented for {type(self).__name__}")



class NativeObjectCarrier[T](Val[T]):
    def _schema(self) -> _pm.Schema:
        structure = self.descriptor.schema
        if structure is None:
            raise TypeError(f"{type(self).__name__} requires a structured descriptor")
        return structure

    def _field_value(self, item: _pm.Item, content: tuple[_Any, ...]) -> _Any:
        if item.key is None:
            return content[item.offset]
        return getattr(self.content, item.key)

    def _field_payload(self, item: _pm.Item, child: Val) -> _Any:
        assert item.key is not None
        original = getattr(self.content, item.key)
        return child if isinstance(original, Val) else child.fetch()

    @property
    def children(self) -> _pm.Tuple:
        schema = self._schema()
        kwargs: dict[str, Val] = {}
        vals: list[Val] = []
        content = _cast(tuple[_Any, ...], self.content)
        for item in _schema_items(schema):
            child = _pm.make_value(item.value, self._field_value(item, content))
            if item.key is None:
                vals.append(child)
                continue
            kwargs[str(item.key)] = child
        return _pm.Tuple.new(*vals, **kwargs)

    def payload_item_at(self, offset: int) -> _pm.Item:
        return _schema_items(self._schema())[offset]

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        values: dict[str, _Any] = {}
        for item, child in zip(_schema_items(self._schema()), children):
            values[str(item.key)] = self._field_payload(item, child)
        return _cast(Self, type(self)(self.descriptor, type(self.content)(**values)))


class LeafCarrier[T](Val[T]):
    @property
    def children(self) -> _pm.Tuple:
        return _pm.Tuple.Empty

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        assert not children
        return self


def _schema_items(schema: _pm.Schema) -> tuple[_pm.Item, ...]:
    keys: tuple[_pm.Id | None, ...]
    if isinstance(schema.descriptor, _pm.IndexedType):
        keys = tuple(schema.descriptor.index.content)
    else:
        keys = (None,) * len(schema.content)
    return tuple(
        _pm.Item(offset, key, child.fetch())
        for offset, (key, child) in enumerate(zip(keys, schema, strict=True))
    )


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
