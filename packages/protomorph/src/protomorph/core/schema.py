from __future__ import annotations

from typing import Any, Iterator, cast, ClassVar

from .foundation import Data, Val, Meta, OMEGA, Omega, Ground, ground
from .index import Index  # , IndexGround


class Schema[K: Data, D: Data](Meta[Index[K] | Ground, D]):

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


class UniformSchema[K: Data](Schema[K, Meta]):
    @property
    def arity(self) -> int | None:
        index = self.index
        return index and index.arity

    def at(self, offset: int) -> Meta:
        return self.__data__

    @property
    def fields(self) -> Iterator[Meta]:
        arity = self.arity
        if arity is None:
            raise TypeError("UniformSchema without index has no finite fields")
        for _ in range(arity):
            yield self.__data__

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Meta, ...]:
        return (self.__data__,)

    def reconstruct(self, children: tuple[Val, ...]) -> UniformSchema:
        (meta,) = children
        # assert isinstance(meta, Meta)
        return UniformSchema(self.__meta__, cast(Meta, meta))

    @classmethod
    def of(cls, meta: Meta, index: Index | None = None) -> UniformSchema:
        return cls(index or cls.Ground, meta)

    Ground: ClassVar[Ground]


class VaryingSchema[K: Data](Schema[K, tuple[Meta, ...]]):
    @property
    def arity(self) -> int:
        return len(self.__data__)

    def at(self, offset: int) -> Meta:
        return self.__data__[offset]

    @property
    def fields(self) -> Iterator[Meta]:
        return iter(self.__data__)

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return False

    def children(self) -> tuple[Meta, ...]:
        return self.__data__

    def reconstruct(self, children: tuple[Val, ...]) -> VaryingSchema:
        return VaryingSchema(self.__meta__, cast(tuple[Meta, ...], children))

    @classmethod
    def of(cls, *metas: Meta, index: Index | None = None) -> VaryingSchema:
        return cls(index or cls.Ground, metas)

    def __invariants__(self) -> None:
        index = self.index
        if index is not None:
            assert index.arity == self.arity

    Ground: ClassVar[Ground]



UniformSchema.Ground = ground(UniformSchema)
VaryingSchema.Ground = ground(VaryingSchema)
