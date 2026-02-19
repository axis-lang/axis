from __future__ import annotations
from typing import TypeAlias, Union as TypingUnion
from protobase import Record, frozendict
#from protobase.inmutable import inmutable, register_inmutable
from axis.dom.tuple_ import Tuple, Shape, Index


class Node(Record, frozen=True, consed=True, abstract=True): ...


type Atom = TypingUnion[int, float, str, bool, None]
type Data = TypingUnion[Atom, tuple, frozenset, frozendict]

class Ref(Record, frozen=True, consed=True):
    member: str
    parent: "Ref | None" = None
    params: Tuple[str, "Val"] = Tuple.EMPTY

    @classmethod
    def from_str(cls, value: str) -> "Ref":
        parts = [part.strip() for part in value.split(".")]
        segments = tuple(part for part in parts if part)
        if not segments:
            raise ValueError("Ref.from_str requires at least one segment")
        ref = cls(parent=None, member=segments[0])
        for segment in segments[1:]:
            ref = ref.member_ref(segment)
        return ref

    @property
    def segments(self) -> tuple[str, ...]:
        if self.parent is None:
            return (self.member,)
        return self.parent.segments + (self.member,)

    def member_ref(self, name: str, *, params: Tuple[str, "Val"] = Tuple.EMPTY) -> "Ref":
        return Ref(parent=self, member=name, params=params)

    def to_val(self) -> "Const":
        parent_data = None if self.parent is None else self.parent.to_val().data
        params_data = tuple(p.data for p in self.params.values)
        data = (parent_data, self.member, params_data)
        return Const(meta=_ref_value_meta(self), data=data)


class TypeForm(Record, frozen=True, consed=True, abstract=True): ...


class Nominal(TypeForm, frozen=True, consed=True):
    ref: Ref


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


def _std_nominal(ref: Ref) -> Type:
    return Type(form=Nominal(ref=ref))


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
        payload: Data = form.ref.to_val().data
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


def _ref_value_meta(ref: Ref) -> Type:
    if ref.parent is None:
        parent_val = Const(meta=Type(form=Literal(None)), data=None)
    else:
        parent_val = ref.parent.to_val()

    params_type_meta = Type(
        form=Struct(
            fields=Tuple(
                index=ref.params.index,
                values=tuple(_std_type_meta() for _ in ref.params.values),
            )
        )
    )
    params_type_val = Const(
        meta=params_type_meta,
        data=tuple(p.meta.to_val().data for p in ref.params.values),
    )
    std_ref_ref = Ref.from_str("std.Ref")
    std_ref_params = Tuple.new(parent_val, params_type_val)
    std_ref_ref = Ref(parent=std_ref_ref.parent, member=std_ref_ref.member, params=std_ref_params)
    return Type(form=Nominal(ref=std_ref_ref))
