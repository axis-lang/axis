from __future__ import annotations

from typing import Sequence

from .foundation import Data, Val, Meta, OMEGA
from .variant import Union
from .index import IndexKeyMeta, Index
from .schema import UniformSchema, VaryingSchema


def union_of(meta: Sequence[Meta]) -> Union:
    return Union(OMEGA, frozenset(meta))


def index_of(vals: Sequence[Val]) -> Index:
    return Index.from_vals(vals)


def uniform_tuple_of(vals: Sequence[Val], with_index: Index | None = None):
    meta = frozenset(val.__meta__ for val in vals)

    if len(meta) == 1:
        meta = next(iter(meta))
        data = tuple(val.__data__ for val in vals)
    else:
        meta = Union(OMEGA, meta)
        data = tuple(meta.inject(val).__data__ for val in vals)

    return Tuple(UniformSchema(with_index or OMEGA, meta), data)


def varying_tuple_of(vals: Sequence[Val], with_index: Index | None = None):
    meta = tuple(val.__meta__ for val in vals)
    data = tuple(val.__data__ for val in vals)
    return Tuple(VaryingSchema(with_index or OMEGA, meta), data)

