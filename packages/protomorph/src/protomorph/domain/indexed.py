from __future__ import annotations

from typing import cast as _cast

import protomorph as _pm

from .spread import Spread as _Spread
from .tuple_like import TupleLikeType as _TupleLikeType
from .varying import VaryingType as _VaryingType


class IndexedType[T](_TupleLikeType):
    inner: _pm.Type[T]
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
        inner = _cast(_TupleLikeType, self.inner).splice()
        index_values: list[object] = []
        for item in _cast(_VaryingType, self.inner).values:
            if isinstance(item, _Spread):
                index_values.append(_Spread((None,) * len(item.values)))
                continue
            index_values.append(None)
        keyed = list(self.index.content)
        for offset, key in enumerate(keyed):
            if key is not None:
                index_values[offset] = key
        index = _pm.Index.of(*_cast(tuple[_pm.Id | None, ...], tuple(index_values))).splice()
        if len(inner) != len(index):
            raise ValueError("IndexedType splice produced mismatched slot count")
        return type(self)(_cast(_pm.Type, inner), index)

    @classmethod
    def of(cls, *args: _pm.Type, **kwargs: _pm.Type) -> IndexedType:
        positional = tuple(
            _cast(_pm.Type, arg.fetch()) if isinstance(arg, _pm.Val) else arg for arg in args
        )
        nominal = {
            key: (_cast(_pm.Type, value.fetch()) if isinstance(value, _pm.Val) else value)
            for key, value in kwargs.items()
        }
        values = positional + tuple(nominal.values())
        keys = (None,) * len(positional) + tuple(_pm.Id(key) for key in nominal)
        return _cast(
            IndexedType, cls(_cast(_pm.Type, _VaryingType(values)), _pm.Index.of(*keys))
        )
