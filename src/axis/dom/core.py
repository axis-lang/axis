from __future__ import annotations

from decimal import Decimal
from typing import Self, Union as TypingUnion, cast

from protobase import Consed, frozendict, inmutable

from axis import syn
from axis.dom.tuple_ import Tuple


class Builtin(Consed, abstract=True): ...


inmutable(Builtin)


type Atom = TypingUnion[int, float, Decimal, str, bool, None]
type Data = TypingUnion[
    Atom, Builtin, tuple["Data", ...], frozenset["Data"], frozendict["Data", "Data"]
]


def _is_data(value: object) -> bool:
    return isinstance(
        value,
        (
            int,
            float,
            Decimal,
            str,
            bool,
            type(None),
            Builtin,
            tuple,
            frozenset,
            frozendict,
        ),
    )


class Type(Builtin, abstract=True):
    @classmethod
    def var(cls, ident: str) -> "Var.Type":
        return Var.Type(id=ident)


class Qualifier(Type, abstract=True):
    underlying: "Type"


class NominalQualifier(Qualifier):
    ref: "Ref"

    @classmethod
    def from_ref(cls, ref: "Ref", underlying: "Type") -> "NominalQualifier":
        return cls(ref=ref, underlying=underlying)

    @classmethod
    def from_str(cls, value: str, underlying: "Type") -> "NominalQualifier":
        return cls.from_ref(Ref.from_str(value), underlying)


class NominalType(Type):
    ref: "Ref"

    @classmethod
    def from_ref(cls, ref: "Ref") -> "NominalType":
        return cls(ref=ref)

    @classmethod
    def from_str(cls, value: str) -> "NominalType":
        return cls.from_ref(Ref.from_str(value))


class StructType(Type):
    fields: Tuple[str, "Type"]


class FnType(Type):
    args: tuple["Type", ...]
    ret: "Type"


class UnionType(Type):
    members: tuple["Type", ...]


class Dom(Consed, abstract=True):
    type: Type


class Val(Dom, abstract=True): ...


class Const(Val):
    data: Data

    @classmethod
    def from_type_data(cls, type_: Type, data: Data) -> Self:
        return cls(type=type_, data=data)

    @classmethod
    def from_literal(cls, value: Data) -> Self:
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
            raise TypeError(f"Const.data must be primitive, got {type(self.data)}")


class Var(Dom):
    class Type(Type):
        id: str

    type: "Var.Type"  # type: ignore[override]
    data: tuple[str, str]

    @classmethod
    def from_id(cls, ident: str) -> "Var":
        return cls(type=Var.Type(id=ident), data=("var", ident))

    def __invariants__(self) -> None:
        if not isinstance(self.data, tuple) or len(self.data) != 2:
            raise TypeError(f"Var.data must be ('var', id), got {self.data!r}")
        tag, ident = self.data
        if tag != "var" or not isinstance(ident, str):
            raise TypeError(f"Var.data must be ('var', id), got {self.data!r}")
        if cast(Var.Type, self.type).id != ident:
            raise TypeError("Var.type id must match Var.data id")


class Err(Val):
    message: str
    origin: "syn.Node | None" = None
    type: "Ref.Type | None" = None  # type: ignore[override]
    data: "Ref.Data | None" = None  # type: ignore[override]

    def __invariants__(self) -> None:
        if not isinstance(self.message, str) or not self.message:
            raise TypeError("Err.message must be a non-empty string")
        if self.type is None:
            object.__setattr__(self, "type", Ref.Type(parent=None, params=Tuple.EMPTY))
        if self.data is None:
            object.__setattr__(
                self,
                "data",
                Ref.Data(parent=None, member="", params=()),
            )


class Ref(Val):
    class Type(Type):
        parent: "Ref.Type | None" = None
        params: Tuple[str, "Type"] = Tuple.EMPTY

    class Data(Builtin):
        member: str
        params: tuple[Data, ...]
        parent: "Ref.Data | None"

    type: "Ref.Type"  # type: ignore[override]
    data: "Ref.Data"

    @classmethod
    def from_parts(
        cls,
        member: str,
        *,
        parent: "Ref | None" = None,
        params: Tuple[str, Const] = Tuple.EMPTY,
    ) -> "Ref":
        parent_type = cast(Ref.Type | None, parent.type) if parent else None
        param_types = Tuple(index=params.index, values=tuple(p.type for p in params.values))
        ref_type = Ref.Type(parent=parent_type, params=param_types)
        ref_data = Ref.Data(
            parent=None if parent is None else parent.data,
            member=member,
            params=tuple(_const_data(p) for p in params.values),
        )
        return cls(type=ref_type, data=ref_data)

    @classmethod
    def root(cls, name: str) -> "Ref":
        ref_type = Ref.Type(parent=None, params=Tuple.EMPTY)
        ref_data = Ref.Data(parent=None, member=name, params=())
        return cls(type=ref_type, data=ref_data)

    @classmethod
    def from_str(cls, value: str) -> "Ref":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Ref.from_str requires at least one segment")
        ref = cls.root(segments[0])
        for segment in segments[1:]:
            ref = ref.child(segment)
        return ref

    def child(
        self,
        name: str,
        *,
        params: Tuple[str, Const] = Tuple.EMPTY,
    ) -> "Ref":
        return Ref.from_parts(name, parent=self, params=params)

    def with_args(self, args: Const) -> "Ref":
        if not isinstance(args.type, StructType):
            raise TypeError("Ref.with_args requires a StructType value")
        if not isinstance(args.data, tuple):
            raise TypeError("Ref.with_args requires tuple data")
        ref_type = Ref.Type(
            parent=self.type.parent,
            params=cast(Tuple[str, Type], args.type.fields),
        )
        ref_data = Ref.Data(parent=self.data.parent, member=self.data.member, params=args.data)
        return Ref(type=ref_type, data=ref_data)

    def __invariants__(self) -> None:
        if not isinstance(self.type, Ref.Type):
            raise TypeError(
                f"Ref.type must be Ref.Type, got {type(self.type).__name__}"
            )
        parent_data = self.data.parent
        member = self.data.member
        params_data = self.data.params
        if not isinstance(member, str) or not member:
            raise TypeError("Ref.member must be a non-empty string")
        if parent_data is None:
            if self.type.parent is not None:
                raise TypeError("Ref.Type parent is set but data has no parent")
        else:
            if self.type.parent is None:
                raise TypeError("Ref.Type parent is None but data has a parent")
        if not isinstance(params_data, tuple):
            raise TypeError("Ref.params data must be a tuple")
        if len(params_data) != len(self.type.params.values):
            raise TypeError("Ref params length does not match Ref.Type params")


def _const_data(value: Const) -> Data:
    if isinstance(value, Const):
        return value.data
    if isinstance(value, Ref):
        return value.data
    if hasattr(value, "data"):
        return cast(Data, getattr(value, "data"))
    raise TypeError("Const must carry data to be encoded")


def ref_segments(ref: Ref) -> tuple[str, ...]:
    segments: list[str] = []
    current: Ref.Data | None = ref.data
    while current is not None:
        segments.append(current.member)
        current = current.parent
    return tuple(reversed(segments))
