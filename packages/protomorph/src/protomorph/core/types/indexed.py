from __future__ import annotations

from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLikeType as _TupleLikeType
from .varying import VaryingType as _VaryingType


class IndexedType(_TupleLikeType):
    inner: _VaryingType # TupleLikeType
    index: _pm.Index

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of("std.metas.Indexed", self.inner.metatype())

    @property
    def schema(self) -> _pm.Schema:
        inner_schema = self.inner.schema
        if inner_schema is None:
            raise TypeError(
                f"IndexedType inner type must expose schema: {type(self.inner).__name__}"
            )
        content = tuple(child.fetch() for child in inner_schema)
        return _pm.Tuple(
            _pm.IndexedType(_pm.VaryingType(content), self.index),
            content,
        )

    def splice(self) -> _TupleLikeType:
        inner = self.inner.splice()
        if not isinstance(inner, _VaryingType):
            raise TypeError(
                "IndexedType splice requires a VaryingType inner descriptor"
            )
        index_values: list[object] = []
        for item in self.inner.values:
            if isinstance(item, _pm.Spread):
                index_values.append(_pm.Spread((None,) * len(item.values)))
                continue
            index_values.append(None)
        keyed = list(self.index.content)
        for offset, key in enumerate(keyed):
            if key is not None:
                index_values[offset] = key
        index = _pm.Index.of(
            *_cast(tuple[_pm.Id | None, ...], tuple(index_values))
        ).splice()
        if len(inner) != len(index):
            raise ValueError("IndexedType splice produced mismatched slot count")
        return type(self)(inner, index)

    @classmethod
    def of(cls, *args: _pm.Type, **kwargs: _pm.Type) -> IndexedType:
        positional = tuple(
            _cast(_pm.Type, arg.fetch()) if isinstance(arg, _pm.Val) else arg
            for arg in args
        )
        values = positional + tuple(
            _cast(_pm.Type, value.fetch()) if isinstance(value, _pm.Val) else value
            for value in kwargs.values()
        )
        keys = (None,) * len(positional) + tuple(_pm.Id(key) for key in kwargs)
        return cls(_VaryingType(values), _pm.Index.of(*keys))

    def __invariants__(self) -> None:
        assert isinstance(
            self.inner, _VaryingType
        ), "IndexedType inner must be a VaryingType"
        assert len(self.inner.values) == len(
            self.index
        ), "IndexedType slots must match index length"
