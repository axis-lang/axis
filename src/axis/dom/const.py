from __future__ import annotations

from typing import Any, Self

from axis import dom


class Const[T: dom.Type = Any, D: dom.Data = Any](dom.Pure[T, D]):

    @staticmethod
    def of_literal(value: dom.Literal):
        return Const(type=dom.type_of_native(type(value)), data=value)

    @staticmethod
    def of_struct(
        *positional: dom.Literal,
        **nominal: dom.Literal,
    ) -> dom.Const[dom.StructType]:
        fields = dom.Struct.new(*positional, **nominal)
        return Const(
            type=dom.StructType(
                fields=fields.map(dom.type_of_literal),
            ),
            data=fields.values,
        )

    # @staticmethod
    # def of_union() -> dom.Const[dom.UnionType]:
    #     ...

# def _type_of_literal(literal: dom.Literal) -> dom.Type:
#     return type_of_native(type(literal))

