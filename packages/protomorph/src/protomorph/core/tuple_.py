from __future__ import annotations

from typing import Any, Iterator, cast, ClassVar

from .foundation import (
    Data,
    Val,
    Meta,
    OMEGA,
    Omega,
    Ground,
    ground,
    Builtin,
)
from .variant import Union
from .index import Index  # , IndexGround
from .schema import Schema, UniformSchema, VaryingSchema


class Tuple[K: Data, V: Data](Val[Schema[K, V], tuple[V, ...]]):

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

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Val, ...]:
        return tuple(self)

    def reconstruct(self, children: tuple[Val, ...]) -> Tuple:
        new_metas = tuple(c.__meta__ for c in children)
        new_data = tuple(c.__data__ for c in children)
        ground = self.index or OMEGA
        meta_set = frozenset(new_metas)
        if len(meta_set) == 1:
            schema = UniformSchema(UniformSchema.Ground, next(iter(meta_set)))
        else:
            schema = VaryingSchema(VaryingSchema.Ground, new_metas)
        return Tuple(schema, new_data)

    def map(self, f) -> Tuple:
        return self.reconstruct(tuple(f(v) for v in self))

    def replace(self, offset: int, val: Val) -> Tuple:
        new_data = (
            self.__data__[:offset] + (val.__data__,) + self.__data__[offset + 1 :]
        )
        schema = self.schema
        if isinstance(schema, VaryingSchema):
            new_metas = (
                schema.__data__[:offset]
                + (val.__meta__,)
                + schema.__data__[offset + 1 :]
            )
            new_schema = VaryingSchema(VaryingSchema.Ground, new_metas)
        elif isinstance(schema, UniformSchema):
            if val.__meta__ == schema.__data__:
                new_schema = schema
            else:
                new_metas = tuple(
                    schema.at(i) if i != offset else val.__meta__
                    for i in range(len(self.__data__))
                )
                new_schema = VaryingSchema(VaryingSchema.Ground, new_metas)
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
        ground = new_index or OMEGA
        if isinstance(schema, UniformSchema):
            new_schema = UniformSchema(
                UniformSchema.Ground,
                schema.__data__,
            )
        elif isinstance(schema, VaryingSchema):
            new_schema = VaryingSchema(
                VaryingSchema.Ground,
                schema.__data__[start:stop],
            )
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
    def empty(cls) -> Tuple[Any, Any]:
        return cls.Empty

    @staticmethod
    def uniform_of(vals: Sequence[Val], with_index: Index | None = None):
        meta = frozenset(val.__meta__ for val in vals)

        if len(meta) == 1:
            meta = next(iter(meta))
            data = tuple(val.__data__ for val in vals)
        else:
            meta = Union(OMEGA, meta)
            data = tuple(meta.inject(val).__data__ for val in vals)

        return Tuple(UniformSchema(with_index or UniformSchema.Ground, meta), data)

    @staticmethod
    def varying_of(vals: Sequence[Val], with_index: Index | None = None):
        meta = tuple(val.__meta__ for val in vals)
        data = tuple(val.__data__ for val in vals)
        return Tuple(VaryingSchema(with_index or VaryingSchema.Ground, meta), data)

    # @staticmethod
    # def of(*args: Val, **kwargs: Val) -> Tuple[str, Any]:
    #     vals = (*args, *kwargs.values())
    #     keys = (None,) * len(args) + tuple(kwargs.keys())
    #     return Tuple.varying_of(vals, with_index=Index.from_vals(kwargs.values()))

    Empty: ClassVar[Tuple[Any, Any]]


Tuple.Empty = Tuple(VaryingSchema(VaryingSchema.Ground, ()), ())
