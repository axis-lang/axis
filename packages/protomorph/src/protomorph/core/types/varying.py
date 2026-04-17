from __future__ import annotations

from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLikeType as _TupleLikeType


class VaryingType[*T](_TupleLikeType):
    ANCHOR: _ClassVar[_pm.Anchor] = _pm.Anchor("std.metas.Varying")
    Empty: _ClassVar[VaryingType]

    values: tuple[_pm.Type, ...]

    def metatype(self) -> _pm.Type:
        # return _pm.Spec.of("std.metas.Varying", *tuple(tp.metatype() for tp in self.values))
        return _pm.Spec.of(
            "std.metas.Varying",
            *(_pm.val(tp.metatype()) for tp in self.values),
        )

    @property
    def schema(self) -> _pm.Schema:
        return _pm.Tuple.new(*(_pm.val(value) for value in self.values))

    @classmethod
    def of(cls, *args: _pm.Type) -> VaryingType:
        normalized = tuple(
            _cast(_pm.Type, arg.content) if isinstance(arg, _pm.Val) else arg
            for arg in args
        )
        return cls(normalized)

    @classmethod
    def new(cls, *vals: _pm.Val, **kwvals: _pm.Val) -> _pm.Tuple:
        if kwvals:
            children = vals + tuple(kwvals.values())
            return _pm.Tuple(
                _pm.IndexedType.of(
                    *(val.descriptor for val in vals),
                    **{key: value.descriptor for key, value in kwvals.items()},
                ),
                children,
            )
        return _pm.Tuple(cls.of(*(val.descriptor for val in vals)), vals)
