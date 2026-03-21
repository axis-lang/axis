# %%
from __future__ import annotations
from typing import ClassVar, Any, Iterator, Self, Sequence

from protobase import Consed, frozendict, slot_cached_property


# ── Foundation ──────────────────────────────────────────────────────────


class Builtin(Consed):
    pass


# type Payload[P: Meta | Data] = P | tuple[P, ...] | frozenset[P] | frozendict[P, P]

type Discriminant = Meta

type Data = (
    int
    | str
    | float
    | bool
    | None
    | Builtin
    | Discriminant
    | tuple["Data", ...]
    | frozenset["Data"]
    | frozendict["Data", "Data"]
    | frozendict[Discriminant, "Data"]
)


class Pure[M: Meta = Any, D: Data = Any](Builtin, abstract=True):
    __meta__: M
    __data__: D


class Val[M: Meta = Any, D: Data = Any](Pure[M, D], abstract=True):

    @property
    def ground(self) -> Meta:
        m = self.__meta__
        while not (m is GROUND or isinstance(m, Anchor)):
            m = m.__meta__
        return m

    def meta_chain(self) -> Iterator[Meta]:
        m = self.__meta__
        while m is not GROUND:
            yield m
            m = m.__meta__
        yield GROUND

    def restructure(self, f) -> Self:
        def _walk(meta: Meta) -> Meta:
            result = f(meta)
            if result is not meta:
                return result
            if meta is GROUND:
                return meta
            return meta.__class__(_walk(meta.__meta__), meta.__data__)

        return self.__class__(_walk(self.__meta__), self.__data__)


class Meta[M: Meta = Any, D: Data = Any](Val[M, D], abstract=True):
    Carrier: ClassVar[type[Val] | None] = None

    def wrap(self, data: Data) -> Val:
        carrier = self.Carrier
        if carrier is None:
            raise NotImplementedError(f"Meta {self!r} has no Carrier")
        return carrier(self, data)

    def accepts(self, data: Data) -> bool:
        try:
            self.wrap(data)
            return True
        except (TypeError, ValueError, AssertionError, NotImplementedError):
            return False

    def is_subtype(self, other: Meta) -> bool:
        if self is other or self == other:
            return True
        if isinstance(other, Union):
            if isinstance(self, Union):
                return self.variants <= other.variants
            return self in other.variants
        return False


# ── Omega ─────────────────────────────────────────────────────────


class Ground(Meta["Ground", None]):
    def __repr__(self) -> str:
        return "Ground"


GROUND = object.__new__(Ground)
object.__setattr__(GROUND, "__meta__", GROUND)
object.__setattr__(GROUND, "__data__", None)
object.__setattr__(GROUND, "__hash_cache__", hash((id(GROUND), None)))
GROUND.__consign__[(GROUND, None)] = GROUND

# ── Anchor ─────────────────────────────────────────────────────────


class Single[M: Meta, D: Data](Val[M, D]): ...


class Anchor[A: Data = Any](Meta[Ground, A]):
    def native[N: Data](self, payload: N) -> Single[Self, N]:
        return Single(self, payload)

    def __call__[P: Data](self, payload: P) -> Single[Self, P]:
        return Single(self, payload)


Anchor.Carrier = Single

DEFAULT_ANCHOR = Anchor(GROUND, None)


# ── Variant ───────────────────────────────────────────────────────────

type UnionGround = Ground | Anchor


class Union(Meta[UnionGround, frozenset[Meta]], abstract=True):
    @property
    def variants(self) -> frozenset[Meta]:
        return self.__data__

    def __repr__(self):
        return " | ".join(repr(v) for v in self.variants)

    def __invariants__(self):
        assert len(self.variants) > 1, "Union must have at least two variants"
        assert all(
            v is not GROUND and not isinstance(v, Anchor) for v in self.variants
        ), f"Union variants cannot be Ground or Anchor: {self.variants!r}"

    @classmethod
    def of(cls, *metas: Meta) -> Union:
        return cls(GROUND, frozenset(metas))

    def contains(self, meta: Meta) -> bool:
        return meta in self.variants

    def inject(self, val: Val) -> Variant:
        if val.__meta__ not in self.variants:
            raise ValueError(
                f"Value meta {val.__meta__!r} is not a variant of this union: {self.variants!r}"
            )
        return Variant(self, frozendict({val.__meta__: val.__data__}))


class Variant[T: Data](Val[Union, frozendict[Discriminant, T]]):
    def is_(self, meta: Meta) -> bool:
        return meta in self.__data__

    @property
    def active(self) -> Val:
        (meta, data), = self.__data__.items()
        return meta.wrap(data)

    @property
    def discriminant(self) -> Meta:
        (meta,) = self.__data__.keys()
        return meta

    def project(self, meta: Meta) -> Val | None:
        if meta in self.__data__:
            return meta.wrap(self.__data__[meta])
        return None

    def map_active(self, f) -> Variant:
        new_val = f(self.active)
        return self.__meta__.inject(new_val)

    def __invariants__(self) -> None:
        assert (
            len(self.__data__) == 1
        ), f"Variant must have exactly one active meta: {self.__data__!r}"
        assert all(
            act in self.__meta__.variants for act in self.__data__.keys()
        ), f"Variant meta {self.__meta__!r} must include active meta: {self.__data__.keys()!r}"


Union.Carrier = Variant


# ── Indexing ─────────────────────────────────────────────────────────

type IndexGround = Ground | Anchor


class IndexKeyMeta[Km: Meta = Any](Meta[IndexGround, Km]):
    @property
    def index_key_meta(self) -> Km:
        return self.__data__


class Index[K: Data](Meta[IndexKeyMeta, tuple[K, ...]]):

    @property
    def arity(self) -> int:
        return len(self.__data__)

    @slot_cached_property
    def keys(self) -> tuple[K, ...]:
        return tuple(data for data in self.__data__ if data is not None)

    @slot_cached_property
    def key_offsets(self) -> frozendict[K, int]:
        return frozendict(
            {data: i for i, data in enumerate(self.__data__) if data is not None}
        )

    def __invariants__(self) -> None:
        if len(self.keys) != len(self.key_offsets):
            raise AssertionError(f"Index keys must be unique: {self.__data__!r}")

    def __iter__(self):
        return iter(self.__data__)

    @property
    def key_meta(self) -> Meta:
        return self.__meta__.__data__

    def _offset_of(self, key: K) -> int:
        return self.key_offsets[key]

    def offset_of(self, k: Val[Meta, K]) -> int:
        if k.__meta__ != self.__meta__.index_key_meta:
            raise KeyError(
                f"Key meta {k.__meta__!r} does not match index key meta {self.__meta__.index_key_meta!r}"
            )
        return self._offset_of(k.__data__)

    def concat(self, other: Index) -> Index:
        if self.__meta__ != other.__meta__:
            raise ValueError(
                f"Cannot concat indices with different key metas: "
                f"{self.key_meta!r} vs {other.key_meta!r}"
            )
        return Index(self.__meta__, self.__data__ + other.__data__)

    @classmethod
    def from_vals(cls, vals: Sequence[Val]) -> Index:
        meta = frozenset(val.__meta__ for val in vals)
        if len(meta) == 1:
            key_meta = next(iter(meta))
            data = tuple(val.__data__ for val in vals)
        else:
            key_meta = Union(GROUND, meta)
            data = tuple(key_meta.inject(val).__data__ for val in vals)
        return cls(IndexKeyMeta(GROUND, key_meta), data)


IndexKeyMeta.Carrier = Index


# ── Uniformity / Varying ─────────────────────────────────────────────────────────

type SchemaGround = IndexGround | Index


class Schema[K, V](Meta[SchemaGround, Any]):

    @property
    def index(self) -> Index | None:
        if isinstance(self.__meta__, Index):
            return self.__meta__

    @property
    def arity(self) -> int | None:
        raise NotImplementedError

    def at(self, offset: int) -> Meta:
        raise NotImplementedError

    @property
    def fields(self) -> Iterator[Meta]:
        raise NotImplementedError


class Tuple[K, V](Val[Schema[K, V], Any]):
    @property
    def schema(self) -> Schema[K, V]:
        return self.__meta__

    @property
    def index(self) -> Index | None:
        return self.schema.index

    @property
    def arity(self) -> int:
        return len(self.__data__)

    def __invariants__(self) -> None:
        schema = self.schema
        if schema is not None and schema.arity is not None:
            assert schema.arity == self.arity

    def at(self, offset: int):
        return self.schema.at(offset).wrap(self.__data__[offset])

    def get(self, key: Val):
        index = self.index
        if index is None:
            raise KeyError(f"Schema {self.schema!r} has no index for key lookup")
        return self.at(index.offset_of(key))

    def __getitem__(self, offset: int):
        return self.at(offset)

    def __len__(self):
        return len(self.__data__)

    def __iter__(self):
        for i, d in enumerate(self.__data__):
            yield self.schema.at(i).wrap(d)

    def items(self):
        index = self.index
        if index is None:
            raise KeyError(f"Schema {self.schema!r} has no index for key lookup")
        key_meta = index.key_meta
        for i, key_data in enumerate(index):
            yield key_meta.wrap(key_data), self.schema.at(i).wrap(self.__data__[i])

    def to_dict(self) -> dict:
        return dict(self.items())

    def map(self, f) -> Tuple:
        new_vals = tuple(f(v) for v in self)
        new_metas = tuple(v.__meta__ for v in new_vals)
        new_data = tuple(v.__data__ for v in new_vals)
        ground = self.index or GROUND
        meta_set = frozenset(new_metas)
        if len(meta_set) == 1:
            schema = UniformSchema(ground, next(iter(meta_set)))
        else:
            schema = VaryingSchema(ground, new_metas)
        return Tuple(schema, new_data)

    def replace(self, offset: int, val: Val) -> Tuple:
        new_data = self.__data__[:offset] + (val.__data__,) + self.__data__[offset + 1:]
        schema = self.schema
        if isinstance(schema, VaryingSchema):
            new_metas = schema.__data__[:offset] + (val.__meta__,) + schema.__data__[offset + 1:]
            new_schema = VaryingSchema(schema.__meta__, new_metas)
        elif isinstance(schema, UniformSchema):
            if val.__meta__ == schema.__data__:
                new_schema = schema
            else:
                new_metas = tuple(
                    schema.at(i) if i != offset else val.__meta__
                    for i in range(len(self.__data__))
                )
                new_schema = VaryingSchema(schema.__meta__, new_metas)
        else:
            new_schema = schema
        return Tuple(new_schema, new_data)

    def replace_key(self, key: Val, val: Val) -> Tuple:
        index = self.index
        if index is None:
            raise KeyError(f"Schema {self.schema!r} has no index for key lookup")
        return self.replace(index.offset_of(key), val)

    def slice(self, start: int, stop: int | None = None) -> Tuple:
        if stop is None:
            stop = self.arity
        new_data = self.__data__[start:stop]
        schema = self.schema
        index = self.index
        new_index = None
        if index is not None:
            new_index = Index(index.__meta__, index.__data__[start:stop])
        ground = new_index or GROUND
        if isinstance(schema, UniformSchema):
            new_schema = UniformSchema(ground, schema.__data__)
        elif isinstance(schema, VaryingSchema):
            new_schema = VaryingSchema(ground, schema.__data__[start:stop])
        else:
            new_schema = schema
        return Tuple(new_schema, new_data)

    @classmethod
    def from_dict(cls, index: Index, d: dict) -> Tuple:
        key_meta = index.key_meta
        data = []
        metas = []
        for key_data in index:
            key_val = key_meta.wrap(key_data)
            field_val = d[key_val]
            data.append(field_val.__data__)
            metas.append(field_val.__meta__)
        meta_set = frozenset(metas)
        if len(meta_set) == 1:
            schema = UniformSchema(index, next(iter(meta_set)))
        else:
            schema = VaryingSchema(index, tuple(metas))
        return cls(schema, tuple(data))

    @classmethod
    def empty(cls) -> Tuple:
        return cls(VaryingSchema(GROUND, ()), ())


Schema.Carrier = Tuple


class UniformSchema[Fm: Meta, G: SchemaGround](Schema[G, Fm]):
    @property
    def arity(self) -> int | None:
        index = self.index
        return index and index.arity

    def at(self, offset: int) -> Fm:
        return self.__data__

    @property
    def fields(self) -> Iterator[Fm]:
        arity = self.arity
        if arity is None:
            raise TypeError("UniformSchema without index has no finite fields")
        for _ in range(arity):
            yield self.__data__

    @classmethod
    def of(cls, meta: Meta, index: Index | None = None) -> UniformSchema:
        return cls(index or GROUND, meta)


class VaryingSchema[Fm: Meta, G: SchemaGround](Schema[G, tuple[Fm, ...]]):
    @property
    def arity(self) -> int:
        return len(self.__data__)

    def at(self, offset: int) -> Fm:
        return self.__data__[offset]

    @property
    def fields(self) -> Iterator[Fm]:
        return iter(self.__data__)

    @classmethod
    def of(cls, *metas: Meta, index: Index | None = None) -> VaryingSchema:
        return cls(index or GROUND, metas)

    def __invariants__(self) -> None:
        index = self.index
        if index is not None:
            assert index.arity == self.arity


# ── Native ───────────────────────────────────────────────────────────


class NativeDescriptor(Builtin):
    """ """


class Native(Meta[Ground | Anchor, NativeDescriptor]): ...


# ── Ref ──────────────────────────────────────────────────────────────


class Ref(Meta[Anchor, tuple]):
    @property
    def ref_anchor(self) -> Anchor:
        return self.__meta__

    @property
    def ref_spec(self) -> tuple:
        return self.__data__

    def wrap(self, data: Data) -> Val:
        raise NotImplementedError(
            f"Ref {self.ref_anchor!r} requires a backend to wrap values"
        )


# ── Constructors ─────────────────────────────────────────────────────


def anchor[P: Data](payload: P) -> Anchor[P]:
    if payload is None:
        return DEFAULT_ANCHOR  # type: ignore
    else:
        return Anchor(GROUND, payload)


def union_of(meta: Sequence[Meta]) -> Union:
    return Union(GROUND, frozenset(meta))


def index_of(vals: Sequence[Val]) -> Index:
    return Index.from_vals(vals)


def uniform_tuple_of(vals: Sequence[Val], with_index: Index | None = None):
    meta = frozenset(val.__meta__ for val in vals)

    if len(meta) == 1:
        meta = next(iter(meta))
        data = tuple(val.__data__ for val in vals)
    else:
        meta = Union(GROUND, meta)
        data = tuple(meta.inject(val).__data__ for val in vals)

    return Tuple(UniformSchema(with_index or GROUND, meta), data)


def varying_tuple_of(vals: Sequence[Val], with_index: Index | None = None):
    meta = tuple(val.__meta__ for val in vals)
    data = tuple(val.__data__ for val in vals)
    return Tuple(VaryingSchema(with_index or GROUND, meta), data)


def with_anchor(val: Val, anch: Data) -> Val:
    def _reanchor(meta: Meta) -> Meta:
        if meta is GROUND or isinstance(meta, Anchor):
            return Anchor(GROUND, anch)
        return meta

    return val.restructure(_reanchor)


if __name__ == "__main__":
    Text = anchor("std.Text")
    Id = anchor("std.Id")
    Nat = anchor("std.Natural")

    IndexKeyMeta(GROUND, Id)

    Id("a")
    Id("b")

    idx = index_of([Id("a"), Id("b")])
    u = uniform_tuple_of([Nat(5), Text(10)], with_index=idx)
    v = varying_tuple_of([Nat(5), Text(10)], with_index=idx)
    s = varying_tuple_of([Nat(5), Text(10)])
    print(u)
    print(v)
    print(s)

    def chainscan(x: Pure):
        print(f"==== Chain Scan for {x.__class__.__qualname__} ====")
        while x is not GROUND:
            print(x.__meta__)
            print(x.__data__)
            x = x.__meta__
            print(f"---- {x.__class__.__qualname__} ----")

    chainscan(with_anchor(s, "my_anchor"))
