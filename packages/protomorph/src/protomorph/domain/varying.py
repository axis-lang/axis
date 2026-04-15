from __future__ import annotations

from itertools import chain as _chain
from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import cast as _cast

import protomorph as _pm

from .spread import Spread as _Spread
from .tuple_like import TupleLikeType as _TupleLikeType


class VaryingType[T: tuple[_Any, ...]](_TupleLikeType):
    Empty: _ClassVar[VaryingType]

    values: tuple[_pm.Type, ...]

    def metatype(self) -> _pm.Type:
        return VaryingType(tuple(tp.metatype() for tp in self.values))

    @property
    def schema(self) -> _pm.Schema:
        return _pm.Tuple.new(*(_pm.val(value) for value in self.values))

    def splice(self) -> _TupleLikeType:
        if not any(isinstance(value, _Spread) for value in self.values):
            return self
        new_values: list[_pm.Type] = []
        for value in self.values:
            if isinstance(value, _Spread):
                new_values.extend(_cast(tuple[_pm.Type, ...], value.values))
                continue
            new_values.append(value)
        return type(self)(tuple(new_values))

    @classmethod
    def of(cls, *args: _pm.Type) -> VaryingType:
        normalized = tuple(
            _cast(_pm.Type, arg.fetch()) if isinstance(arg, _pm.Val) else arg for arg in args
        )
        return cls(normalized)

    @classmethod
    def new(cls, *vals: _pm.Val, **kwvals: _pm.Val) -> _pm.Tuple:
        if kwvals:
            indexed_type = getattr(_pm, "IndexedType")
            return _pm.Tuple(
                indexed_type.of(
                    *(val.descriptor for val in vals),
                    **{key: value.descriptor for key, value in kwvals.items()},
                ),
                tuple(_chain(vals, kwvals.values())),
            )
        return _pm.Tuple(cls.of(*(val.descriptor for val in vals)), tuple(vals))
