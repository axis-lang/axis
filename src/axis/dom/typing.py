from __future__ import annotations
from typing import TypeAlias
from protobase import Record, frozendict
#from protobase.inmutable import inmutable, register_inmutable
from axis.dom.tuple_ import Tuple, Shape, Index


class Node(Record, frozen=True, consed=True, abstract=True): ...


Atom: TypeAlias = int | float | str | bool | None
Data: TypeAlias = Atom | tuple | frozenset | frozendict

class Ref(Record, frozen=True, consed=True):
    segments: tuple[str, ...]

    @classmethod
    def from_str(cls, value: str) -> "Ref":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Ref.from_str requires at least one segment")
        return cls(segments=segments)


class TypeForm(Record, frozen=True, consed=True, abstract=True): ...


class Nominal(TypeForm, frozen=True, consed=True):
    ref: Ref
    params: "Const"
    schema: "Type | None"


class Struct(TypeForm, frozen=True, consed=True):
    fields: Tuple[str, "Type"]


class Function(TypeForm, frozen=True, consed=True):
    args: tuple["Type", ...]
    ret: "Type"


class Union(TypeForm, frozen=True, consed=True):
    members: tuple["Type", ...]


class Literal(TypeForm, frozen=True, consed=True):
    value: Data


class TypeVar(TypeForm, frozen=True, consed=True):
    id: str


class Type(Record, frozen=True, consed=True):
    form: TypeForm
    qualifiers: tuple["Type", ...] = ()


Meta = Type


class Val(Node, frozen=True, consed=True, abstract=True):
    meta: Type
    data: Data

    def __invariants__(self) -> None:
        if not isinstance(self.data, (int, float, str, bool, type(None), tuple, frozenset, frozendict)):
            raise TypeError(f"Val.data must be primitive, got {type(self.data)}")


class Const(Val, frozen=True, consed=True):
    ...


class Var(Val, frozen=True, consed=True):
    def __invariants__(self) -> None:
        assert isinstance(self.data, tuple)
        assert len(self.data) == 2
        tag, ident = self.data
        assert tag == "var"
        assert isinstance(ident, str)
