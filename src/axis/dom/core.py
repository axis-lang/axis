from __future__ import annotations

from decimal import Decimal
from typing import Any, Union as TypingUnion, cast

from protobase import Record, cached_property, frozendict

from axis.dom.tuple_ import Tuple


class Node(Record, frozen=True, consed=True, abstract=True): ...


type Atom = TypingUnion[int, float, Decimal, str, bool, None]
type Data = TypingUnion[Atom, tuple, frozenset, frozendict]


def _is_data(value: object) -> bool:
    return isinstance(
        value,
        (int, float, Decimal, str, bool, type(None), tuple, frozenset, frozendict),
    )


class Type(Record, frozen=True, consed=True, abstract=True):
    @classmethod
    def var(cls, ident: str) -> "VarType":
        return VarType(id=ident)


class RefType(Type, frozen=True, consed=True):
    parent: "RefType | None" = None
    params: Tuple[str | None, "Const"] = Tuple.EMPTY


class Qualifier(Type, frozen=True, consed=True, abstract=True):
    underlying: "Type"


class NominalQualifier(Qualifier, frozen=True, consed=True):
    ref: "Ref"

    @classmethod
    def from_ref(cls, ref: "Ref", underlying: "Type") -> "NominalQualifier":
        return cls(ref=ref, underlying=underlying)

    @classmethod
    def from_str(cls, value: str, underlying: "Type") -> "NominalQualifier":
        return cls.from_ref(Ref.from_str(value), underlying)


class NominalType(Type, frozen=True, consed=True):
    ref: "Ref"

    @classmethod
    def from_ref(cls, ref: "Ref") -> "NominalType":
        return cls(ref=ref)

    @classmethod
    def from_str(cls, value: str) -> "NominalType":
        return cls.from_ref(Ref.from_str(value))


class StructType(Type, frozen=True, consed=True):
    fields: Tuple[str | None, "Type"]


class FnType(Type, frozen=True, consed=True):
    args: tuple["Type", ...]
    ret: "Type"


class UnionType(Type, frozen=True, consed=True):
    members: tuple["Type", ...]


class VarType(Type, frozen=True, consed=True):
    id: str


class ValueBase[T: Type = Type](Node, frozen=True, consed=True, abstract=True):
    type: T


class Const[T: Type = Type](ValueBase[T], frozen=True, consed=True, abstract=True):
    ...


class Val(Const, frozen=True, consed=True):
    data: Data

    @classmethod
    def from_type_data(cls, type_: Type, data: Data) -> "Val":
        return cls(type=type_, data=data)

    @classmethod
    def from_literal(cls, value: Data) -> "Val":
        if isinstance(value, bool):
            type_ = NominalType.from_str("std.Boolean")
        elif isinstance(value, int):
            type_ = NominalType.from_str("std.Integer")
        elif isinstance(value, Decimal):
            if value == value.to_integral_value():
                type_ = NominalType.from_str("std.Integer")
                value = int(value)
            else:
                type_ = NominalType.from_str("std.Decimal")
        elif isinstance(value, str):
            type_ = NominalType.from_str("std.Text")
        else:
            type_ = NominalType.from_str("std.Value")
        return cls(type=type_, data=value)

    def __invariants__(self) -> None:
        if not _is_data(self.data):
            raise TypeError(f"Val.data must be primitive, got {type(self.data)}")


class Var(ValueBase[VarType], frozen=True, consed=True):
    type: VarType
    data: tuple[str, str]

    @classmethod
    def from_id(cls, ident: str) -> "Var":
        return cls(type=VarType(id=ident), data=("var", ident))

    def __invariants__(self) -> None:
        if not isinstance(self.data, tuple) or len(self.data) != 2:
            raise TypeError(f"Var.data must be ('var', id), got {self.data!r}")
        tag, ident = self.data
        if tag != "var" or not isinstance(ident, str):
            raise TypeError(f"Var.data must be ('var', id), got {self.data!r}")
        if self.type.id != ident:
            raise TypeError("Var.type id must match Var.data id")


class Meta(Const, frozen=True, consed=True):
    ...


type RefData = tuple["RefData | None", str, tuple[Data, ...]]


class Ref(Const[RefType], frozen=True, consed=True):
    type: RefType
    data: RefData

    @classmethod
    def from_parts(
        cls,
        member: str,
        *,
        parent: "Ref | None" = None,
        params: Tuple[str | None, Const] = Tuple.EMPTY,
    ) -> "Ref":
        ref_type = RefType(parent=parent.type if parent else None, params=params)
        ref_data = (
            None if parent is None else parent.data,
            member,
            tuple(_const_data(p) for p in params.values),
        )
        return cls(type=ref_type, data=ref_data)

    @classmethod
    def from_str(cls, value: str) -> "Ref":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Ref.from_str requires at least one segment")
        ref = cls.from_parts(segments[0])
        for segment in segments[1:]:
            ref = ref.member_ref(segment)
        return ref

    @cached_property
    def parent(self) -> "Ref | None":
        parent_data = self.data[0]
        if parent_data is None:
            return None
        parent_type = self.type.parent
        if parent_type is None:
            raise ValueError("Ref data has parent but type has no parent")
        return Ref(type=parent_type, data=cast(RefData, parent_data))

    @property
    def member(self) -> str:
        return self.data[1]

    @cached_property
    def params(self) -> Tuple[str | None, Const]:
        return self.type.params

    @property
    def segments(self) -> tuple[str, ...]:
        if self.parent is None:
            return (self.member,)
        return self.parent.segments + (self.member,)

    def member_ref(
        self,
        name: str,
        *,
        params: Tuple[str | None, Const] = Tuple.EMPTY,
    ) -> "Ref":
        return Ref.from_parts(name, parent=self, params=params)

    def __invariants__(self) -> None:
        if not isinstance(self.type, RefType):
            raise TypeError(f"Ref.type must be RefType, got {type(self.type).__name__}")
        parent_data, member, params_data = self.data
        if not isinstance(member, str) or not member:
            raise TypeError("Ref.member must be a non-empty string")
        if parent_data is None:
            if self.type.parent is not None:
                raise TypeError("RefType parent is set but data has no parent")
        else:
            if self.type.parent is None:
                raise TypeError("RefType parent is None but data has a parent")
        if not isinstance(params_data, tuple):
            raise TypeError("Ref.params data must be a tuple")
        if len(params_data) != len(self.type.params.values):
            raise TypeError("Ref params length does not match RefType params")


def _const_data(value: Const) -> Data:
    if isinstance(value, Meta):
        return None
    if isinstance(value, Val):
        return cast(Val, value).data
    if isinstance(value, Ref):
        return cast(Ref, value).data
    if hasattr(value, "data"):
        return cast(Data, getattr(value, "data"))
    raise TypeError("Const must carry data to be encoded")
