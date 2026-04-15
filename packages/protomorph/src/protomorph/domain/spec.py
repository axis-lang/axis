from __future__ import annotations

from typing import Any as _Any
from typing import cast as _cast

import protomorph as _pm
from protobase import flux as _flux

from .ids import Anchor as _Anchor
from .type_ import Type as _Type


class Spec(_Type):
    anchor: _Anchor
    args: _pm.Tuple

    def metatype(self) -> _pm.Type:
        return Spec.of("std.metas.Specialization")

    @property
    def schema(self) -> _pm.Schema | None:
        return _pm.current_realm().schema_for(self)

    @classmethod
    def of(cls, anchor: _Anchor | str, *args: _Any, **kwargs: _Any) -> Spec:
        values = args + tuple(kwargs.values())
        descriptors = tuple(_value_descriptor(value) for value in values)
        indexed_type = _cast(_Any, getattr(_pm, "IndexedType"))
        descriptor = (
            indexed_type.of(
                *descriptors[: len(args)],
                **{
                    key: descriptors[len(args) + index]
                    for index, key in enumerate(kwargs)
                },
            )
            if kwargs
            else _pm.VaryingType(descriptors)
        )
        tuple_args = _cast(_pm.Tuple, _pm.Tuple(_cast(_pm.Type[tuple], descriptor), values))
        return _cast(Spec, cls(_Anchor(anchor), tuple_args))

    @classmethod
    def new(cls, anchor: _Anchor | str, *vals: _pm.Val, **kwvals: _pm.Val) -> Spec:
        return _cast(Spec, cls(_Anchor(anchor), _pm.VaryingType.new(*vals, **kwvals)))


def _value_descriptor(value: _Any) -> _pm.Type:
    if isinstance(value, _pm.Val):
        return value.descriptor
    if isinstance(value, _Type):
        return value.metatype()
    return _project_runtime_type(value)


def _project_runtime_type(value: _Any) -> _pm.Type:
    return _cast(_pm.Type, _pm.val(type(value)).fetch())
