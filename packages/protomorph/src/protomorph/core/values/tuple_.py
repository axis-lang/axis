from __future__ import annotations

from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import Self
from typing import cast as _cast

import protomorph.core as _pm
from protobase import frozendict


from ..foundation import Id
from .base import Entry, Val



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

    def __getitem__(self, key: int | slice) -> Val | Self:
        if isinstance(key, slice):
            descriptor = _slice_descriptor(self.descriptor, key)
            return _cast(Self, self._new(_cast(_pm.Type[tuple[*T]], descriptor), self.content[key]))
        return _pm.make_value(_slot_descriptor_at(self.descriptor, key), self.content[key])

    def entry_at(self, offset: int) -> Entry[Id, _Any]:
        key = self.descriptor.index.key_at(offset) if isinstance(self.descriptor, _pm.Indexed) else None
        return Entry(
            key,
            _pm.make_value(_slot_descriptor_at(self.descriptor, offset), self.content[offset]),
        )

    def entries(self):
        for offset in range(len(self.content)):
            yield self.entry_at(offset)

    def attr(self, id: Id) -> Val:
        if not isinstance(self.descriptor, _pm.Indexed):
            raise KeyError(id)
        offset = self.descriptor.index.offset_of(id)
        return _pm.make_value(_slot_descriptor_at(self.descriptor, offset), self.content[offset])

    def __contains__(self, value: _Any) -> bool:
        return value in self.content

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, self._new(self.descriptor, tuple(child.content for child in children)))

    def map(self, f) -> Tuple:
        mapped = tuple(f(child) for child in self)
        if not all(isinstance(child, Val) for child in mapped):
            raise TypeError("Tuple.map() callback must return Carrier values")
        carriers = _cast(tuple[Val, ...], mapped)
        content, child_descriptors = _mapped_tuple_parts(carriers)
        if isinstance(self.descriptor, _pm.Uniform):
            if not carriers:
                descriptor = _cast(_pm.Type[tuple], _pm.Varying.Empty)
            else:
                first = child_descriptors[0]
                if all(child_descriptor == first for child_descriptor in child_descriptors):
                    descriptor = _cast(
                        _pm.Type[tuple[*T]],
                        _pm.Uniform(first, unique=self.descriptor.unique and len(carriers) == len(set(content))),
                    )
                else:
                    descriptor = _cast(_pm.Type[tuple[*T]], _pm.Varying(child_descriptors))
            return _cast(Tuple, self._new(descriptor, content))
        if isinstance(self.descriptor, _pm.Indexed):
            descriptor = _cast(
                _pm.Type[tuple[*T]],
                _pm.Indexed(
                    _pm.Varying(child_descriptors),
                    self.descriptor.index,
                ),
            )
            return _cast(Tuple, self._new(descriptor, content))
        descriptor = _cast(_pm.Type[tuple[*T]], _pm.Varying(child_descriptors))
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
            inner = _pm.Varying(tuple(v.descriptor for v in all_vals))
            descriptor = _pm.Indexed(inner, Index.of(*keys))
            return cls(descriptor, tuple(v.content for v in all_vals))
        descriptor = _pm.Varying(tuple(v.descriptor for v in vals))
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
            if isinstance(descriptor, _pm.Indexed):
                has_index = True
                type_values.extend(_slot_types(descriptor.slots, len(descriptor.index)))
                index_parts.append(descriptor.index)
            elif isinstance(descriptor, _pm.Varying):
                type_values.extend(descriptor.element_types)
                index_parts.append(Index.of(*((None,) * len(descriptor.element_types))))
            elif isinstance(descriptor, _pm.Uniform):
                type_values.extend((descriptor.element_type,) * len(tuple_.content))
            else:
                raise TypeError(f"Unsupported descriptor for Tuple.extends: {type(descriptor).__name__}")
        combined_type = _pm.Varying(tuple(type_values))
        if has_index:
            index = Index.concat(*index_parts)
            descriptor = _cast(_pm.Type[tuple], _pm.Indexed(combined_type, index))
        else:
            descriptor = _cast(_pm.Type[tuple], combined_type)
        return _cast(Tuple, cls._new(descriptor, tuple(values)))

    def __invariants__(self):
        super().__invariants__()
        assert isinstance(self.content, tuple)
        if isinstance(self.descriptor, _pm.Uniform):
            return
        if isinstance(self.descriptor, _pm.Indexed):
            expected = len(self.descriptor.index)
        elif isinstance(self.descriptor, _pm.Varying):
            expected = len(self.descriptor.element_types)
        else:
            expected = len(self.descriptor)
        assert len(self.content) == expected, "Tuple content must match descriptor length"

class Index[K: _pm.AnyData = Id](Tuple[*tuple[K | None, ...]]):
    descriptor: _pm.Uniform[K | None]
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

    def __getitem__(self, key: int | slice) -> Val | Index[K]:
        if isinstance(key, slice):
            return type(self).of(*self.content[key])
        return super().__getitem__(key)

    @classmethod
    def of(cls, *keys: K | None) -> Index[K]:
        sparse = any(k is None for k in keys)
        id_type = _pm.Spec.Id
        element_type = (
            _cast(_pm.Type, _pm.types.optional(id_type))
            if sparse else id_type
        )
        return _cast(Index[K], cls(_pm.Uniform(element_type, unique=True), keys))
    
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


def _slice_descriptor(descriptor: _pm.Type, key: slice) -> _pm.Type:
    if isinstance(descriptor, _pm.Uniform):
        return descriptor
    if isinstance(descriptor, _pm.Indexed):
        fetched_slots = (
            descriptor.slots
            if isinstance(descriptor.slots, _pm.Uniform)
            else _pm.Varying(descriptor.slots.element_types[key])
        )
        index = descriptor.index[key]
        assert isinstance(index, _pm.Index)
        return _pm.Indexed(fetched_slots, index)
    if isinstance(descriptor, _pm.Varying):
        return _pm.Varying(descriptor.element_types[key])
    schema = descriptor.schema
    if schema is None:
        raise TypeError(f"{type(descriptor).__name__} does not support slicing")
    sliced = schema[key]
    assert isinstance(sliced, _pm.Tuple)
    return _cast(_pm.Type, sliced.content)


def _slot_descriptor_at(descriptor: _pm.Type, offset: int) -> _pm.Type:
    if isinstance(descriptor, _pm.Uniform):
        return descriptor.element_type
    if isinstance(descriptor, _pm.Indexed):
        return _slot_descriptor_at(descriptor.slots, offset)
    if isinstance(descriptor, _pm.Varying):
        return _cast(_pm.Type, descriptor.element_types[offset])
    schema = descriptor.schema
    if schema is None:
        raise TypeError(f"{type(descriptor).__name__} has no payload slot descriptors")
    return _cast(_pm.Type, schema[offset].content)


def _mapped_tuple_parts(carriers: tuple[Val, ...]) -> tuple[tuple[_Any, ...], tuple[_pm.Type, ...]]:
    return (
        tuple(child.content for child in carriers),
        tuple(child.descriptor for child in carriers),
    )


def _slot_types(descriptor: _pm.Uniform | _pm.Varying, size: int) -> tuple[_pm.Type, ...]:
    if isinstance(descriptor, _pm.Uniform):
        return (descriptor.element_type,) * size
    return descriptor.element_types
