from __future__ import annotations

from typing import Any, Self

from axis import dom


class Const[T: dom.Type = Any, D: dom.Data = Any](dom.Pure[T, D]):

    @staticmethod
    def new_literal(value: dom.Literal) -> dom.Const:
        return Const(type=dom.Type.of_literal(value), data=value)

    @staticmethod
    def new_struct(
        *positional: dom.Literal,
        **nominal: dom.Literal,
    ) -> dom.Const[dom.StructType]:
        fields = dom.Struct.new(*positional, **nominal)
        return dom.Const(
            type=dom.StructType(fields=fields.map(dom.Type.of_literal)),
            data=fields.values,
        )
