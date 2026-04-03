from __future__ import annotations

from typing import Any, Callable, ClassVar, Iterable, Iterator, Self, cast, overload

from protobase import Consed, slot_cached_property

from .base import Builtin
from .map import Map

__all__ = ["Struct"]


class Struct[K, V](Builtin):
    class Shape[SK](Builtin):
        arity: int
        keys: frozenset[SK]

        @classmethod
        def from_index(cls, index: Struct.Index[SK]) -> Self:
            return cls(arity=index.arity, keys=frozenset(index._indexed_keys))

        @property
        def named_count(self) -> int:
            return len(self.keys)

        @property
        def positional_count(self) -> int:
            return self.arity - self.named_count

        @property
        def is_empty(self) -> bool:
            return len(self.keys) == 0

        @property
        def is_named_only(self) -> bool:
            return self.positional_count == 0

        @property
        def is_positional_only(self) -> bool:
            return self.named_count == 0

        @property
        def is_mixed(self) -> bool:
            return self.named_count > 0 and self.positional_count > 0

        @property
        def is_full(self) -> bool:
            return self.arity == len(self.keys)

        @property
        def is_sparse(self) -> bool:
            return not self.is_empty and not self.is_full

        def __invariants__(self):
            assert self.arity >= 0
            assert len(self.keys) <= self.arity

        def __repr__(self) -> str:
            keys = sorted(map(repr, self.keys))
            return f"Shape[{self.arity}] _ = ({', '.join(keys)})"

        def __len__(self) -> int:
            return self.arity

        def __iter__(self) -> Iterator[SK]:
            return iter(self.keys)

        def __contains__(self, key: SK) -> bool:
            return key in self.keys

        def matches(self, index: Struct.Index[SK]) -> bool:
            return self == type(self).from_index(index)

        def accepts(self, index: Struct.Index[SK]) -> bool:
            return self.matches(index)

    class Index[IK](Builtin):
        keys: tuple[IK, ...]

        @classmethod
        def empty(cls) -> Self:
            return cls(())

        @classmethod
        def positional(cls, n: int) -> Struct.Index[None]:
            return Struct.Index((None,) * n)

        @classmethod
        def named(cls, *keys: IK) -> Self:
            return cls(keys)

        @classmethod
        def of(cls, *keys: IK) -> Self:
            return cls(keys)

        def __invariants__(self) -> None:
            assert len(self._keyed_indices) == len(self._indexed_keys), (
                f"Duplicate keys in {self}"
            )

        @property
        def arity(self) -> int:
            return len(self.keys)

        @property
        def named_count(self) -> int:
            return len(self._keyed_indices)

        @property
        def positional_count(self) -> int:
            return self.arity - self.named_count

        @property
        def named_keys(self) -> tuple[IK, ...]:
            return tuple(self._indexed_keys)

        @property
        def named_offsets(self) -> tuple[int, ...]:
            return tuple(self._indexed_keys.keys)

        @slot_cached_property
        def _keyed_indices(self) -> Map[IK, int]:
            return Map.new((k, i) for i, k in enumerate(self.keys) if k is not None)

        @slot_cached_property
        def _indexed_keys(self) -> Map[int, IK]:
            return Map.new((i, k) for i, k in enumerate(self.keys) if k is not None)

        @property
        def is_empty(self) -> bool:
            return len(self.keys) == 0

        @property
        def is_named_only(self) -> bool:
            return self.positional_count == 0

        @property
        def is_positional_only(self) -> bool:
            return self.named_count == 0

        @property
        def is_mixed(self) -> bool:
            return self.named_count > 0 and self.positional_count > 0

        @property
        def is_full(self) -> bool:
            return len(self._keyed_indices) == self.arity

        @property
        def is_sparse(self) -> bool:
            return not self.is_empty and not self.is_full

        @slot_cached_property
        def shape(self) -> Struct.Shape[IK]:
            return Struct.Shape.from_index(self)

        def __repr__(self) -> str:
            keys = ("_" if k is None else repr(k) for k in self.keys)
            return f"Index[{self.arity}] _ = ({', '.join(keys)})"

        def __len__(self) -> int:
            return self.arity

        def __iter__(self) -> Iterator[IK]:
            return iter(self.keys)

        @overload
        def __getitem__(self, offset: int) -> IK: ...

        @overload
        def __getitem__(self, offset: slice) -> Self: ...

        def __getitem__(self, offset: int | slice) -> Any:
            if isinstance(offset, slice):
                return type(self)(self.keys[offset])
            return self.keys[offset]

        def prefix(self, n: int) -> Struct.Index[IK]:
            return self[:n]

        def middle(self, start: int, stop: int | None = None) -> Struct.Index[IK]:
            return self[start:stop]

        def suffix(self, n: int) -> Struct.Index[IK]:
            return self[len(self.keys) - n :] if n else type(self)(())

        def split_at(self, offset: int) -> tuple[Struct.Index[IK], Struct.Index[IK]]:
            return self.prefix(offset), self.middle(offset)

        def split_variadic(
            self,
            prefix_len: int,
            suffix_len: int,
        ) -> tuple[Struct.Index[IK], Struct.Index[IK], Struct.Index[IK]]:
            if prefix_len + suffix_len > self.arity:
                raise ValueError("variadic split exceeds index arity")
            tail_start = self.arity - suffix_len
            return self.prefix(prefix_len), self.middle(prefix_len, tail_start), self.suffix(suffix_len)

        def take_offsets(self, offsets: Iterable[int]) -> Struct.Index[IK]:
            selected = tuple(self.keys[offset] for offset in offsets)
            return type(self)(selected)

        def drop_offsets(self, offsets: Iterable[int]) -> Struct.Index[IK]:
            dropped = set(offsets)
            kept = tuple(key for offset, key in enumerate(self.keys) if offset not in dropped)
            return type(self)(kept)

        def offset_of(self, key: IK, **kwargs):
            return self._keyed_indices.get(key, **kwargs)

        def contains_key(self, key: IK) -> bool:
            return self._keyed_indices.has(key)

        @property
        def get(self):
            return self._keyed_indices.get

        @property
        def has(self):
            return self._keyed_indices.has

    Empty: ClassVar[Struct[Any, Any]]

    index: Index[K]
    values: tuple[V, ...]

    @property
    def arity(self) -> int:
        return len(self.index)

    @property
    def keys(self) -> tuple[K, ...]:
        return self.index.keys

    @property
    def named_keys(self) -> tuple[K, ...]:
        return self.index.named_keys

    @property
    def positional_count(self) -> int:
        return self.index.positional_count

    @property
    def named_count(self) -> int:
        return self.index.named_count

    @property
    def is_named_only(self) -> bool:
        return self.index.is_named_only

    @property
    def is_positional_only(self) -> bool:
        return self.index.is_positional_only

    @property
    def is_mixed(self) -> bool:
        return self.index.is_mixed

    @property
    def shape(self) -> Shape[K]:
        return self.index.shape

    def __invariants__(self):
        assert len(self.index) == len(self.values)

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        def repr_element(k, v):
            if k is None:
                return repr(v)
            return f"{k}={repr(v)}"

        return (
            "(" + ", ".join(repr_element(k, v) for k, v in zip(self.index, self.values)) + ")"
        )

    @staticmethod
    def new[T](*positional: T, **nominal: T) -> Struct[str | None, T]:
        index = Struct.Index((None,) * len(positional) + tuple(nominal.keys()))
        values = positional + tuple(nominal.values())
        return Struct(index, values)

    @classmethod
    def from_index(cls, index: Struct.Index[K], values: tuple[V, ...]) -> Self:
        return cls(index=index, values=values)

    @classmethod
    def from_iter(cls, entries: Iterable[tuple[K, V]]) -> Self:
        items = tuple(entries)
        keys, values = zip(*items) if items else ((), ())
        return cls.from_index(Struct.Index(keys), values)

    @classmethod
    def from_keys(cls, keys: tuple[K, ...], values: tuple[V, ...]) -> Self:
        return cls.from_index(Struct.Index(keys), values)

    def __contains__(self, value: V) -> bool:
        return value in self.values

    @overload
    def __getitem__(self, offset: int) -> V: ...

    @overload
    def __getitem__(self, offset: slice) -> Self: ...

    def __getitem__(self, offset: int | slice) -> Any:
        if isinstance(offset, slice):
            return type(self).from_index(self.index[offset], self.values[offset])
        return self.values[offset]

    @property
    def entries(self) -> tuple[tuple[K, V], ...]:
        return tuple(zip(self.index.keys, self.values))

    @property
    def positional_values(self) -> tuple[V, ...]:
        return tuple(value for key, value in self.entries if key is None)

    def named_items(self) -> tuple[tuple[K, V], ...]:
        return tuple((key, value) for key, value in self.entries if key is not None)

    def named_dict(self) -> dict[K, V]:
        return dict(self.named_items())

    def with_values(self, values: tuple[V, ...]) -> Struct[K, V]:
        return type(self).from_index(self.index, values)

    def with_index(self, index: Struct.Index[K]) -> Struct[K, V]:
        return type(self).from_index(index, self.values)

    def prefix(self, n: int) -> Struct[K, V]:
        return self[:n]

    def middle(self, start: int, stop: int | None = None) -> Struct[K, V]:
        return self[start:stop]

    def suffix(self, n: int) -> Struct[K, V]:
        return self[len(self.values) - n :] if n else type(self).from_keys((), ())

    def split_at(self, offset: int) -> tuple[Struct[K, V], Struct[K, V]]:
        return self.prefix(offset), self.middle(offset)

    def split_variadic(
        self,
        prefix_len: int,
        suffix_len: int,
    ) -> tuple[Struct[K, V], Struct[K, V], Struct[K, V]]:
        if prefix_len + suffix_len > self.arity:
            raise ValueError("variadic split exceeds struct arity")
        tail_start = self.arity - suffix_len
        return self.prefix(prefix_len), self.middle(prefix_len, tail_start), self.suffix(suffix_len)

    def filter_entries(self, pred: Callable[[K, V], bool]) -> Struct[K, V]:
        return type(self).from_iter((key, value) for key, value in self.entries if pred(key, value))

    def take_offsets(self, offsets: Iterable[int]) -> Struct[K, V]:
        selected = tuple(offsets)
        return type(self).from_index(self.index.take_offsets(selected), tuple(self.values[offset] for offset in selected))

    def drop_offsets(self, offsets: Iterable[int]) -> Struct[K, V]:
        dropped = set(offsets)
        kept_offsets = tuple(offset for offset in range(self.arity) if offset not in dropped)
        return self.take_offsets(kept_offsets)

    def as_const(self):
        import protomorph_ as pm

        if not all(isinstance(value, pm.Val) for value in self.values):
            raise TypeError("Struct.as_const requires protomorph values")

        fields = cast("Struct[K, pm.Val]", self)
        return _struct_const(fields)

    @classmethod
    def from_const(cls, value) -> Self | None:
        import protomorph_ as pm

        if not isinstance(value, pm.Const) or not isinstance(value.__type__, pm.StructType):
            return None
        if not isinstance(value.__data__, tuple):
            return None

        fields = tuple(
            field_type._wrap(field_data)
            for field_type, field_data in zip(value.__type__.meta_attrs.values, value.__data__)
        )
        builder = cast(Any, cls)
        return cast(Self, builder.from_keys(value.__type__.meta_attrs.index.keys, fields))

    @overload
    def get(self, key: K) -> V: ...

    @overload
    def get[D](self, key: K, *, default: D) -> V | D: ...

    @overload
    def get[D](self, key: K, *, fallback: Callable[[], D]) -> V | D: ...

    def get(self, key: K, **kwargs):
        if (offset := self.index.get(key, default=None)) is None:
            if "default" in kwargs:
                return kwargs["default"]
            if "fallback" in kwargs:
                return kwargs["fallback"]()
            raise KeyError(f"Key not found: {key}")
        return self.values[offset]

    def map[R](self, func: Callable[[V], R]) -> Struct[K, R]:
        return Struct(index=self.index, values=tuple(func(v) for v in self.values))


Struct.Empty = Struct(Struct.Index(()), ())


def _struct_const(struct: Struct[Any, Any]):
    import protomorph_ as pm

    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for key, value in struct.entries:
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return pm.struct(*positional, **nominal)
