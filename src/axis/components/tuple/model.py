# %%
from __future__ import annotations
from typing import Callable
from frozendict import frozendict
from protobase import Object, traits


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
        return iter(self._inner.values())

    def __getitem__(self, key: str) -> T:
        return self._inner[key]

    def item_at(self, index: int) -> T:
        return self._inner.item(index)

    def key_at(self, index: int) -> T:
        return self._inner.key(index)

    def value_at(self, index: int) -> T:
        return self._inner.value(index)

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
