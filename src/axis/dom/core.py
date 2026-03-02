from __future__ import annotations

from decimal import Decimal
from typing import Self, Union as TypingUnion, cast

from protobase import Consed, frozendict

from axis import src
from axis.dom.struct import Struct


class Builtin(Consed, abstract=True): ...


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
        return cls.from_ref(Anchor.from_str(value), underlying)


class NominalType(Type):
    ref: "Ref"

    @classmethod
    def from_ref(cls, ref: "Ref") -> "NominalType":
        return cls(ref=ref)

    @classmethod
    def from_str(cls, value: str) -> "NominalType":
        return cls.from_ref(Anchor.from_str(value))


class StructType(Type):
    """
    def Struct[...]:
    extends Type
    takes:
        fields: Struct[I] Type
    where:
        val I: Struct.Index
    """

    fields: Struct[str, "Type"]


class FnType(Type):
    args: tuple["Type", ...]
    ret: "Type"


class UnionType(Type):
    members: tuple["Type", ...]


class Val(Consed, abstract=True):
    pass


class Pure[T: Type = Type, D: Data = Data](Val, abstract=True):
    type: T
    data: D


class Const(Pure):

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


class Ref(Pure, abstract=True):
    class Type(Type, abstract=True):
        ...

    class Data(Builtin, abstract=True):
        ...

    @property
    def is_anchor(self) -> bool:
        return isinstance(self, Anchor)

    @property
    def anchor(self) -> "Anchor":
        if isinstance(self, Anchor):
            return self
        return cast(Spec, self).anchor

    def __rich__(self):
        from axis.tui.dom_render import render_ref

        return render_ref(self)

    def __str__(self) -> str:
        from axis.tui.dom_render import format_ref

        return format_ref(self)


class Anchor(Ref):
    class Type(Ref.Type):
        parent: "Anchor.Type | None" = None

    class Data(Ref.Data):
        parent: "Anchor.Data | None"
        member: str

    @classmethod
    def from_parts(cls, member: str, *, parent: "Anchor | None" = None) -> "Anchor":
        parent_type = cast(Anchor.Type, parent.type) if parent else None
        anchor_type = Anchor.Type(parent=parent_type)
        anchor_data = Anchor.Data(
            parent=None if parent is None else cast(Anchor.Data, parent.data),
            member=member,
        )
        return cls(type=anchor_type, data=anchor_data)

    @classmethod
    def root(cls, name: str) -> "Anchor":
        anchor_type = Anchor.Type(parent=None)
        anchor_data = Anchor.Data(parent=None, member=name)
        return cls(type=anchor_type, data=anchor_data)

    @classmethod
    def from_str(cls, value: str) -> "Anchor":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Anchor.from_str requires at least one segment")
        ref = cls.root(segments[0])
        for segment in segments[1:]:
            ref = ref.child(segment)
        return ref

    def child(self, name: str) -> "Anchor":
        return Anchor.from_parts(name, parent=self)

    def specialize(self, spec: Const | None) -> "Spec":
        if spec is None:
            spec_type = None
            spec_data = None
        else:
            if not isinstance(spec.type, StructType):
                raise TypeError("Anchor.specialize requires a StructType value")
            if not isinstance(spec.data, tuple):
                raise TypeError("Anchor.specialize requires tuple data")
            spec_type = spec.type
            spec_data = spec.data
        return Spec(
            type=Spec.Type(anchor=cast(Anchor.Type, self.type), spec=spec_type),
            data=Spec.Data(anchor=cast(Anchor.Data, self.data), spec=spec_data),
        )

    @property
    def parent(self) -> "Anchor | None":
        data = cast(Anchor.Data, self.data)
        parent_data = data.parent
        if parent_data is None:
            return None
        parent_type = cast(Anchor.Type, self.type).parent
        if parent_type is None:
            raise TypeError("Anchor has parent data but no parent type")
        return Anchor(type=parent_type, data=parent_data)

    def __invariants__(self) -> None:
        if not isinstance(self.type, Anchor.Type):
            raise TypeError(
                f"Anchor.type must be Anchor.Type, got {type(self.type).__name__}"
            )
        data = cast(Anchor.Data, self.data)
        parent_data = data.parent
        member = data.member
        if not isinstance(member, str) or not member:
            raise TypeError("Anchor.member must be a non-empty string")
        if parent_data is None:
            if self.type.parent is not None:
                raise TypeError("Anchor.Type parent is set but data has no parent")
        else:
            if self.type.parent is None:
                raise TypeError("Anchor.Type parent is None but data has a parent")


class Spec(Ref):
    class Type(Ref.Type):
        anchor: Anchor.Type
        spec: StructType | None = None

    class Data(Ref.Data):
        anchor: Anchor.Data
        spec: tuple[Data, ...] | None

    @property
    def anchor(self) -> Anchor:
        spec_type = cast(Spec.Type, self.type)
        spec_data = cast(Spec.Data, self.data)
        return Anchor(type=spec_type.anchor, data=spec_data.anchor)

    @property
    def parent(self) -> Anchor:
        return self.anchor

    @property
    def spec(self) -> Const | None:
        spec_type = cast(Spec.Type, self.type)
        spec_data = cast(Spec.Data, self.data)
        if spec_type.spec is None or spec_data.spec is None:
            return None
        return Const.from_type_data(spec_type.spec, spec_data.spec)

    def __invariants__(self) -> None:
        if not isinstance(self.type, Spec.Type):
            raise TypeError(
                f"Spec.type must be Spec.Type, got {type(self.type).__name__}"
            )
        if not isinstance(self.data, Spec.Data):
            raise TypeError(
                f"Spec.data must be Spec.Data, got {type(self.data).__name__}"
            )
        data = cast(Spec.Data, self.data)
        type_ = cast(Spec.Type, self.type)
        if data.anchor is None:
            raise TypeError("Spec.anchor data must be set")
        if type_.anchor is None:
            raise TypeError("Spec.anchor type must be set")
        if data.spec is None:
            if type_.spec is not None:
                raise TypeError("Spec type has spec but data is None")
            return
        if type_.spec is None:
            raise TypeError("Spec data has spec but type is None")
        if not isinstance(data.spec, tuple):
            raise TypeError("Spec.spec data must be a tuple")
        if len(data.spec) != len(type_.spec.fields.values):
            raise TypeError("Spec spec length does not match Spec.Type spec")


class Err(Val):
    diagnostic: src.Diagnostic | None = None


class Var(Val):
    class Type(Type):
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


class Bound(Pure):
    type: Type
    data: Data

    @classmethod
    def from_literal(cls, value: Data) -> "Bound":
        literal = Const.from_literal(value)
        return cls(type=literal.type, data=literal.data)

    @classmethod
    def from_ref(cls, ref: Ref) -> "Bound":
        return cls(type=ref.type, data=ref.data)

    @classmethod
    def var(cls, ident: str) -> "Bound":
        return cls(type=Var.Type(id=ident), data=ident)

    def __invariants__(self) -> None:
        if not _is_data(self.data):
            raise TypeError(f"Bound.data must be primitive, got {type(self.data)}")


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
    anchor = ref.anchor
    current = cast(Anchor.Data | None, anchor.data)
    while current is not None:
        segments.append(current.member)
        current = current.parent
    return tuple(reversed(segments))


if __name__ == "__main__":
    from rich import print

    std = Anchor.root("std").child("io").child("console").child("print")
    print(std)
