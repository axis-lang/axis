from __future__ import annotations

from decimal import Decimal
from typing import Any, ClassVar, Iterable, Union

from protobase import Inmutable, Consed, Missing, MissingType, frozendict, is_abstract

import protomorph as morph

__all__ = [
    "Literal",
    "Builtin",
    "Data",
    "Val",
    "Const",
]


_PENDING_BUILTINS: list[type["Builtin"]] = []


type Literal = Union[
    int,
    float,
    Decimal,
    str,
    bool,
    None,
]

type Data = Union[
    Literal,
    Builtin,
    tuple["Data", ...],
    frozenset["Data"],
    frozendict["Data", "Data"],
]


class Builtin(Consed, abstract=True):
    ANCHOR: ClassVar[str]

    @classmethod
    def __class_post_build__(cls) -> None:
        if is_abstract(cls):
            return
        _PENDING_BUILTINS.append(cls)

    @classmethod
    def _anchor_path(cls) -> str:
        anchor = cls.__dict__.get("ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def _type(cls, *args: type | morph.Type) -> morph.Type:
        from .native import build_builtin_type

        return build_builtin_type(cls, *args)


class Val(Inmutable, abstract=True):
    __type__: morph.Type
    __data__: Data

    @property
    def type(self) -> morph.Type:
        return self.__type__

    @property
    def data(self) -> Data:
        return self.__data__

    def __repr__(self) -> str:
        from .format import format_morph

        return format_morph(self)

    def __getitem__(self, keyname: str | int) -> Val:
        return morph.get(self, keyname)

    def wrap(self, data: Data) -> Val:
        if not self.__type__.is_meta:
            raise TypeError(
                f"{type(self).__name__}.wrap requires a type value, got {self.__type__!r}"
                f" with data {self.__data__!r}"
            )
        if not isinstance(self.__data__, morph.Type):
            raise TypeError(
                f"{type(self).__name__}.wrap requires a value that resolves to protomorph.Type"
                f" as its type, got {self.__data__!r} of type {type(self.__data__)}"
            )
        return self.__data__._wrap(data)

    @property
    def attrs(self) -> morph.Struct[str, Val] | None:
        fields = morph.dir(self)
        if fields is None:
            return None

        values = tuple(
            morph.get(self, key if key is not None else i)
            for i, key in enumerate(fields.index.keys)
        )
        return morph.Struct.from_keys(fields.index.keys, values)

    @property
    def has_attrs(self) -> bool:
        return self.attrs is not None

    def __len__(self) -> int:
        attrs = self.attrs
        return 0 if attrs is None else len(attrs)

    def get(self, key: int | str, default: Val | MissingType = Missing) -> Val | MissingType:
        try:
            return morph.get(self, key)
        except KeyError:
            if default is Missing:
                raise
            return default

    def dir(self) -> Iterable[str]:
        return (morph.dir(self) or morph.Struct.Empty).index._keyed_indices.keys


class Const[T: morph.Type = Any, D: Data = Any](Val, Consed):
    pass
