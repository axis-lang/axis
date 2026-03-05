from __future__ import annotations

from typing import cast

from axis import dom


class Var(dom.Val):
    class Type(dom.Type):
        id: str

    type: "Var.Type"  # type: ignore[override]
    data: str

    @classmethod
    def from_id(cls, ident: str) -> "Var":
        return cls(type=Var.Type(id=ident), data=ident)

    def __invariants__(self) -> None:
        if not isinstance(self.data, str) or not self.data:
            raise TypeError(f"Var.data must be a non-empty string, got {self.data!r}")
        if cast(Var.Type, self.type).id != self.data:
            raise TypeError("Var.type id must match Var.data id")


class Bound(dom.Pure):
    type: dom.Type
    data: dom.Data

    @classmethod
    def from_literal(cls, value: dom.Literal) -> "Bound":
        literal = dom.Const.new_literal(value)
        return cls(type=literal.type, data=literal.data)

    @classmethod
    def from_ref(cls, ref: dom.Ref) -> "Bound":
        return cls(type=ref.type, data=ref.data)

    @classmethod
    def var(cls, ident: str) -> "Bound":
        return cls(type=Var.Type(id=ident), data=ident)

