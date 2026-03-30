from __future__ import annotations

from typing import Any, Self, Iterator, cast, ClassVar

from protobase import Consed, frozendict

import pm
from .foundation import Id

_RECONSTRUCT = object()


class Carrier[T](Consed, abstract=True):
    descriptor: pm.Type[T]
    content: T

    def __repr__(self) -> str:
        from .display import repr_any

        return repr_any(self)

    def child(self, tp: pm.Type, dt: Any) -> Carrier:
        if isinstance(dt, Carrier):
            return dt
        if isinstance(dt, pm.Placeholder):
            return LeafCarrier(tp, dt)
        if isinstance(dt, pm.Type):
            return dt.metatype().make(dt)
        provider = pm.carrier_factory_for(tp)
        if provider is None:
            raise NotImplementedError(
                f"Custom carrier provider not implemented for {type(tp).__name__}"
            )
        return provider(tp, dt)

    @property
    def type(self) -> Carrier[pm.Type[T]]:
        return NativeObjectCarrier(self.descriptor.metatype(), self.descriptor)

    def fetch(self) -> T:
        return self.content

    def attr(self, id: Id) -> Carrier:
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Carrier:
        raise NotImplementedError(
            f"__getitem__ not implemented for {type(self).__name__}"
        )

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
        raise NotImplementedError(
            f"reconstruct() not implemented for {type(self).__name__}"
        )

    def deep_iter(self, is_leaf=None) -> Iterator[Carrier]:
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
        def _is_leaf(c):
            return c in mapping or c.is_leaf

        return self.deep_map(lambda c: mapping.get(c, c), is_leaf=_is_leaf)

    def search(self, target: Carrier) -> bool:
        stack: list[Carrier] = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(list(node))
        return False


class NativeObjectCarrier[T](Carrier[T]):
    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, getattr(self.content, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        assert field.key is not None
        return self.child(field.value, getattr(self.content, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values = []
        for item, child in zip(self.descriptor.items(), children):
            assert item.key is not None
            original = getattr(self.content, item.key)
            if isinstance(original, Carrier):
                values.append(child)
            else:
                values.append(child.fetch())
        return cast(Self, type(self)(self.descriptor, type(self.content)(*values)))


class LeafCarrier[T](Carrier[T]):
    @property
    def is_leaf(self) -> bool:
        return True

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class Tuple[*T](Carrier[tuple[*T]]):
    Empty: ClassVar[Tuple[tuple[()]]]

    descriptor: pm.Type[tuple[*T]]

    def items(self):
        for i in range(len(self)):
            yield self.descriptor.item_at(i)

    def __getitem__(self, offset: int) -> Carrier:
        field = self.descriptor.item_at(offset)
        return self.child(field.value, self.content[offset])

    def attr(self, id: Id) -> Carrier:
        field = self.descriptor.item(id)
        return self.child(field.value, self.content[field.offset])

    def __contains__(self, value: Any) -> bool:
        return value in self.content

    def __len__(self) -> int:
        a = self.descriptor.arity
        return a if a is not None else len(self.content)

    @property
    def head(self) -> Carrier:
        return self[0]

    @property
    def tail(self) -> Self:
        if len(self.content) <= 1:
            return cast(Self, self._new(pm.VaryingType.Empty, ()))
        descriptor = self.descriptor
        indexed_type = getattr(pm, "IndexedType", None)
        if indexed_type is not None and isinstance(descriptor, indexed_type):
            indexed_descriptor = cast(Any, descriptor)
            descriptor = cast(
                pm.Type[tuple[*T]],
                indexed_type(_tail_inner(indexed_descriptor.inner), indexed_descriptor.index.tail),
            )
        elif isinstance(descriptor, pm.VaryingType):
            descriptor = cast(pm.Type[tuple[*T]], pm.VaryingType(descriptor.values[1:]))
        return cast(Self, self._new(descriptor, self.content[1:]))

    def splice(self) -> Self:
        has_spread = any(isinstance(value, pm.Spread) for value in self.content)
        if not has_spread:
            return self
        new_values: list[Any] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                new_values.extend(value.values)
            else:
                new_values.append(value)
        descriptor = cast(pm.TupleLikeType, self.descriptor).splice()
        return cast(Self, self._new(cast(pm.Type[tuple[*T]], descriptor), tuple(new_values)))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        values = [child.fetch() for child in children]
        return cast(Self, self._new(self.descriptor, tuple(values)))

    @classmethod
    def _new(cls, descriptor: pm.Type[tuple[*T]], content: tuple[Any, ...]) -> Tuple[*T]:
        return cast(Tuple[*T], cls(descriptor, content))

    @classmethod
    def extends(cls, *tuples: Tuple) -> Tuple:
        if not tuples:
            return cast(Tuple, cls._new(pm.VaryingType.Empty, ()))
        values: list[Any] = []
        type_values: list[pm.Type] = []
        index_parts: list[pm.Index] = []
        has_index = False
        indexed_type = cast(Any, getattr(pm, "IndexedType", None))
        for tuple_ in tuples:
            values.extend(tuple_.content)
            descriptor = tuple_.descriptor
            if indexed_type is not None and isinstance(descriptor, indexed_type):
                indexed_descriptor = cast(Any, descriptor)
                has_index = True
                inner = cast(pm.VaryingType, indexed_descriptor.inner)
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
            descriptor = cast(pm.Type[tuple], indexed_type(cast(pm.Type, combined_type), index))
        else:
            descriptor = cast(pm.Type[tuple], combined_type)
        return cast(Tuple, cls._new(descriptor, tuple(values)))

    def __invariants__(self):
        assert isinstance(self.content, tuple)
        arity = self.descriptor.arity
        if arity is not None:
            assert len(self.content) == arity, "Tuple content must match descriptor arity"


class Index(Tuple):
    descriptor: pm.UniformType[Id | None]
    content: tuple[Id | None, ...]

    @property
    def arity(self) -> int:
        return len(self.content)

    @property
    def is_sparse(self) -> bool:
        return self.arity > 0 and any(key is None for key in self.content)

    @property
    def keys(self) -> tuple[Id | None, ...]:
        return self.content

    @property
    def offsets(self) -> frozendict[Id, int]:
        return frozendict(
            {
                key: offset
                for offset, key in enumerate(self.content)
                if key is not None
            }
        )

    def key_at(self, offset: int) -> Id | None:
        return self.content[offset]

    def offset_of(self, id: Id) -> int:
        return self.offsets[id]

    def splice(self) -> Index:
        has_spread = any(isinstance(value, pm.Spread) for value in self.content)
        if not has_spread:
            return self
        new_values: list[Id | None] = []
        for value in self.content:
            if isinstance(value, pm.Spread):
                spread_values = cast(tuple[Id | None, ...], value.values)
                new_values.extend(spread_values)
            else:
                new_values.append(cast(Id | None, value))
        return type(self).of(*new_values)

    @classmethod
    def of(cls, *keys: Id | None) -> Index:
        return cast(Index, cls(pm.UniformType(_index_key_type(), unique=True), keys))

    @classmethod
    def concat(cls, *indices: Index) -> Index:
        values: list[Id | None] = []
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
        indexed_inner = cast(Any, inner)
        return indexed_type(_tail_inner(indexed_inner.inner), indexed_inner.index.tail)
    return inner


def _index_key_type() -> pm.Type:
    return pm.UnionType.of(pm.Spec.of("std.types.Id"), pm.Spec.of("std.types.Empty"))
