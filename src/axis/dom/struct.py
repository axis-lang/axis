# %%
from __future__ import annotations

from typing import Any, Callable, ClassVar, Iterator, overload

from protobase import Consed, cached_property

from axis.dom.map import Map

__all__ = ["Struct"]

class Struct[K, V](Consed):
    class Shape[SK](Consed):
        """
        def Shape[arity] K

        Se utiliza para determinar igualdad debil y para hacer dispatch por sobrecarga.
        """

        arity: int  # Whole
        keys: frozenset[SK]  # Set K

        @property
        def is_empty(self) -> bool:
            return len(self.keys) == 0

        @property
        def is_full(self) -> bool:
            return self.arity == len(self.keys)

        @property
        def is_sparse(self) -> bool:
            return not self.is_empty and not self.is_full

        def __invariants__(self):
            """Invariant: arity >= 0 and keys ⊆ [0..arity)."""
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

    class Index[IK](Consed):
        """
        def Index[K] Whole
        Index[K]('a', 'b', None, 'x', 'y')
        """

        keys: tuple[IK | None, ...]  # Set[sparse=True] K

        def __invariants__(self) -> None:
            """Invariant: keyed indices are unique and consistent."""
            assert len(self._keyed_indices) == len(
                self._indexed_keys
            ), f"Duplicate keys in {self}"

        @property
        def arity(self) -> int:
            return len(self.keys)

        @cached_property
        def _keyed_indices(self) -> Map[IK, int]:  # Map[K] Whole
            return Map.new((k, i) for i, k in enumerate(self.keys) if k is not None)

        @cached_property
        def _indexed_keys(self) -> Map[int, IK]:  # Map[Whole] K
            return Map.new((i, k) for i, k in enumerate(self.keys) if k is not None)

        @property
        def is_empty(self) -> bool:
            return len(self.keys) == 0

        @property
        def is_full(self) -> bool:
            return len(self._keyed_indices) == self.arity

        @property
        def is_sparse(self) -> bool:
            return not self.is_empty and not self.is_full

        @cached_property
        def shape(self) -> "Struct.Shape[IK]":  # Shape[arity] K
            return Struct.Shape(arity=self.arity, keys=frozenset(self._indexed_keys))

        def __repr__(self) -> str:
            keys = ('_' if k is None else repr(k) for k in self.keys)
            return f"Index[{self.arity}] _ = ({', '.join(keys)})"

        def __len__(self) -> int:
            return self.arity

        def __iter__(self) -> Iterator[IK | None]:
            return iter(self.keys)

        def __getitem__(self, offset: int) -> IK | None:
            return self.keys[offset]

        @property
        def get(self):
            return self._keyed_indices.get

        @property
        def has(self):
            return self._keyed_indices.has

    index: Index[K]  # Index[L] K
    values: tuple[V, ...]  # inner representation

    @property
    def arity(self) -> int:
        return len(self.index)

    @property
    def shape(self) -> Shape[K]:  # Shape[arity] K
        return self.index.shape

    def __invariants__(self):
        """Invariant: index keys and values share the same arity."""
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
            "("
            + ", ".join(repr_element(k, v) for k, v in zip(self.index, self.values))
            + ")"
        )

    @staticmethod
    def new[T](*positional: T, **nominal: T) -> Struct[str, T]:
        index = Struct.Index((None,) * len(positional) + tuple(nominal.keys()))
        values = positional + tuple(nominal.values())
        return Struct(index, values)

    @classmethod
    def from_index(
        cls, index: "Struct.Index[K]", values: tuple[V, ...]
    ) -> "Struct[K, V]":
        return Struct(index=index, values=values)

    @classmethod
    def from_keys(
        cls, keys: tuple[K | None, ...], values: tuple[V, ...]
    ) -> "Struct[K, V]":
        return Struct.from_index(Struct.Index(keys), values)

    EMPTY: ClassVar["Struct[Any, Any]"]

    def __contains__(self, value: V) -> bool:
        return value in self.values

    def __getitem__(self, offset: int) -> V:
        return self.values[offset]

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

    def map[R](self, func: Callable[[V], R]) -> "Struct[K, R]":
        return Struct(
            index=self.index,
            values=tuple(func(v) for v in self.values),
        )


Struct.EMPTY = Struct(Struct.Index(()), ())
