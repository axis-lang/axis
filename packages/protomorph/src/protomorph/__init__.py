from __future__ import annotations

from contextvars import ContextVar
from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import Any, cast, get_origin

from protobase import frozendict

from .format import format_morph
from .map import *
from .struct import *
from .base import *
from .subst import _subst_spec, _subst_type, as_type, subst_val
from .types import *
from .qualifiers import *
from .refs import *
from .vars import *
from .bridge import *
from .errors import *

ANY_TYPE: Type
EMPTY_TYPE: Type
INTEGER_TYPE: Type
TEXT_TYPE: Type
EMPTY_STRUCT_TYPE: StructType
EmptyStruct: Const[StructType]
_ANCHOR_TYPE: AnchorType
NATIVE_REGISTRY: NativeRegistry
NATIVE_BACKEND: NativeBackend
DEFAULT_BRIDGE: SemanticBridge
BRIDGE: ContextVar[SemanticBridge]


def _empty_struct_type() -> StructType:
    try:
        return EMPTY_STRUCT_TYPE
    except NameError:
        return StructType(meta_attrs=Struct.Empty)


def spec(*positional: type | Type | Const | Var, **nominal: type | Type | Const | Var) -> Const[StructType]:
    if not positional and not nominal:
        return EmptyStruct

    def as_spec_value(value: type | Type | Const | Var) -> Const | Var:
        if isinstance(value, (Const, Var)):
            return value
        return cast(Const | Var, val(type_(value)))

    return struct(
        *[as_spec_value(item) for item in positional],
        **{key: as_spec_value(item) for key, item in nominal.items()},
    )


def type_(annotation: type | Type) -> Type:
    if isinstance(annotation, Type):
        return annotation
    return type_from_python(annotation)


def anchor(path: str) -> Anchor:
    return Anchor(_ANCHOR_TYPE, tuple(path.split(".")))


def spec_ref(anchor_: str | Anchor, spec: Const | None = None) -> Spec:
    if isinstance(anchor_, str):
        anchor_ = anchor(anchor_)

    spec = EmptyStruct if spec is None else spec
    assert isinstance(spec.__type__, StructType)
    assert isinstance(spec.__data__, tuple)
    return Spec(
        SpecType(meta_args=spec.__type__),
        (anchor_.segments, spec.__data__),
    )


def struct(*positional: Const | Var, **nominal: Const | Var) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal)
    struct_type = StructType(
        meta_attrs=fields.map(lambda x: x if isinstance(x, Var) else x.__type__),
    )
    return cast(
        Const[StructType], struct_type._wrap(fields.map(lambda x: x.__data__).values)
    )


def struct_value(*positional: Const | Var, **nominal: Const | Var) -> Const[StructType]:
    return struct(*positional, **nominal)


def struct_type(*positional: type | Type, **nominal: type | Type) -> StructType:
    return StructType(
        meta_attrs=Struct.new(
            *[type_(item) for item in positional],
            **{key: type_(item) for key, item in nominal.items()},
        )
    )


def literal(value: Literal | None) -> Const:
    type_ = NATIVE_REGISTRY.native_types.get(type(value))
    if type_ is None:
        raise TypeError(f"Unsupported literal type: {type(value).__name__}")
    return cast(Const, type_._wrap(value))


def literal_struct(*positional: Literal, **nominal: Literal) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal).map(literal)
    struct_type = StructType(meta_attrs=fields.map(lambda x: x.__type__))
    return cast(
        Const[StructType], struct_type._wrap(fields.map(lambda x: x.__data__).values)
    )


def struct_literal(*positional: Literal, **nominal: Literal) -> Const[StructType]:
    return literal_struct(*positional, **nominal)


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
    discriminator = active if isinstance(active, Var) else active.__type__
    if discriminator not in active_union_type.types:
        raise TypeError(
            f"Active variant type {discriminator} is not in the union types"
        )
    return cast(Const[UnionType], active_union_type._wrap((discriminator, active.__data__)))


def union_value(*types: type | Type, active: type | Type | Const | Var | Literal) -> Const[UnionType]:
    union_types = frozenset(type_(item) for item in types)
    active_value = active if isinstance(active, (Const, Var)) else cast(Const | Var, val(active))
    return union(union_types, active_value)


def nominal_type(anchor_: str | Anchor, args: Const | None = None) -> NominalType:
    return NominalType(spec_ref=spec_ref(anchor_, args))


def nominal_qual(
    anchor_: str | Anchor,
    args: Const | None = None,
    *,
    underlying: Type,
) -> NominalQualifier:
    return NominalQualifier(spec_ref=spec_ref(anchor_, args), underlying=underlying)


def val(*positional, **nominal) -> Val:
    def as_const(value, where: str) -> Const | Var:
        coerced = val(value)
        if not isinstance(coerced, (Const, Var)):
            raise ValueError(
                f"protomorph.val expected Const/Var value for {where}, got {type(coerced).__name__}"
            )
        return coerced

    try:
        if not positional and not nominal:
            raise ValueError("protomorph.val requires at least one value")

        if len(positional) != 1 or nominal:
            args = [
                as_const(item, f"positional[{i}]") for i, item in enumerate(positional)
            ]
            kwargs = {
                key: as_const(item, f"key {key!r}") for key, item in nominal.items()
            }
            return struct(*args, **kwargs)

        value = positional[0]
        if isinstance(value, Val):
            return value
        if isinstance(value, Type):
            return value._metatype()._wrap(value)

        origin = get_origin(value)
        if value is Any or isinstance(value, type) or origin is not None:
            return val(type_from_python(value))

        try:
            literal_type_token = NATIVE_REGISTRY.native_types.get(value)
        except TypeError:
            literal_type_token = None
        if literal_type_token is not None:
            return val(literal_type_token)

        literal_type = NATIVE_REGISTRY.native_types.get(type(value))
        if literal_type is not None:
            return literal_type._wrap(value)

        if isinstance(value, (dict, frozendict)):
            kwargs: dict[str, Const | Var] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError(
                        "protomorph.val only supports dict/frozendict with string keys"
                    )
                kwargs[key] = as_const(item, f"key {key!r}")
            return struct(**kwargs)

        if isinstance(value, (tuple, list)):
            return struct(
                *[as_const(item, f"sequence[{i}]") for i, item in enumerate(value)]
            )

        if isinstance(value, Builtin):
            runtime_args = builtin_runtime_type_args(value)
            typed_runtime_args = cast(tuple[type | Type, ...], runtime_args)
            builtin_type = value._type(*typed_runtime_args) if runtime_args is not None else value._type()
            return builtin_type._wrap(value)

        raise ValueError(
            f"protomorph.val does not support value of type {type(value).__name__}"
        )
    except ValueError:
        raise


def type_of(value: Val) -> Const:
    return cast(Const, val(value.__type__))


def native_type(type_: type[Literal] | None) -> Type:
    if type_ is None:
        type_ = type(None)
    if type_ not in NATIVE_REGISTRY.native_types:
        raise TypeError(f"No protomorph type mapping for native type {type_.__name__}")
    return NATIVE_REGISTRY.native_types[type_]


def encode(value: Val, format: str | None = None) -> Data:
    return value.encode(format)


import protomorph.native as native
from .native import *


def _bootstrap() -> None:
    global ANY_TYPE, EMPTY_TYPE, INTEGER_TYPE, TEXT_TYPE, EMPTY_STRUCT_TYPE, EmptyStruct
    global NATIVE_REGISTRY, NATIVE_BACKEND, DEFAULT_BRIDGE, BRIDGE

    if native._BOOTSTRAPPED:
        return

    global _ANCHOR_TYPE
    _ANCHOR_TYPE = AnchorType()
    EMPTY_STRUCT_TYPE = StructType(meta_attrs=Struct.Empty)
    EmptyStruct = cast(Const[StructType], EMPTY_STRUCT_TYPE._wrap(()))
    NATIVE_REGISTRY = NativeRegistry()
    NATIVE_BACKEND = NativeBackend(registry=NATIVE_REGISTRY)
    DEFAULT_BRIDGE = NATIVE_BACKEND
    BRIDGE = ContextVar("protomorph.BRIDGE", default=DEFAULT_BRIDGE)

    empty_type = nominal_type("std.Empty")
    boolean_type = nominal_type("std.Boolean")
    integer_type = nominal_type("std.Integer")
    decimal_type = nominal_type("std.Decimal")
    text_type = nominal_type("std.Text")
    any_type = nominal_type("std.Any")

    EMPTY_TYPE = empty_type
    INTEGER_TYPE = integer_type
    TEXT_TYPE = text_type
    ANY_TYPE = any_type

    register_native_type(bool, boolean_type)
    register_native_type(int, integer_type)
    register_native_type(float, decimal_type)
    register_native_type(str, text_type)
    register_native_type(type(None), empty_type)
    register_native_type(Decimal, decimal_type)

    def set_transform(value_type: Type) -> Type:
        return nominal_qual("std.Set", native._spec_from_types(), underlying=value_type)

    def map_transform(key_type: Type, value_type: Type) -> Type:
        return nominal_qual("std.Map", native._spec_from_types(K=key_type), underlying=value_type)

    def list_transform(value_type: Type) -> Type:
        return nominal_qual("std.List", native._spec_from_types(), underlying=value_type)

    def union_transform(*types: Type) -> Type:
        return union_type(*types)

    register_python_type(dict, map_transform)
    register_python_type(frozendict, map_transform)
    register_python_type(list, list_transform)
    register_python_type(set, set_transform)
    register_python_type(frozenset, set_transform)
    register_python_type(tuple, native._tuple_transform)
    register_python_type(cast(type, PEP604Union), union_transform)

    register_atomic_layout("std.Empty", AtomicLayout(valid_types=frozenset({NoneType})))
    register_atomic_layout("std.Boolean", AtomicLayout(valid_types=frozenset({bool})))
    register_atomic_layout("std.Natural", AtomicLayout(valid_types=frozenset({int})))
    register_atomic_layout("std.Whole", AtomicLayout(valid_types=frozenset({int})))
    register_atomic_layout("std.Integer", AtomicLayout(valid_types=frozenset({int})))
    register_atomic_layout("std.Decimal", AtomicLayout(valid_types=frozenset({int, float, Decimal})))
    register_atomic_layout("std.Text", AtomicLayout(valid_types=frozenset({str})))

    native._BOOTSTRAPPED = True


_bootstrap()
