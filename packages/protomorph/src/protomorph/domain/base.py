from __future__ import annotations

from itertools import chain as _chain
from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import Iterator as _Iterator
from typing import cast as _cast

import protomorph as pm
from protobase import Consed, flux, frozendict, _


class Id(str):
    """Typed string for field/attribute identifiers."""

    __slots__ = ()


class Anchor(str):
    """Typed string for type system anchor paths (e.g. 'std.types.Text')."""

    __slots__ = ()

    @property
    def name(self) -> Id:
        return self.segments[-1]

    @property
    def segments(self) -> tuple[Id, ...]:
        return tuple(Id(s) for s in self.split("."))

    @property
    def parent(self) -> Anchor | None:
        parts = self.split(".")
        if len(parts) <= 1:
            return None
        return Anchor(".".join(parts[:-1]))

    def child(self, id: Id) -> Anchor:
        return Anchor(f"{self}.{id}")


ALL_BUILTINS: set[type["Builtin"]] = set()


class Builtin(Consed, abstract=True):
    def __repr__(self) -> str:
        from ..display import repr_any

        return repr_any(self)

    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return

        ALL_BUILTINS.add(cls)

        try:
            import protomorph as pm_core  # type: ignore[import-not-found]

            pm_core.NativeRealm.all_builtins.invalidate_for(pm_core.NATIVE_REALM)
        except (AttributeError, ImportError):
            pass


type Datum = (
    int
    | float
    | str
    | bool
    | None
    | tuple[Datum, ...]
    | frozenset[Datum]
    | frozendict[Datum, Datum]
    | Builtin
)


class Type[T](Builtin, abstract=True):
    def metatype(self) -> Type:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def make(self, data: T):
        return pm.make_value(self, data)

    @flux.property
    def schema(self) -> TupleLikeType | None:
        tuple_like_type = globals().get("TupleLikeType")
        if tuple_like_type is not None and isinstance(self, tuple_like_type):
            return _cast(TupleLikeType, self)
        return None

    @property
    def arity(self) -> int | None:
        return 0

    def item_at(self, offset: int) -> pm.Item:
        raise IndexError(offset)

    def item(self, id: Id) -> pm.Item:
        raise KeyError(id)

    def items(self) -> _Iterator[pm.Item]:
        arity = self.arity
        if arity is None:
            return
        for offset in range(arity):
            yield self.item_at(offset)

    def __len__(self) -> int:
        arity = self.arity
        if arity is None:
            raise TypeError(
                f"Unbounded type has no finite length: {type(self).__name__}"
            )
        return arity

    def __iter__(self) -> _Iterator:
        for item in self.items():
            yield item.value


class Placeholder(Type, abstract=True):
    def metatype(self) -> Type:
        return PlaceholderMetatype(self, 1)

    def display_label(self) -> str | None:
        return None


class Var(Placeholder, abstract=True):
    pass


class Mark(Placeholder, abstract=True):
    pass


class WildcardMark(Mark):
    def display_label(self) -> str | None:
        return "_"


class EllipsisMark(Mark):
    def display_label(self) -> str | None:
        return "..."


class SelfMark(Mark):
    def display_label(self) -> str | None:
        return "self"


class PlaceholderMetatype(Placeholder):
    of: Placeholder
    level: int

    def metatype(self) -> Type:
        return type(self)(self.of, self.level + 1)

    def display_label(self) -> str | None:
        base = placeholder_label(self.of)
        if self.level <= 3:
            return base + ("'" * self.level)
        return f"{base}^{self.level}"


class SimpleVar[C: Builtin, I: Datum = str](Var):
    ctx: C | None = None
    id: I = _
    bound: Type = _

    def metatype(self):
        return self.bound

    def display_label(self) -> str:
        return str(self.id)


def var[C: Builtin, I: Datum](
    id: I, bound: Type | _Any, ctx: C | None = None
) -> SimpleVar[C, I]:
    if not isinstance(bound, Type):
        bound = pm.project_type(bound)
    return SimpleVar(id=id, bound=bound, ctx=ctx)


WILDCARD = WildcardMark()
ELLIPSIS = EllipsisMark()
SELF = SelfMark()


def placeholder_name(value: Placeholder) -> str | None:
    ident = getattr(value, "id", None)
    return ident if isinstance(ident, str) else None


def placeholder_context(value: Placeholder) -> _Any | None:
    return getattr(value, "ctx", None)


def placeholder_slot(value: Placeholder) -> int | None:
    slot = getattr(value, "slot", None)
    return slot if isinstance(slot, int) else None


def placeholder_label(value: Placeholder) -> str:
    label_fn = getattr(value, "display_label", None)
    if callable(label_fn):
        label = label_fn()
        if isinstance(label, str):
            return label
    ident = placeholder_name(value)
    if ident is not None:
        return ident
    slot = placeholder_slot(value)
    if slot is not None:
        return str(slot)
    return type(value).__name__


class Spread[V](Builtin):
    values: tuple[V, ...]


class TupleLikeType(Type[tuple], abstract=True):
    def splice(self) -> TupleLikeType:
        return self


class UniformType[T](TupleLikeType):
    element_type: Type[T]
    unique: bool = False

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Uniform", self.element_type.metatype())

    @property
    def arity(self) -> int | None:
        return None

    def item_at(self, offset: int) -> pm.Item:
        return pm.Item(offset, None, self.element_type)


class UnionType[T: tuple[_Any, ...]](Type[T]):
    variants: frozenset[Type]

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Union")

    @classmethod
    def of(cls, *types: Type) -> Type:
        flat: set[Type] = set()
        for tp in types:
            if isinstance(tp, UnionType):
                flat.update(tp.variants)
                continue
            flat.add(tp)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))


class VaryingType[T: tuple[_Any, ...]](TupleLikeType):
    Empty: _ClassVar[VaryingType]

    values: tuple[Type, ...]

    def metatype(self) -> Type:
        return VaryingType(tuple(tp.metatype() for tp in self.values))

    @property
    def arity(self) -> int:
        return len(self.values)

    def item_at(self, offset: int) -> pm.Item:
        return pm.Item(offset, None, self.values[offset])

    def splice(self) -> TupleLikeType:
        if not any(isinstance(value, Spread) for value in self.values):
            return self
        new_values: list[Type] = []
        for value in self.values:
            if isinstance(value, Spread):
                new_values.extend(_cast(tuple[Type, ...], value.values))
                continue
            new_values.append(value)
        return type(self)(tuple(new_values))

    @classmethod
    def of(cls, *args: Type) -> VaryingType:
        normalized = tuple(
            _cast(Type, arg.fetch()) if isinstance(arg, pm.Val) else arg for arg in args
        )
        return cls(normalized)

    @classmethod
    def new(cls, *vals: pm.Val, **kwvals: pm.Val) -> pm.Tuple:
        if kwvals:
            indexed_type = getattr(pm, "IndexedType")
            return pm.Tuple(
                indexed_type.of(
                    *(val.descriptor for val in vals),
                    **{key: value.descriptor for key, value in kwvals.items()},
                ),
                tuple(_chain(vals, kwvals.values())),
            )
        return pm.Tuple(cls.of(*(val.descriptor for val in vals)), tuple(vals))


class IndexedType[T](TupleLikeType):
    inner: Type[T]
    index: pm.Index

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Indexed", self.inner.metatype())

    @property
    def arity(self) -> int:
        return self.index.arity

    def item_at(self, offset: int) -> pm.Item:
        item = self.inner.item_at(offset)
        return pm.Item(offset, self.index.key_at(offset), item.value)

    def item(self, id: Id) -> pm.Item:
        offset = self.index.offset_of(id)
        item = self.inner.item_at(offset)
        return pm.Item(offset, id, item.value)

    def splice(self) -> TupleLikeType:
        inner = _cast(TupleLikeType, self.inner).splice()
        index_values: list[object] = []
        for item in _cast(VaryingType, self.inner).values:
            if isinstance(item, Spread):
                index_values.append(Spread((None,) * len(item.values)))
                continue
            index_values.append(None)
        keyed = list(self.index.content)
        for offset, key in enumerate(keyed):
            if key is not None:
                index_values[offset] = key
        index = pm.Index.of(*_cast(tuple[Id | None, ...], tuple(index_values))).splice()
        if inner.arity is not None and inner.arity != index.arity:
            raise ValueError("IndexedType splice produced mismatched arity")
        return type(self)(_cast(Type, inner), index)

    @classmethod
    def of(cls, *args: Type, **kwargs: Type) -> IndexedType:
        positional = tuple(
            _cast(Type, arg.fetch()) if isinstance(arg, pm.Val) else arg for arg in args
        )
        nominal = {
            key: (_cast(Type, value.fetch()) if isinstance(value, pm.Val) else value)
            for key, value in kwargs.items()
        }
        values = positional + tuple(nominal.values())
        keys = (None,) * len(positional) + tuple(Id(key) for key in nominal)
        return _cast(
            IndexedType, cls(_cast(Type, VaryingType(values)), pm.Index.of(*keys))
        )


class Spec(Type):
    anchor: Anchor
    args: pm.Tuple

    def metatype(self) -> Type:
        return Spec.of("std.metas.Specialization")

    @flux.property
    def schema(self) -> TupleLikeType | None:
        return pm.current_realm().schema_for(self)

    @property
    def arity(self) -> int | None:
        schema = self.schema
        return schema.arity if schema is not None else 0

    def item_at(self, offset: int) -> pm.Item:
        schema = self.schema
        if schema is None:
            raise IndexError(offset)
        return schema.item_at(offset)

    def item(self, id: pm.Id) -> pm.Item:
        schema = self.schema
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    @classmethod
    def of(cls, anchor: Anchor | str, *args: _Any, **kwargs: _Any) -> Spec:
        values = args + tuple(kwargs.values())
        descriptors = tuple(_value_descriptor(value) for value in values)
        indexed_type = _cast(_Any, getattr(pm, "IndexedType"))
        descriptor = (
            indexed_type.of(
                *descriptors[: len(args)],
                **{
                    key: descriptors[len(args) + index]
                    for index, key in enumerate(kwargs)
                },
            )
            if kwargs
            else pm.VaryingType(descriptors)
        )
        tuple_args = _cast(pm.Tuple, pm.Tuple(_cast(Type[tuple], descriptor), values))
        return _cast(Spec, cls(Anchor(anchor), tuple_args))

    @classmethod
    def new(cls, anchor: Anchor | str, *vals: pm.Val, **kwvals: pm.Val) -> Spec:
        return _cast(Spec, cls(Anchor(anchor), pm.VaryingType.new(*vals, **kwvals)))


class Qual(Type):
    underlying: Type
    qualifiers: pm.Tuple

    def metatype(self) -> Type:
        return Spec.of("std.metas.Qualifier")

    @flux.property
    def schema(self) -> TupleLikeType | None:
        return None

    @property
    def arity(self) -> int | None:
        schema = self.schema
        return schema.arity if schema is not None else 0

    def item_at(self, offset: int) -> pm.Item:
        schema = self.schema
        if schema is None:
            raise IndexError(offset)
        return schema.item_at(offset)

    def item(self, id: pm.Id) -> pm.Item:
        schema = self.schema
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    @property
    def last_qualifier(self) -> Spec | None:
        qualifiers = tuple(_cast(Spec, child.fetch()) for child in self.qualifiers)
        if not qualifiers:
            return None
        return qualifiers[-1]

    @property
    def unwrap(self) -> Type:
        qualifiers = tuple(_cast(Spec, child.fetch()) for child in self.qualifiers)
        if len(qualifiers) <= 1:
            return self.underlying
        return _cast(Type, type(self).of(self.underlying, *qualifiers[:-1]))

    @classmethod
    def of(cls, underlying: Type, *qualifiers: Spec) -> Qual:
        if isinstance(underlying, Qual):
            nested = _cast(Qual, underlying)
            return _cast(
                Qual,
                cls(
                    nested.underlying,
                    pm.Tuple.extends(
                        nested.qualifiers, _normalize_tuple_values(tuple(qualifiers))
                    ),
                ),
            )
        return _cast(Qual, cls(underlying, _normalize_tuple_values(tuple(qualifiers))))


def _value_descriptor(value: _Any) -> Type:
    if isinstance(value, pm.Val):
        return value.descriptor
    if isinstance(value, Type):
        return value.metatype()
    return _project_runtime_type(value)


def _project_runtime_type(value: _Any) -> Type:
    return _cast(Type, pm.val(type(value)).fetch())


def _normalize_tuple_values(values: tuple[_Any, ...]) -> pm.Tuple:
    descriptors = tuple(_value_descriptor(value) for value in values)
    return _cast(pm.Tuple, pm.Tuple(pm.VaryingType(descriptors), values))
