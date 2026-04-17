from __future__ import annotations

from collections.abc import Mapping as _Mapping
from typing import NamedTuple as _NamedTuple
from typing import Any as _Any, Callable as _Callable, Iterator as _Iterator, Self, cast as _cast

from protobase import Consed

import protomorph.core as _pm


class Entry[K, V](_NamedTuple):
    key: K | None
    value: Val[V]


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

    def entry_at(self, offset: int) -> Entry[_pm.Id, _Any]:
        return self.children.entry_at(offset)

    def entries(self) -> _Iterator[Entry[_pm.Id, _Any]]:
        yield from self.children.entries()

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

    def _field_value(self, offset: int, entry: Entry[_pm.Id, _Any], content: tuple[_Any, ...]) -> _Any:
        if entry.key is None:
            return content[offset]
        return getattr(self.content, entry.key)

    def _field_payload(self, entry: Entry[_pm.Id, _Any], child: Val) -> _Any:
        assert entry.key is not None
        original = getattr(self.content, entry.key)
        return child if isinstance(original, Val) else child.content

    @property
    def children(self) -> _pm.Tuple:
        schema = self._schema()
        kwargs: dict[str, Val] = {}
        vals: list[Val] = []
        content = _cast(tuple[_Any, ...], self.content)
        for offset, entry in enumerate(_schema_entries(schema)):
            child = _pm.make_value(entry.value.content, self._field_value(offset, entry, content))
            if entry.key is None:
                vals.append(child)
                continue
            kwargs[str(entry.key)] = child
        return _pm.Tuple.new(*vals, **kwargs)

    def entry_at(self, offset: int) -> Entry[_pm.Id, _Any]:
        return _child_entries(self.children)[offset]

    def entries(self) -> _Iterator[Entry[_pm.Id, _Any]]:
        yield from _child_entries(self.children)

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        values: dict[str, _Any] = {}
        for entry, child in zip(_schema_entries(self._schema()), children):
            values[str(entry.key)] = self._field_payload(entry, child)
        return _cast(Self, type(self)(self.descriptor, type(self.content)(**values)))


class LeafCarrier[T](Val[T]):
    @property
    def children(self) -> _pm.Tuple:
        if isinstance(self.content, (_pm.UniformType, _pm.VaryingType, _pm.IndexedType)):
            schema = self.content.schema
            if schema is None:
                return _pm.Tuple.Empty
            return schema
        return _pm.Tuple.Empty

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        if isinstance(self.content, _pm.VaryingType):
            rebuilt = _pm.VaryingType(
                tuple(_cast(_pm.Type, child.content) for child in children)
            )
            return _cast(Self, _leaf_with_content(self.descriptor, rebuilt))
        if isinstance(self.content, _pm.UniformType):
            rebuilt = _cast(_pm.UniformType, self.content)
            for child in children:
                rebuilt = _pm.UniformType(_cast(_pm.Type, child.content), unique=rebuilt.unique)
            return _cast(Self, _leaf_with_content(self.descriptor, rebuilt))
        if isinstance(self.content, _pm.IndexedType):
            rebuilt = _pm.IndexedType(
                _pm.VaryingType(tuple(_cast(_pm.Type, child.content) for child in children)),
                self.content.index,
            )
            return _cast(Self, _leaf_with_content(self.descriptor, rebuilt))
        assert not children
        return self


def _schema_entries(schema: _pm.Schema) -> tuple[Entry[_pm.Id, _Any], ...]:
    keys: tuple[_pm.Id | None, ...]
    if isinstance(schema.descriptor, _pm.IndexedType):
        keys = tuple(schema.descriptor.index.content)
    else:
        keys = (None,) * len(schema.content)
    return tuple(
        Entry(key, child)
        for offset, (key, child) in enumerate(zip(keys, schema, strict=True))
    )


def _child_entries(children: _pm.Tuple) -> tuple[Entry[_pm.Id, _Any], ...]:
    return tuple(children.entries())


def _leaf_with_content(descriptor: _pm.Type, content: _Any) -> LeafCarrier[_Any]:
    return LeafCarrier(descriptor, content)


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
