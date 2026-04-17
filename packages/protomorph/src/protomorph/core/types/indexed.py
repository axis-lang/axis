from __future__ import annotations

from typing import cast as _cast

import protomorph.core as _pm

from .tuple_like import TupleLikeType as _TupleLikeType
from .varying import VaryingType as _VaryingType


class IndexedType(_TupleLikeType):
    slots: _pm.UniformType | _VaryingType
    index: _pm.Index

    def metatype(self) -> _pm.Type:
        return _pm.Spec.of("std.metas.Indexed", self.slots.metatype())

    @property
    def schema(self) -> _pm.Schema:
        if isinstance(self.slots, _pm.UniformType):
            content = (self.slots.element_type,) * len(self.index)
        else:
            slots_schema = self.slots.schema
            if slots_schema is None:
                raise TypeError(
                    f"IndexedType slots type must expose schema: {type(self.slots).__name__}"
                )
            content = tuple(_cast(_pm.Type, child.content) for child in slots_schema)
        return _pm.Tuple(
            _pm.IndexedType(_pm.VaryingType(content), self.index),
            content,
        )

    @classmethod
    def of(cls, *args: _pm.Type, **kwargs: _pm.Type) -> IndexedType:
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
            self.slots, (_pm.UniformType, _VaryingType)
        ), "IndexedType slots must be uniform or varying"
        expected = len(self.index) if isinstance(self.slots, _pm.UniformType) else len(self.slots.values)
        assert expected == len(self.index), "IndexedType slots must match index length"
