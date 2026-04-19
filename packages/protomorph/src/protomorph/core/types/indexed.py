from __future__ import annotations

from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLike as _TupleLikeType
from .varying import Varying as _VaryingType


class Indexed(_TupleLikeType):
    slots: _pm.Uniform | _VaryingType
    index: _pm.Index

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of(_pm.anchors.indexed, self.slots.metatype())

    def __contains__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Indexed) or type(self) is not type(other):
            return False
        return self.index is other.index and other.slots in self.slots

    @property
    def schema(self) -> _pm.Schema:
        if isinstance(self.slots, _pm.Uniform):
            content = (self.slots.element_type,) * len(self.index)
        else:
            slots_schema = self.slots.schema
            if slots_schema is None:
                raise TypeError(
                    f"IndexedType slots type must expose schema: {type(self.slots).__name__}"
                )
            content = tuple(_cast(_pm.Type, child.content) for child in slots_schema)
        return _pm.Tuple(
            _pm.Indexed(_pm.Varying(content), self.index),
            content,
        )

    @classmethod
    def of(cls, *args: _pm.Type, **kwargs: _pm.Type) -> Indexed:
        positional = tuple(
            _cast(_pm.Type, arg.content) if isinstance(arg, _pm.Val) else arg
            for arg in args
        )
        values = positional + tuple(
            _cast(_pm.Type, value.content) if isinstance(value, _pm.Val) else value
            for value in kwargs.values()
        )
        keys = (None,) * len(positional) + tuple(_pm.Id(key) for key in kwargs)
        return cls(_VaryingType(values), _pm.Index.of(*keys))

    def __invariants__(self) -> None:
        assert isinstance(
            self.slots, (_pm.Uniform, _VaryingType)
        ), "IndexedType slots must be uniform or varying"
        expected = len(self.index) if isinstance(self.slots, _pm.Uniform) else len(self.slots.element_types)
        assert expected == len(self.index), "IndexedType slots must match index length"
