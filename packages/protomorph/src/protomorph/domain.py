from __future__ import annotations

from itertools import chain
from typing import Any, ClassVar, cast

from protobase import flux

import protomorph as pm

from .abstract.contract import Item
from .foundation import Builtin, Id, Anchor
from .realm import current_realm
from .type_ import Type


class Spread[V](Builtin):
    """Sentinel: wraps values to be spliced into a tuple-like parent.

    Like Python's *iterable unpacking — the parent splice() method
    flattens Spread entries into its own values sequence.
    """

    values: tuple[V, ...]


class TupleLikeType(Type[tuple], abstract=True):
    def splice(self) -> TupleLikeType:
        return self


class UniformType[T](TupleLikeType):
    """Homogeneous positional collection."""

    element_type: pm.Type[T]
    unique: bool = False

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Uniform", self.element_type.metatype())

    @property
    def arity(self) -> int | None:
        return None

    def item_at(self, offset: int) -> Item:
        return Item(offset, None, self.element_type)

    def splice(self) -> TupleLikeType:
        return self


class UnionType[T: tuple[Any, ...]](Type[T]):
    """Union of types — leaf in structure, carrier dispatches at runtime."""

    variants: frozenset[pm.Type]

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Union")

    @classmethod
    def of(cls, *types: pm.Type) -> pm.Type:
        """Build a union, flattening nested unions. Returns single type if only one."""
        flat: set[pm.Type] = set()
        for t in types:
            if isinstance(t, UnionType):
                flat.update(t.variants)
            else:
                flat.add(t)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))


class VaryingType[T: tuple[Any, ...]](TupleLikeType):
    """Heterogeneous positional tuple type."""

    Empty: ClassVar[VaryingType]

    values: tuple[pm.Type, ...]

    def metatype(self) -> Type:
        return VaryingType(tuple(t.metatype() for t in self.values))

    @property
    def arity(self) -> int:
        return len(self.values)

    def item_at(self, offset: int) -> Item:
        return Item(offset, None, self.values[offset])

    def splice(self) -> TupleLikeType:
        has_spread = any(isinstance(value, Spread) for value in self.values)
        if not has_spread:
            return self
        new_values: list[pm.Type] = []
        for value in self.values:
            if isinstance(value, Spread):
                for spread_value in value.values:
                    new_values.append(cast(pm.Type, spread_value))
                continue
            new_values.append(value)
        return type(self)(tuple(new_values))

    @classmethod
    def of(cls, *args: pm.Type) -> VaryingType:
        normalized = tuple(
            cast(pm.Type, arg.fetch()) if isinstance(arg, pm.Carrier) else arg
            for arg in args
        )
        return cls(normalized)

    @classmethod
    def new(cls, *vals: pm.Carrier, **kwvals: pm.Carrier) -> pm.Tuple:
        if kwvals:
            indexed_type = getattr(pm, "IndexedType")
            return pm.Tuple(
                indexed_type.of(
                    *(val.descriptor for val in vals),
                    **{k: v.descriptor for k, v in kwvals.items()},
                ),
                tuple(chain(vals, kwvals.values())),
            )
        return pm.Tuple(cls.of(*(val.descriptor for val in vals)), tuple(vals))


class IndexedType[T](TupleLikeType):
    inner: pm.Type[T]
    index: pm.Index

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Indexed", self.inner.metatype())

    @property
    def arity(self) -> int:
        return self.index.arity

    def item_at(self, offset: int) -> Item:
        item = self.inner.item_at(offset)
        return Item(offset, self.index.key_at(offset), item.value)

    def item(self, id: Id) -> Item:
        offset = self.index.offset_of(id)
        item = self.inner.item_at(offset)
        return Item(offset, id, item.value)

    def splice(self) -> TupleLikeType:
        inner = cast(pm.TupleLikeType, self.inner).splice()
        index_values: list[object] = []
        for item in cast(pm.VaryingType, self.inner).values:
            if isinstance(item, Spread):
                spread_len = len(item.values)
                index_values.append(Spread((None,) * spread_len))
            else:
                index_values.append(None)
        keyed = list(self.index.content)
        for offset, key in enumerate(keyed):
            if key is not None:
                index_values[offset] = key
        index = pm.Index.of(*cast(tuple[Id | None, ...], tuple(index_values))).splice()
        if inner.arity is not None and inner.arity != index.arity:
            raise ValueError("IndexedType splice produced mismatched arity")
        return type(self)(cast(pm.Type, inner), index)

    @classmethod
    def of(cls, *args: pm.Type, **kwargs: pm.Type) -> IndexedType:
        positional = tuple(
            cast(pm.Type, arg.fetch()) if isinstance(arg, pm.Carrier) else arg
            for arg in args
        )
        nominal = {
            key: (
                cast(pm.Type, value.fetch()) if isinstance(value, pm.Carrier) else value
            )
            for key, value in kwargs.items()
        }
        values = positional + tuple(nominal.values())
        keys = (None,) * len(positional) + tuple(Id(key) for key in nominal)
        return cast(
            IndexedType, cls(cast(pm.Type, VaryingType(values)), pm.Index.of(*keys))
        )


VaryingType.Empty = VaryingType(())


class Spec(Type):
    anchor: Anchor
    args: pm.Tuple

    def metatype(self) -> pm.Type:
        return Spec.of("std.metas.Specialization")

    @flux.property
    def schema(self) -> pm.TupleLikeType | None:
        return current_realm().schema_for(self)

    @property
    def arity(self) -> int | None:
        schema = self.schema
        return schema.arity if schema is not None else 0

    def item_at(self, offset: int) -> Item:
        schema = self.schema
        if schema is None:
            raise IndexError(offset)
        return schema.item_at(offset)

    def item(self, id: pm.Id) -> Item:
        schema = self.schema
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    @classmethod
    def of(cls, anchor: Anchor | str, *args: Any, **kwargs: Any) -> Spec:
        values = args + tuple(kwargs.values())
        descriptors = tuple(_value_descriptor(value) for value in values)
        indexed_type = cast(Any, getattr(pm, "IndexedType"))
        descriptor = (
            indexed_type.of(
                *descriptors[: len(args)],
                **{k: descriptors[len(args) + i] for i, k in enumerate(kwargs)},
            )
            if kwargs
            else pm.VaryingType(descriptors)
        )
        tuple_args = cast(pm.Tuple, pm.Tuple(cast(pm.Type[tuple], descriptor), values))
        return cast(Spec, cls(Anchor(anchor), tuple_args))

    @classmethod
    def new(
        cls,
        anchor: Anchor | str,
        *vals: pm.Carrier,
        **kwvals: pm.Carrier,
    ) -> Spec:
        return cast(Spec, cls(Anchor(anchor), pm.VaryingType.new(*vals, **kwvals)))


class Qual(Type):
    underlying: pm.Type
    qualifiers: pm.Tuple

    def metatype(self) -> pm.Type:
        return Spec.of("std.metas.Qualifier")

    @flux.property
    def schema(self) -> pm.TupleLikeType | None:
        return None

    @property
    def arity(self) -> int | None:
        schema = self.schema
        return schema.arity if schema is not None else 0

    def item_at(self, offset: int) -> Item:
        schema = self.schema
        if schema is None:
            raise IndexError(offset)
        return schema.item_at(offset)

    def item(self, id: pm.Id) -> Item:
        schema = self.schema
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    @property
    def last_qualifier(self) -> Spec | None:
        qualifiers = tuple(cast(Spec, child.fetch()) for child in self.qualifiers)
        if not qualifiers:
            return None
        return qualifiers[-1]

    @property
    def unwrap(self) -> pm.Type:
        qualifiers = tuple(cast(Spec, child.fetch()) for child in self.qualifiers)
        if len(qualifiers) <= 1:
            return self.underlying
        return cast(pm.Type, type(self).of(self.underlying, *qualifiers[:-1]))

    @classmethod
    def of(cls, underlying: pm.Type, *qualifiers: Spec) -> Qual:
        if isinstance(underlying, Qual):
            nested = cast(Qual, underlying)
            return cast(
                Qual,
                cls(
                    nested.underlying,
                    pm.Tuple.extends(nested.qualifiers, _normalize_tuple_values(tuple(qualifiers))),
                ),
            )
        return cast(Qual, cls(underlying, _normalize_tuple_values(tuple(qualifiers))))


def _value_descriptor(value: Any) -> pm.Type:
    if isinstance(value, pm.Carrier):
        return value.descriptor
    if isinstance(value, pm.Type):
        return value.metatype()
    return _project_runtime_type(value)


def _project_runtime_type(value: Any) -> pm.Type:
    return cast(pm.Type, pm.wrap(type(value)).fetch())


def _normalize_tuple_values(values: tuple[Any, ...]) -> pm.Tuple:
    descriptors = tuple(_value_descriptor(value) for value in values)
    return cast(pm.Tuple, pm.Tuple(pm.VaryingType(descriptors), values))
