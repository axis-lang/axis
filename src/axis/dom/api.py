from __future__ import annotations

from typing import Any, cast, get_origin

from protobase import frozendict

from .base import Builtin, Const, Data, Literal, Val
from .errors import Err
from .qualifiers import NominalQualifier
from .refs import Anchor, Spec, SpecType
from .struct import Struct
from .types import (
    NominalType,
    StructType,
    Type,
    UnionType,
)
from .vars import ContextProto, Var


STRUCT_TYPE: Type
NOMINAL_TYPE: Type

EMPTY_TYPE: Type
BOOLEAN_TYPE: Type
NATURAL_TYPE: Type
WHOLE_TYPE: Type
INTEGER_TYPE: Type
DECIMAL_TYPE: Type
TEXT_TYPE: Type

ANY_TYPE: Type
MAP_TYPE: Type
SET_TYPE: Type
LIST_TYPE: Type

TYPE_BY_NATIVE: dict[object, Type] = {}
LITERAL_TYPES = TYPE_BY_NATIVE


def anchor(path: str) -> Anchor:
    return Anchor(data=tuple(path.split(".")))


def spec_ref(anchor_: str | Anchor, spec: Const | None = None) -> Spec:
    if isinstance(anchor_, str):
        anchor_ = anchor(anchor_)
    anchor_value = cast(Anchor, anchor_)

    if spec is not None:
        assert isinstance(spec.type, StructType)
        assert isinstance(spec.data, tuple)
        return Spec(type=SpecType(meta_args=spec.type), data=(anchor_value.data, spec.data))

    return Spec(type=SpecType(meta_args=None), data=(anchor_value.data, None))


def struct(*positional: Const | Var, **nominal: Const | Var) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal)
    struct_type = StructType(
        meta_attrs=fields.map(lambda x: x if isinstance(x, Var) else x.type),
    )
    return cast(Const[StructType], struct_type.wrap(fields.map(lambda x: x.data).values))


def literal(value: Literal | None) -> Const:
    type_ = TYPE_BY_NATIVE.get(type(value))
    if type_ is None:
        raise TypeError(f"Unsupported literal type: {type(value).__name__}")
    return cast(Const, type_.wrap(value))


def literal_struct(*positional: Literal, **nominal: Literal) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal).map(literal)
    struct_type = StructType(meta_attrs=fields.map(lambda x: x.type))
    return cast(Const[StructType], struct_type.wrap(fields.map(lambda x: x.data).values))


def union_type(*types: Type) -> UnionType:
    flat: set[Type] = set()
    for type_ in types:
        if isinstance(type_, UnionType):
            flat.update(type_.types)
        else:
            flat.add(type_)
    return UnionType(types=frozenset(flat))


def union(types: frozenset[Type], active: Const | Var) -> Const[UnionType]:
    active_union_type = union_type(*types)
    discriminator = active if isinstance(active, Var) else active.type
    if discriminator not in active_union_type.types:
        raise TypeError(f"Active variant type {discriminator} is not in the union types")
    return cast(Const[UnionType], active_union_type.wrap((discriminator, active.data)))


def nominal_type(anchor_: str | Anchor, args: Const | None = None) -> NominalType:
    return NominalType(spec_ref=spec_ref(anchor_, args))


def nominal_qual(
    anchor_: str | Anchor,
    args: Const | None = None,
    *,
    underlying: Type,
) -> NominalQualifier:
    return NominalQualifier(spec_ref=spec_ref(anchor_, args), underlying=underlying)


class _ValContext(ContextProto):
    def lookup_bound(self, name: str) -> Type | None:
        return None


_VAL_CTX = _ValContext()


def val(*positional, **nominal) -> Val:
    from .interop import builtin_runtime_type_args, python_to_axis_type

    def as_const(value, where: str) -> Const | Var:
        coerced = val(value)
        if not isinstance(coerced, (Const, Var)):
            raise ValueError(
                f"dom.val expected Const/Var value for {where}, got {type(coerced).__name__}"
            )
        return coerced

    try:
        if not positional and not nominal:
            raise ValueError("dom.val requires at least one value")

        if len(positional) != 1 or nominal:
            args = [as_const(item, f"positional[{i}]") for i, item in enumerate(positional)]
            kwargs = {key: as_const(item, f"key {key!r}") for key, item in nominal.items()}
            return struct(*args, **kwargs)

        value = positional[0]
        if isinstance(value, Val):
            return value
        if isinstance(value, Type):
            return value._metatype().wrap(value)

        try:
            literal_type_token = LITERAL_TYPES.get(value)
        except TypeError:
            literal_type_token = None
        if literal_type_token is not None:
            return val(literal_type_token)

        literal_type = TYPE_BY_NATIVE.get(type(value))
        if literal_type is not None:
            return literal_type.wrap(value)

        origin = get_origin(value)
        if value is Any or isinstance(value, type) or origin is not None:
            return val(python_to_axis_type(value, ctx=_VAL_CTX))

        if isinstance(value, (dict, frozendict)):
            kwargs: dict[str, Const | Var] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("dom.val only supports dict/frozendict with string keys")
                kwargs[key] = as_const(item, f"key {key!r}")
            return struct(**kwargs)

        if isinstance(value, (tuple, list)):
            return struct(*[as_const(item, f"sequence[{i}]") for i, item in enumerate(value)])

        if isinstance(value, Builtin):
            builtin_cls = type(value)
            runtime_args = builtin_runtime_type_args(value)
            parameters = tuple(getattr(builtin_cls, "__parameters__", ()))

            if parameters and runtime_args is None:
                raise ValueError(
                    f"dom.val cannot infer type arguments for generic Builtin instance {builtin_cls.__name__}; instantiate with explicit type args"
                )

            builtin_type = builtin_cls._type(*runtime_args) if runtime_args is not None else builtin_cls._type()
            return builtin_type.wrap(value)

        raise ValueError(f"dom.val does not support value of type {type(value).__name__}")
    except ValueError:
        raise
    except Exception as exc:
        typename = type(positional[0]).__name__ if positional else "<struct>"
        raise ValueError(f"dom.val failed to convert {typename}") from exc


def type_of(value: Val) -> Const:
    return cast(Const, val(value.type))


def native_type(type_: type[Literal] | None) -> Type:
    if type_ is None:
        type_ = type(None)
    if type_ not in TYPE_BY_NATIVE:
        raise TypeError(f"No dom type mapping for native type {type_.__name__}")
    return TYPE_BY_NATIVE[type_]


def _encode(type_: Type, value) -> Data:
    match value:
        case Struct(values=values):
            value = values
        case Val(type=value_type, data=data):
            value = _encode(value_type, data)
        case Builtin():
            pass
    return type_._encode(value)


def _decode(type_: Type, raw_data):
    return type_._decode(raw_data)


def encode(value: Val) -> Val:
    if not isinstance(value, (Const, Err)):
        raise TypeError(f"dom.encode only supports Const/Err values, got {type(value).__name__}")
    return value.type.wrap(_encode(value.type, value.data))


def decode(value: Val) -> Val:
    if not isinstance(value, (Const, Err)):
        raise TypeError(f"dom.decode only supports Const/Err values, got {type(value).__name__}")
    return value.type.wrap(_decode(value.type, value.data))


def dir(value: Val) -> Struct[str, Type] | None:
    return value.type._dir(value.data)


def get(value: Val, key: str | int) -> Val:
    return value.type._get(value.data, key)
