from __future__ import annotations
from typing import TypeAlias, Union as TypingUnion
from protobase import Record, frozendict
#from protobase.inmutable import inmutable, register_inmutable
from axis.dom.tuple_ import Tuple, Shape, Index


class Node(Record, frozen=True, consed=True, abstract=True): ...


type Atom = TypingUnion[int, float, str, bool, None]
type Data = TypingUnion[Atom, tuple, frozenset, frozendict]

class Ref(Record, frozen=True, consed=True):
    segments: tuple[str, ...]

    @classmethod
    def from_str(cls, value: str) -> "Ref":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Ref.from_str requires at least one segment")
        return cls(segments=segments)

    @property
    def parent(self) -> "Ref":
        if len(self.segments) <= 1:
            return Ref(segments=())
        return Ref(segments=self.segments[:-1])

    def member(self, name: str) -> "Ref":
        return Ref(segments=self.segments + (name,))

    def to_val(self) -> "Const":
        return Const(meta=_std_ref_meta(), data=self.segments)


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

    @classmethod
    def Var(cls, ident: str) -> "Type":
        return cls(form=TypeVar(id=ident))

    def to_val(self) -> "Const":
        qualifiers_data = tuple(q.to_val().data for q in self.qualifiers)
        form_data = _encode_typeform(self.form)
        return Const(meta=_std_type_meta(), data=("type", (qualifiers_data, form_data)))


type Meta = Type


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


def _empty_params() -> Const:
    return Const(meta=Type(form=Struct(fields=Tuple.EMPTY)), data=())


def _std_nominal(ref: Ref) -> Type:
    return Type(form=Nominal(ref=ref, params=_empty_params(), schema=None))


def _std_type_meta() -> Type:
    return _std_nominal(Ref.from_str("std.Type"))


def _std_ref_meta() -> Type:
    return _std_nominal(Ref.from_str("std.Ref"))


def _typeform_tag_data(form: TypeForm) -> Data:
    if isinstance(form, Nominal):
        return Ref.from_str("std.Type.Nominal").to_val().data
    if isinstance(form, Struct):
        return Ref.from_str("std.Type.Struct").to_val().data
    if isinstance(form, Function):
        return Ref.from_str("std.Type.Function").to_val().data
    if isinstance(form, Union):
        return Ref.from_str("std.Type.Union").to_val().data
    if isinstance(form, Literal):
        return Ref.from_str("std.Type.Literal").to_val().data
    if isinstance(form, TypeVar):
        return Ref.from_str("std.Type.Var").to_val().data
    raise TypeError(f"Unsupported TypeForm: {type(form)}")


def _encode_typeform(form: TypeForm) -> tuple[Data, Data]:
    tag_data = _typeform_tag_data(form)
    if isinstance(form, Nominal):
        schema_data = None if form.schema is None else form.schema.to_val().data
        payload: Data = (form.ref.to_val().data, form.params.data, schema_data)
        return (tag_data, payload)
    if isinstance(form, Struct):
        index_data = tuple(form.fields.index.keys)
        fields_data = tuple(t.to_val().data for t in form.fields.values)
        return (tag_data, (index_data, fields_data))
    if isinstance(form, Function):
        args_data = tuple(t.to_val().data for t in form.args)
        ret_data = form.ret.to_val().data
        return (tag_data, (args_data, ret_data))
    if isinstance(form, Union):
        members_data = tuple(t.to_val().data for t in form.members)
        return (tag_data, (members_data,))
    if isinstance(form, Literal):
        return (tag_data, form.value)
    if isinstance(form, TypeVar):
        return (tag_data, form.id)
    raise TypeError(f"Unsupported TypeForm: {type(form)}")
