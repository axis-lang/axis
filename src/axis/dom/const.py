from __future__ import annotations

from typing import Any, Self

from axis import dom


class Const[T: dom.Type = Any, D: dom.Data = Any](dom.Pure[T, D]):

    @staticmethod
    def from_literal(value: dom.Literal) -> "Const[dom.NominalType]":
        return Const(type=dom.Type.of_literal(value), data=value)

    @staticmethod
    def from_struct(
        *positional: dom.Literal, **nominal: dom.Literal
    ) -> Const[dom.StructType]:
        fields = dom.Struct.new(*positional, **nominal)
        field_types = fields.map(dom.Type.of_literal)
        return Const(type=dom.StructType(fields=field_types), data=fields.values)
