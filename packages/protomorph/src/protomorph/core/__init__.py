from __future__ import annotations

from typing import cast

from protobase import flux as _flux

from decimal import Decimal
from types import NoneType

from .foundation import *
from .types import *
from .values import *
from .native import *
from .realm import *
from .traversal import *




NATIVE_REALM = NativeRealm()
REALM = _flux.contextvar("pm.REALM", default=cast(Realm, NATIVE_REALM))


VaryingType.Empty = VaryingType(())
Tuple.Empty = Tuple._new(VaryingType.Empty, ())
Spec.Any = Spec.of("std.types.Any")
Spec.Tuple = Spec.of("std.types.Tuple")
Spec.Index = Spec.of("std.types.Index")
Spec.Never = Spec.of("std.types.Never")
Spec.Integer = Spec.of("std.types.Integer")
Spec.Text = Spec.of("std.types.Text")
Spec.Decimal = Spec.of("std.types.Decimal")
Spec.Boolean = Spec.of("std.types.Boolean")
Spec.Empty = Spec.of("std.types.Empty")
Spec.Id = Spec.of("std.types.Id")
Spec.Anchor = Spec.of("std.types.Anchor")
Option.qualifier = Spec.of("std.qualifiers.Optional")


register_native_spec(int, Spec.Integer)
register_native_spec(str, Spec.Text)
register_native_spec(float, Spec.Decimal)
register_native_spec(Decimal, Spec.Decimal)
register_native_spec(bool, Spec.Boolean)
register_native_spec(NoneType, Spec.Empty)
register_native_spec(Id, Spec.Id)
register_native_spec(Anchor, Spec.Anchor)


def _set_transform(value_type: Type) -> Type:
    return cast(
        Type,
        Qual.of(value_type, Spec.of("std.qualifiers.Set")),
    )


def _map_transform(key_type: Type, value_type: Type) -> Type:
    return cast(
        Type,
        Qual.of(value_type, Spec.of("std.qualifiers.Map", key_type)),
    )


def _list_transform(value_type: Type) -> Type:
    return cast(
        Type,
        Qual.of(value_type, Spec.of("std.qualifiers.List")),
    )


def _frozenset_transform(value_type: Type) -> Type:
    return cast(
        Type,
        Qual.of(value_type, Spec.of("std.qualifiers.Set")),
    )


def _tuple_transform(*types: Type | object) -> Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(Type, UniformType(cast(Type, types[0])))
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(
        Type,
        VaryingType(cast(tuple[Type, ...], types)),
    )


def _result_transform(err_type: Type, ok_type: Type) -> Type:
    return cast(
        Type,
        Qual(Result.qualifier(val(err_type)), ok_type),
    )


register_python_transform(dict, _map_transform)
register_python_transform(list, _list_transform)
register_python_transform(set, _set_transform)
register_python_transform(frozenset, _frozenset_transform)
register_python_transform(tuple, _tuple_transform)
register_python_transform(Result, _result_transform)


Wildcard = val(WILDCARD)
