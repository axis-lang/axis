from __future__ import annotations

from typing import Any, Iterator, Sequence, cast, ClassVar

from . import display
from .foundation import Data, Val, Meta
from .index import Index  # , IndexGround
from .schema import Schema, UniformSchema, VaryingSchema


class Tuple[K: Data, V: Data](Val[Schema[K, V], tuple[V, ...]]):

    def __repr__(self) -> str:
        return display.repr_tuple(self)

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
        for i in range(len(self.__data__)):
            yield self.at(i)

    def items(self):
        index = self.index
        if index is None:
            raise KeyError(f"Schema {self.schema!r} has no index for key lookup")
        key_meta = index.key_meta
        for i, key_data in enumerate(index):
            yield key_meta.wrap(key_data), self.at(i)

    def to_dict(self) -> dict:
        return dict(self.items())

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Val, ...]:
        return tuple(self)

    def reconstruct(self, children: tuple[Val, ...]) -> Tuple:
        new_metas = tuple(c.__meta__ for c in children)
        new_data = tuple(c.__data__ for c in children)
        meta_set = frozenset(new_metas)
        if len(meta_set) == 1:
            schema = UniformSchema(
                self.index or UniformSchema.Ground, next(iter(meta_set))
            )
        else:
            schema = VaryingSchema(self.index or VaryingSchema.Ground, new_metas)
        return Tuple(cast(Schema[K, V], schema), new_data)

    def map(self, f) -> Tuple:
        return self.reconstruct(tuple(f(v) for v in self))

    def replace(self, offset: int, val: Val) -> Tuple:
        new_data = self.__data__[:offset] + (val.__data__,) + self.__data__[offset + 1 :]
        schema = self.schema
        if isinstance(schema, VaryingSchema):
            new_metas = (
                schema.__data__[:offset]
                + (val.__meta__,)
                + schema.__data__[offset + 1 :]
            )
            new_schema = VaryingSchema(self.index or VaryingSchema.Ground, new_metas)
        elif isinstance(schema, UniformSchema):
            if val.__meta__ == schema.__data__:
                new_schema = schema
            else:
                new_metas = tuple(
                    schema.at(i) if i != offset else val.__meta__
                    for i in range(len(self.__data__))
                )
                new_schema = VaryingSchema(
                    self.index or VaryingSchema.Ground, new_metas
                )
        else:
            new_schema = schema
        return Tuple(cast(Schema[K, V], new_schema), new_data)

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
        new_index = index.slice(start, stop) if index is not None else None
        if isinstance(schema, UniformSchema):
            new_schema = UniformSchema(
                new_index or UniformSchema.Ground,
                schema.__data__,
            )
        elif isinstance(schema, VaryingSchema):
            new_schema = VaryingSchema(
                new_index or VaryingSchema.Ground,
                schema.__data__[start:stop],
            )
        else:
            new_schema = schema
        return Tuple(cast(Schema[K, V], new_schema), new_data)

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
        return cls(cast(Schema[K, V], schema), tuple(data))

    @classmethod
    def empty(cls) -> Tuple[Any, Any]:
        return cls.Empty

    @staticmethod
    def uniform_of(vals: Sequence[Val], with_index: Index | None = None):
        metas = tuple(val.__meta__ for val in vals)
        data = tuple(val.__data__ for val in vals)
        meta_set = frozenset(metas)

        if len(meta_set) == 1:
            schema = UniformSchema(with_index or UniformSchema.Ground, next(iter(meta_set)))
        else:
            schema = VaryingSchema(with_index or VaryingSchema.Ground, metas)

        return Tuple(cast(Schema[K, V], schema), data)

    @staticmethod
    def varying_of(vals: Sequence[Val], with_index: Index | None = None):
        meta = tuple(val.__meta__ for val in vals)
        data = tuple(val.__data__ for val in vals)
        return Tuple(VaryingSchema(with_index or VaryingSchema.Ground, meta), data)

    @staticmethod
    def of(*args: Val, **kwargs: Val) -> Tuple:
        if kwargs and not args:
            from .index import Index, IndexMeta
            from .hosted import Id

            key_meta = IndexMeta(IndexMeta.Ground, Id)
            index = Index(key_meta, tuple(kwargs.keys()))
            return Tuple.varying_of(list(kwargs.values()), with_index=index)
        elif not kwargs:
            return Tuple.varying_of(list(args))
        else:
            # positional (None key) then keyword
            from .index import Index, IndexMeta
            from .hosted import Id

            key_meta = IndexMeta(IndexMeta.Ground, Id)
            index = Index(key_meta, (None,) * len(args) + tuple(kwargs.keys()))
            return Tuple.varying_of(
                list(args) + list(kwargs.values()), with_index=index
            )

    Empty: ClassVar[Tuple[Any, Any]]


Tuple.Empty = Tuple(VaryingSchema(VaryingSchema.Ground, ()), ())
