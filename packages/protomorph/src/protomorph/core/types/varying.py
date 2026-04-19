from __future__ import annotations

from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLike as _TupleLikeType


class Varying[*T](_TupleLikeType):
    ANCHOR: _ClassVar[_pm.Anchor] = _pm.anchors.varying
    Empty: _ClassVar[Varying]

    element_types: tuple[_pm.Type, ...]

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of(
            _pm.anchors.varying,
            *(tp.metatype() for tp in self.element_types),
        )

    @property
    def schema(self) -> _pm.Schema:
        return _pm.Tuple.new(*(_pm.val(value) for value in self.element_types))

    def _contains_slots(self) -> tuple[_pm.Type, ...]:
        return self.element_types

    @classmethod
    def of(cls, *args: _pm.Type) -> Varying:
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
                _pm.Indexed.of(
                    *(val.descriptor for val in vals),
                    **{key: value.descriptor for key, value in kwvals.items()},
                ),
                children,
            )
        return _pm.Tuple(cls.of(*(val.descriptor for val in vals)), vals)
