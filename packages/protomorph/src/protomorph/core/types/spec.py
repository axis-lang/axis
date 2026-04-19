from __future__ import annotations

from typing import Any as _Any, ClassVar as _ClassVar

import protomorph.core as _pm

from protomorph.core.foundation import Anchor as _Anchor
from .type_ import Type as _Type



class Spec(_Type):
    Any: _ClassVar[Spec]
    Tuple: _ClassVar[Spec]
    Index: _ClassVar[Spec]
    Never: _ClassVar[Spec]
    Integer: _ClassVar[Spec]
    Text: _ClassVar[Spec]
    Decimal: _ClassVar[Spec]
    Boolean: _ClassVar[Spec]
    Empty: _ClassVar[Spec]
    Id: _ClassVar[Spec]
    Anchor: _ClassVar[Spec]

    anchor: _Anchor
    args: _pm.Tuple

    def metatype(self) -> _pm.Type:
        return Spec.of(_pm.anchors.specialization)

    @property
    def schema(self) -> _pm.Schema | None:
        return _pm.current_realm().schema_for(self)

    @property
    def variants(self) -> frozenset[_pm.Type]:
        return _pm.current_realm().variants_of(self)

    @classmethod
    def of(cls, anchor: _Anchor | str, *args: _Any, **kwargs: _Any) -> Spec:
        values = args + tuple(kwargs.values())
        descriptors = tuple(
            (
                value.descriptor
                if isinstance(value, _pm.Val)
                else (
                    value.metatype()
                    if isinstance(value, _Type)
                    else _pm.val(type(value)).content
                )
            )
            for value in values
        )
        descriptor = (
            _pm.Indexed.of(
                *descriptors[: len(args)],
                **{
                    key: descriptors[len(args) + index]
                    for index, key in enumerate(kwargs)
                },
            )
            if kwargs
            else _pm.Varying(descriptors)
        )
        return cls(_Anchor(anchor), _pm.Tuple(descriptor, values))

    @classmethod
    def new(cls, anchor: _Anchor | str, *vals: _pm.Val, **kwvals: _pm.Val) -> Spec:
        return cls(_Anchor(anchor), _pm.Varying.new(*vals, **kwvals))
