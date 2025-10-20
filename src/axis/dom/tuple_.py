# %%
from __future__ import annotations
from typing import Any, Callable, ClassVar, Iterator, overload
from protobase import Record, cached_property, classproperty
from axis.dom.map import Map

class Shape[K](Record, frozen=True, consed=True):
    """
    def Shape[arity] K

    Se utiliza para determinar igualdad debil y para hacer dispatch por sobrecarga.
    """

    arity: int  # Whole
    keys: frozenset[K]  # Set K

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
        assert self.arity >= 0
        assert len(self.keys) <= self.arity

    def __repr__(self) -> str:
        keys = sorted(map(repr, self.keys))
        return f"Shape[{self.arity}] _ = ({', '.join(keys)})"

    def __len__(self) -> int:
        return self.arity

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys)

    def __contains__(self, key: K) -> bool:
        return key in self.keys


class Index[K](Record, frozen=True, consed=True):
    """
    def Index[K] Whole
    Index[K]('a', 'b', None, 'x', 'y')
    """

    keys: tuple[K | None, ...]  # Set[sparse=True] K

    def __invariants__(self) -> None:
        # Check for duplicate keys
        assert len(self._keyed_indices) == len(
            self._indexed_keys
        ), f"Duplicate keys in {self}"

    @property
    def arity(self) -> int:
        return len(self.keys)

    @cached_property
    def _keyed_indices(self) -> Map[K, int]:  # Map[K] Whole
        return Map.new((k, i) for i, k in enumerate(self.keys) if k is not None)

    @cached_property
    def _indexed_keys(self) -> Map[int, K]:  # Map[Whole] K
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
    def shape(self) -> Shape[K]:  # Shape[arity] K
        return Shape(arity=self.arity, keys=frozenset(self._indexed_keys))

    def __repr__(self) -> str:
        keys = ('_' if k is None else repr(k) for k in self.keys)
        return f"Index[{self.arity}] _ = ({', '.join(keys)})"

    def __len__(self) -> int:
        return self.arity

    def __iter__(self) -> Iterator[K | None]:
        return iter(self.keys)

    def __getitem__(self, offset: int) -> K | None:
        return self.keys[offset]

    @property
    def get(self):
        return self._keyed_indices.get

    @property
    def has(self):
        return self._keyed_indices.has


class Tuple[K, V](Record, frozen=True, consed=True):
    index: Index[K]  # Index[L] K
    values: tuple[V, ...]  # inner representation

    @property
    def arity(self) -> int:
        return len(self.index)

    @property
    def shape(self) -> Shape[K]:  # Shape[arity] K
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
            else:
                return f"{k}={repr(v)}"

        return (
            "("
            + ", ".join(repr_element(k, v) for k, v in zip(self.index, self.values))
            + ")"
        )

    @classmethod
    def new(cls, *positional: V, **nominal: V) -> Tuple[str, V]:
        index = Index((None,) * len(positional) + tuple(nominal.keys()))
        values = positional + tuple(nominal.values())
        return Tuple(index, values)

    EMPTY: ClassVar[Tuple[Any, Any]]

    # @classmethod
    # def new(cls, *positional: V, **nominal: dict[str, V]) -> Tuple[str, V]:
    #     items: list[tuple[Optional[str], V]] = []
    #     for i, v in enumerate(positional):
    #         items.append((None, v))
    #     for k, v in nominal.items():
    #         items.append((k, v))
    #     return cls.from_iter(items)

    # @classmethod
    # def from_iter(cls, items: Iterable[tuple[K, V]]) -> Tuple[V, K]:
    #     return cls(
    #         _key_index=Index.from_iter(k for k, v in items),
    #         _values=tuple(v for k, v in items),
    #     )

    # @classmethod
    # def from_dict(cls, d: dict[K, V]) -> Tuple[V, K]:
    #     return cls.from_iter(d.items())

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
            # if offset is None:
            if "default" in kwargs:
                return kwargs["default"]
            if "fallback" in kwargs:
                return kwargs["fallback"]()
            raise KeyError(f"Key not found: {key}")
        return self.values[offset]

    # def has(self, key: K) -> bool:
    #     return self.index.has(key)

    def apply[R](self, func: Callable[[V], R]) -> Tuple[K, R]:
        return Tuple(
            index=self.index,
            values=tuple(func(v) for v in self.values),
        )


Tuple.EMPTY = Tuple(Index(()), ())

