from __future__ import annotations

from decimal import Decimal
from collections.abc import Callable
from typing import Any, ClassVar, Iterable, Union, cast

from protobase import Inmutable, Consed, Missing, MissingType, frozendict, is_abstract

import protomorph_ as pm

__all__ = [
    "Literal",
    "ALL_BUILTINS",
    "Builtin",
    "Data",
    "Val",
    "Const",
]


ALL_BUILTINS: set[type["Builtin"]] = set()


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
        ALL_BUILTINS.add(cls)
        
        # Invalidate flux cache for builtin discovery
        # Use try/except to handle circular imports during bootstrap
        try:
            import protomorph_ as pm
            pm.NativeRegistry.all_builtins.invalidate_for(pm.NATIVE_REGISTRY)
        except (AttributeError, ImportError):
            # During bootstrap, registry may not be available yet
            # The invalidation will happen during the first registry access
            pass

    @classmethod
    def _anchor_path(cls) -> str:
        anchor = cls.__dict__.get("ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def _type(cls, *args: type | pm.Type) -> pm.Type:
        return pm.build_builtin_type(cls, *args)


class Val(Inmutable, abstract=True):
    __type__: pm.Type
    __data__: Data

    def __repr__(self) -> str:
        return pm.format_morph(self)

    def __getitem__(self, keyname: str | int) -> Val:
        return self.__type__._get(self.__data__, keyname)

    def wrap(self, data: Data) -> Val:
        if not isinstance(self.__data__, pm.Type):
            raise TypeError(
                f"{type(self).__name__}.wrap requires a value that resolves to protomorph.Type"
                f" as its type, got {self.__data__!r} of type {type(self.__data__)}"
            )
        return self.__data__._wrap(data)

    def encode(self, format: str | None = None) -> Data:
        return self.__type__.serialize(self.__data__, format)

    def as_type(self) -> pm.Type | None:
        return pm.as_type(self)

    def subst(
        self,
        env: Callable[[pm.Val], pm.Val | None],
    ) -> Val:
        return pm.subst_val(self, env)

    @property
    def attrs(self) -> pm.Struct[str, Val] | None:
        layout = self.__type__.layout()
        fields = layout.fields if isinstance(layout, pm.StructLayout) else None
        if fields is None:
            return None

        values = tuple(
            self.__type__._get(self.__data__, key if key is not None else i)
            for i, key in enumerate(fields.index.keys)
        )
        return cast(pm.Struct[str, Val], fields).with_values(values)

    @property
    def has_attrs(self) -> bool:
        return self.attrs is not None

    def __len__(self) -> int:
        attrs = self.attrs
        return 0 if attrs is None else len(attrs)

    def get(
        self, key: int | str, default: Val | MissingType = Missing
    ) -> Val | MissingType:
        try:
            return self.__type__._get(self.__data__, key)
        except KeyError:
            if default is Missing:
                raise
            return default

    def dir(self) -> Iterable[str]:
        layout = self.__type__.layout()
        fields = pm.Struct.Empty
        if isinstance(layout, pm.StructLayout):
            fields = layout.fields
        return fields.index._keyed_indices.keys

    @property
    def type(self) -> pm.Type:
        return self.__type__

    @property
    def data(self) -> Data:
        return self.__data__


class Const[T: pm.Type = Any, D: Data = Any](Val, Consed):
    pass
