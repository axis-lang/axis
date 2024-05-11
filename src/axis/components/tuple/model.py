# %%
from __future__ import annotations
from typing import Callable, Optional
from frozendict import frozendict
from protobase import Object, traits

__all__ = [
    "Tuple",
]


class Tuple[T](Object, traits.Repr, traits.Consed):
    _inner: frozendict

    @classmethod
    def from_args(cls, *args, **kwargs) -> Tuple:
        return cls({n: v for n, v in enumerate(args)} | kwargs)

    def __new__(cls, *args, **kwargs) -> Tuple:
        return super().__new__(cls, _inner=frozendict(*args, **kwargs))

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self._inner)})"

    def __iter__(self):
        return self._inner.values()

    def __getitem__(self, key: str) -> T:
        return self._inner[key]

    def item_at(self, index: int) -> T:
        return self._inner.item(index)

    def key_at(self, index: int) -> T:
        return self._inner.key(index)

    def value_at(self, index: int) -> T:
        return self._inner.value(index)

    def items(self):
        return self._inner.items()

    def keys(self):
        return self._inner.keys()

    def values(self):
        return self._inner.values()

    def map[R](self, fn: Callable[[T], R]) -> Tuple[R]:
        cls = self.__class__
        return cls({k: fn(v) for k, v in self._inner.items()})

    def to_args(self):
        args = []
        kwargs = {}

        for k, v in self._inner.items():
            if isinstance(k, int):
                if k != len(args):
                    raise ValueError(
                        "Tuple keys must be contiguous integers starting from 0."
                    )
                args.append(v)
            elif isinstance(k, str):
                kwargs[k] = v
            else:
                raise ValueError("Tuple keys must be either integers or strings.")
        return args, kwargs


t = Tuple.from_args(1, 2, x=3, y=4, z=5)


class MatchPattern:
    """
    Matching puede ser tambien sore shapes
    MatchPattern debe estar fuera de tuple

    Un patron de matching puede reducirse a un conjunto de condiciones (guards)
    que deben probarse para determinar si un objeto cumple con el patron.

    """

    def match(self, obj: Tuple) -> Optional[Tuple]: ...

    # (..) MATCH_ALL default pattern, less specific


class MatchDict[T]: ...
