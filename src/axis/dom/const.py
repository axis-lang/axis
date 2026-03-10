from __future__ import annotations

from typing import Any

from axis import dom


class Const[T: dom.Type = Any, D: dom.Data = Any](dom.Pure[T, D]):

    @staticmethod
    def new_literal(value: dom.Literal):
        return dom._literal(value)

    @staticmethod
    def new_literal_struct(
        *positional: dom.Literal,
        **nominal: dom.Literal,
    ) -> dom.Const[dom.StructType]:
        return dom._literal_struct(*positional, **nominal)


    @staticmethod
    def new_struct(
        *positional: dom.Pure | dom.Var,
        **nominal: dom.Pure  | dom.Var,
    ) -> dom.Const[dom.StructType]:
        return dom._struct(*positional, **nominal)

    @staticmethod
    def new_union(
        types: frozenset[dom.Type],
        active: dom.Pure | dom.Var,
    ) -> dom.Const[dom.UnionType]:
        return dom._union(types, active)
