from __future__ import annotations

from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import Self
from typing import cast as _cast

import protomorph as pm
from protobase import frozendict


from ..domain import Id
from .base import Val


class Tuple[*T](Val[tuple[*T]]):
    Empty: _ClassVar[Tuple[tuple[()]]]

    descriptor: pm.Type[tuple[*T]]

    def __getitem__(self, offset: int) -> Val:
        return self.child(_slot_descriptor_at(self.descriptor, offset), self.content[offset])

    def _structural_child_count(self) -> int:
        if isinstance(self.descriptor, pm.UniformType):
            return len(self.content)
        return len(self.content)

    def payload_item_at(self, offset: int) -> pm.Item:
        return pm.Item(
            offset,
            _slot_key_at(self.descriptor, offset),
            _slot_descriptor_at(self.descriptor, offset),
        )

    def attr(self, id: Id) -> Val:
        if not isinstance(self.descriptor, pm.IndexedType):
            raise KeyError(id)
        offset = self.descriptor.index.offset_of(id)
        return self.child(_slot_descriptor_at(self.descriptor, offset), self.content[offset])

    def __contains__(self, value: _Any) -> bool:
        return value in self.content

    @property
    def head(self) -> Val:
        return self[0]

    @property
    def tail(self) -> Self:
        if len(self.content) <= 1:
            return _cast(Self, self._new(pm.VaryingType.Empty, ()))
        descriptor = self.descriptor
        indexed_type = getattr(pm, "IndexedType", None)
        if indexed_type is not None and isinstance(descriptor, indexed_type):
            indexed_descriptor = _cast(_Any, descriptor)
            descriptor = _cast(
                pm.Type[tuple[*T]],
                indexed_type(_tail_inner(indexed_descriptor.inner), indexed_descriptor.index.tail),
            )
        elif isinstance(descriptor, pm.VaryingType):
            descriptor = _cast(pm.Type[tuple[*T]], pm.VaryingType(descriptor.values[1:]))
        return _cast(Self, self._new(descriptor, self.content[1:]))

    def splice(self) -> Self:
        if not any(isinstance(value, pm.Spread) for value in self.content):
            return self
        new_values: list[_Any] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                new_values.extend(value.values)
                continue
            new_values.append(value)
        descriptor = _cast(pm.TupleLikeType, self.descriptor).splice()
        return _cast(Self, self._new(_cast(pm.Type[tuple[*T]], descriptor), tuple(new_values)))

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return _cast(Self, self._new(self.descriptor, tuple(child.fetch() for child in children)))

    def map(self, f) -> Tuple:
        mapped = tuple(f(child) for child in self)
        if not all(isinstance(child, Val) for child in mapped):
            raise TypeError("Tuple.map() callback must return Carrier values")
        carriers = _cast(tuple[Val, ...], mapped)
        if isinstance(self.descriptor, pm.UniformType):
            if not carriers:
                descriptor = _cast(pm.Type[tuple], pm.VaryingType.Empty)
            else:
                first = carriers[0].descriptor
                if all(child.descriptor == first for child in carriers):
                    descriptor = _cast(
                        pm.Type[tuple[*T]],
                        pm.UniformType(first, unique=self.descriptor.unique and len(carriers) == len({child.fetch() for child in carriers})),
                    )
                else:
                    descriptor = _cast(pm.Type[tuple[*T]], pm.VaryingType(tuple(child.descriptor for child in carriers)))
            return _cast(Tuple, self._new(descriptor, tuple(child.fetch() for child in carriers)))
        if isinstance(self.descriptor, pm.IndexedType):
            descriptor = _cast(
                pm.Type[tuple[*T]],
                pm.IndexedType(
                    pm.VaryingType(tuple(child.descriptor for child in carriers)),
                    self.descriptor.index,
                ),
            )
            return _cast(Tuple, self._new(descriptor, tuple(child.fetch() for child in carriers)))
        descriptor = _cast(pm.Type[tuple[*T]], pm.VaryingType(tuple(child.descriptor for child in carriers)))
        return _cast(Tuple, self._new(descriptor, tuple(child.fetch() for child in carriers)))

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
            inner = pm.VaryingType(tuple(v.descriptor for v in all_vals))
            descriptor = pm.IndexedType(inner, Index.of(*keys))
            return cls(descriptor, tuple(v.content for v in all_vals))
        descriptor = pm.VaryingType(tuple(v.descriptor for v in vals))
        return cls(descriptor, tuple(v.content for v in vals))

    @classmethod
    def empty(cls) -> Tuple[tuple[()]]:
        return _cast(Tuple[tuple[()]], cls.Empty)

    @classmethod
    def _new(cls, descriptor: pm.Type[tuple[*T]], content: tuple[_Any, ...]) -> Tuple[*T]:
        return _cast(Tuple[*T], cls(descriptor, content))

    @classmethod
    def extends(cls, *tuples: Tuple) -> Tuple:
        if not tuples:
            return _cast(Tuple, cls.Empty)
        values: list[_Any] = []
        type_values: list[pm.Type] = []
        index_parts: list[pm.Index] = []
        has_index = False
        indexed_type = _cast(_Any, getattr(pm, "IndexedType", None))
        for tuple_ in tuples:
            values.extend(tuple_.content)
            descriptor = tuple_.descriptor
            if indexed_type is not None and isinstance(descriptor, indexed_type):
                indexed_descriptor = _cast(_Any, descriptor)
                has_index = True
                inner = _cast(pm.VaryingType, indexed_descriptor.inner)
                type_values.extend(inner.values)
                index_parts.append(indexed_descriptor.index)
            elif isinstance(descriptor, pm.VaryingType):
                type_values.extend(descriptor.values)
                index_parts.append(Index.of(*((None,) * len(descriptor.values))))
            else:
                raise TypeError(f"Unsupported descriptor for Tuple.extends: {type(descriptor).__name__}")
        combined_type = pm.VaryingType(tuple(type_values))
        if has_index:
            index = Index.concat(*index_parts)
            descriptor = _cast(pm.Type[tuple], indexed_type(_cast(pm.Type, combined_type), index))
        else:
            descriptor = _cast(pm.Type[tuple], combined_type)
        return _cast(Tuple, cls._new(descriptor, tuple(values)))

    def __invariants__(self):
        assert isinstance(self.content, tuple)
        if isinstance(self.descriptor, pm.UniformType):
            return
        if isinstance(self.descriptor, pm.IndexedType):
            expected = len(self.descriptor.index)
        elif isinstance(self.descriptor, pm.VaryingType):
            expected = len(self.descriptor.values)
        else:
            expected = len(self.descriptor)
        assert len(self.content) == expected, "Tuple content must match descriptor length"


def _id_type() -> pm.Type:
    return pm.Spec.of("std.types.Id")


def _optional_id_type() -> pm.Type:
    return _cast(pm.Type, pm.Qual.of(
        pm.Spec.of("std.types.Id"),
        pm.Spec.of("std.qualifiers.Optional"),
    ))


class Index[K : Id](Tuple[*tuple[K | None, ...]]):
    descriptor: pm.UniformType[K | None]
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
        if not any(isinstance(value, pm.Spread) for value in self.content):
            return self
        new_values: list[K | None] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                new_values.extend(_cast(tuple[K | None, ...], value.values))
                continue
            new_values.append(_cast(K | None, value))
        return type(self).of(*new_values)

    @classmethod
    def of(cls, *keys: K | None) -> Index[K]:
        sparse = any(k is None for k in keys)
        element_type = _optional_id_type() if sparse else _id_type()
        return _cast(Index[K], cls(pm.UniformType(element_type, unique=True), keys))
    
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


def _tail_inner(inner: pm.Type) -> pm.Type:
    indexed_type = getattr(pm, "IndexedType", None)
    if isinstance(inner, pm.VaryingType):
        return pm.VaryingType(inner.values[1:])
    if indexed_type is not None and isinstance(inner, indexed_type):
        indexed_inner = _cast(_Any, inner)
        return indexed_type(_tail_inner(indexed_inner.inner), indexed_inner.index.tail)
    return inner


def _slot_descriptor_at(descriptor: pm.Type, offset: int) -> pm.Type:
    if isinstance(descriptor, pm.UniformType):
        return descriptor.element_type
    if isinstance(descriptor, pm.IndexedType):
        return _slot_descriptor_at(descriptor.inner, offset)
    if isinstance(descriptor, pm.VaryingType):
        return _cast(pm.Type, descriptor.values[offset])
    schema = descriptor.schema
    if schema is None:
        raise TypeError(f"{type(descriptor).__name__} has no payload slot descriptors")
    return _cast(pm.Type, schema[offset].fetch())


def _slot_key_at(descriptor: pm.Type, offset: int) -> Id | None:
    if isinstance(descriptor, pm.IndexedType):
        return descriptor.index.key_at(offset)
    return None
