from __future__ import annotations

from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import Self
from typing import cast as _cast

import protomorph.core as _pm
from protobase import frozendict


from ..foundation import Id
from .base import Val



class Tuple[*T](Val[tuple[*T]]):
    Empty: _ClassVar[Tuple[tuple[()]]]

    descriptor: _pm.Type[tuple[*T]]

    @property
    def children(self) -> Tuple[*T]:
        return self

    def __len__(self) -> int:
        return len(self.content)

    def __iter__(self):
        for offset in range(len(self.content)):
            yield self[offset]

    def __getitem__(self, offset: int) -> Val:
        return _pm.make_value(_slot_descriptor_at(self.descriptor, offset), self.content[offset])

    def payload_item_at(self, offset: int) -> _pm.Item:
        key = self.descriptor.index.key_at(offset) if isinstance(self.descriptor, _pm.IndexedType) else None
        return _pm.Item(
            offset,
            key,
            _slot_descriptor_at(self.descriptor, offset),
        )

    def attr(self, id: Id) -> Val:
        if not isinstance(self.descriptor, _pm.IndexedType):
            raise KeyError(id)
        offset = self.descriptor.index.offset_of(id)
        return _pm.make_value(_slot_descriptor_at(self.descriptor, offset), self.content[offset])

    def __contains__(self, value: _Any) -> bool:
        return value in self.content

    @property
    def head(self) -> Val:
        return self[0]

    @property
    def tail(self) -> Self:
        if len(self.content) <= 1:
            return _cast(Self, self._new(_pm.VaryingType.Empty, ()))
        descriptor = self.descriptor
        if isinstance(descriptor, _pm.IndexedType):
            inner = _tail_inner(descriptor.inner)
            assert isinstance(inner, _pm.VaryingType)
            descriptor = _cast(
                _pm.Type[tuple[*T]],
                _pm.IndexedType(inner, descriptor.index.tail),
            )
        elif isinstance(descriptor, _pm.VaryingType):
            descriptor = _cast(_pm.Type[tuple[*T]], _pm.VaryingType(descriptor.values[1:]))
        return _cast(Self, self._new(descriptor, self.content[1:]))

    def splice(self) -> Self:
        if not any(isinstance(value, _pm.Spread) for value in self.content):
            return self
        new_values: list[_Any] = []
        for value in self.content:
            if isinstance(value, _pm.Spread):
                new_values.extend(value.values)
                continue
            new_values.append(value)
        assert isinstance(self.descriptor, _pm.TupleLikeType)
        descriptor = self.descriptor.splice()
        return _cast(Self, self._new(_cast(_pm.Type[tuple[*T]], descriptor), tuple(new_values)))

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, self._new(self.descriptor, tuple(child.fetch() for child in children)))

    def map(self, f) -> Tuple:
        mapped = tuple(f(child) for child in self)
        if not all(isinstance(child, Val) for child in mapped):
            raise TypeError("Tuple.map() callback must return Carrier values")
        carriers = _cast(tuple[Val, ...], mapped)
        content, child_descriptors = _mapped_tuple_parts(carriers)
        if isinstance(self.descriptor, _pm.UniformType):
            if not carriers:
                descriptor = _cast(_pm.Type[tuple], _pm.VaryingType.Empty)
            else:
                first = child_descriptors[0]
                if all(child_descriptor == first for child_descriptor in child_descriptors):
                    descriptor = _cast(
                        _pm.Type[tuple[*T]],
                        _pm.UniformType(first, unique=self.descriptor.unique and len(carriers) == len(set(content))),
                    )
                else:
                    descriptor = _cast(_pm.Type[tuple[*T]], _pm.VaryingType(child_descriptors))
            return _cast(Tuple, self._new(descriptor, content))
        if isinstance(self.descriptor, _pm.IndexedType):
            descriptor = _cast(
                _pm.Type[tuple[*T]],
                _pm.IndexedType(
                    _pm.VaryingType(child_descriptors),
                    self.descriptor.index,
                ),
            )
            return _cast(Tuple, self._new(descriptor, content))
        descriptor = _cast(_pm.Type[tuple[*T]], _pm.VaryingType(child_descriptors))
        return _cast(Tuple, self._new(descriptor, content))

    @classmethod
    def new(cls, *vals: Val, **kwvals: Val) -> Tuple:
        """Build a Tuple from Val children.

        Positional-only → unindexed (VaryingType).
        Any keyword argument → indexed (IndexedType), with positional slots
        getting ``None`` keys and keyword slots getting named Id keys.
        """
        if kwvals:
            all_vals = vals + tuple(kwvals.values())
            keys: tuple[Id | None, ...] = (None,) * len(vals) + tuple(Id(k) for k in kwvals)
            inner = _pm.VaryingType(tuple(v.descriptor for v in all_vals))
            descriptor = _pm.IndexedType(inner, Index.of(*keys))
            return cls(descriptor, tuple(v.content for v in all_vals))
        descriptor = _pm.VaryingType(tuple(v.descriptor for v in vals))
        return cls(descriptor, tuple(v.content for v in vals))

    @classmethod
    def empty(cls) -> Tuple[tuple[()]]:
        return _cast(Tuple[tuple[()]], cls.Empty)

    @classmethod
    def _new(cls, descriptor: _pm.Type[tuple[*T]], content: tuple[_Any, ...]) -> Tuple[*T]:
        return _cast(Tuple[*T], cls(descriptor, content))

    @classmethod
    def extends(cls, *tuples: Tuple) -> Tuple:
        if not tuples:
            return _cast(Tuple, cls.Empty)
        values: list[_Any] = []
        type_values: list[_pm.Type] = []
        index_parts: list[_pm.Index] = []
        has_index = False
        for tuple_ in tuples:
            values.extend(tuple_.content)
            descriptor = tuple_.descriptor
            if isinstance(descriptor, _pm.IndexedType):
                has_index = True
                type_values.extend(descriptor.inner.values)
                index_parts.append(descriptor.index)
            elif isinstance(descriptor, _pm.VaryingType):
                type_values.extend(descriptor.values)
                index_parts.append(Index.of(*((None,) * len(descriptor.values))))
            else:
                raise TypeError(f"Unsupported descriptor for Tuple.extends: {type(descriptor).__name__}")
        combined_type = _pm.VaryingType(tuple(type_values))
        if has_index:
            index = Index.concat(*index_parts)
            descriptor = _cast(_pm.Type[tuple], _pm.IndexedType(combined_type, index))
        else:
            descriptor = _cast(_pm.Type[tuple], combined_type)
        return _cast(Tuple, cls._new(descriptor, tuple(values)))

    def __invariants__(self):
        assert isinstance(self.content, tuple)
        if isinstance(self.descriptor, _pm.UniformType):
            return
        if isinstance(self.descriptor, _pm.IndexedType):
            expected = len(self.descriptor.index)
        elif isinstance(self.descriptor, _pm.VaryingType):
            expected = len(self.descriptor.values)
        else:
            expected = len(self.descriptor)
        assert len(self.content) == expected, "Tuple content must match descriptor length"

class Index[K : Id](Tuple[*tuple[K | None, ...]]):
    descriptor: _pm.UniformType[K | None]
    #content: tuple[K | None, ...]

    @property
    def is_sparse(self) -> bool:
        return len(self.content) > 0 and any(key is None for key in self.content)

    @property
    def keys(self) -> tuple[K | None, ...]:
        return self.content

    @property
    def offsets(self) -> frozendict[K, int]:
        return frozendict({key: offset for offset, key in enumerate(self.content) if key is not None})

    def key_at(self, offset: int) -> K | None:
        return self.content[offset]

    def offset_of(self, id: K) -> int:
        return self.offsets[id]

    def splice(self) -> Index:
        if not any(isinstance(value, _pm.Spread) for value in self.content):
            return self
        new_values: list[K | None] = []
        for value in self.content:
            if isinstance(value, _pm.Spread):
                new_values.extend(_cast(tuple[K | None, ...], value.values))
                continue
            new_values.append(value)
        return type(self).of(*new_values)

    @classmethod
    def of(cls, *keys: K | None) -> Index[K]:
        sparse = any(k is None for k in keys)
        id_type = _pm.Spec.Id
        element_type = (
            _cast(_pm.Type, _pm.Qual.of(id_type, _pm.Spec.of("std.qualifiers.Optional")))
            if sparse else id_type
        )
        return _cast(Index[K], cls(_pm.UniformType(element_type, unique=True), keys))
    
    @classmethod
    def concat(cls, *indices: Index[K]) -> Index[K]:
        values: list[K | None] = []
        for index in indices:
            values.extend(index.content)
        return cls.of(*values)

    def __invariants__(self):
        super().__invariants__()
        ids = [key for key in self.content if key is not None]
        assert len(ids) == len(set(ids)), "Index ids must be unique"


def _tail_inner(inner: _pm.Type) -> _pm.Type:
    if isinstance(inner, _pm.VaryingType):
        return _pm.VaryingType(inner.values[1:])
    if isinstance(inner, _pm.IndexedType):
        tail_inner = _tail_inner(inner.inner)
        assert isinstance(tail_inner, _pm.VaryingType)
        return _pm.IndexedType(tail_inner, inner.index.tail)
    return inner


def _slot_descriptor_at(descriptor: _pm.Type, offset: int) -> _pm.Type:
    if isinstance(descriptor, _pm.UniformType):
        return descriptor.element_type
    if isinstance(descriptor, _pm.IndexedType):
        return _slot_descriptor_at(descriptor.inner, offset)
    if isinstance(descriptor, _pm.VaryingType):
        return _cast(_pm.Type, descriptor.values[offset])
    schema = descriptor.schema
    if schema is None:
        raise TypeError(f"{type(descriptor).__name__} has no payload slot descriptors")
    return _cast(_pm.Type, schema[offset].fetch())


def _mapped_tuple_parts(carriers: tuple[Val, ...]) -> tuple[tuple[_Any, ...], tuple[_pm.Type, ...]]:
    return (
        tuple(child.fetch() for child in carriers),
        tuple(child.descriptor for child in carriers),
    )
