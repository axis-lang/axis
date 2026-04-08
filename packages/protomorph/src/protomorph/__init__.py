from __future__ import annotations

from typing import cast

from protobase import flux as _flux

from . import match
from .abstract import contract
from .abstract.contract import Item
from .domain import *
from .native import *
from .realm import *
from .traversal import *
from .unification import *
from .values import *
from .constraint import Constraint

assert issubclass(Type, contract.Descriptor)


NATIVE_REALM = NativeRealm()
REALM = _flux.contextvar("pm.REALM", default=NATIVE_REALM)


VaryingType.Empty = VaryingType(())
Tuple.Empty = Tuple._new(pm.VaryingType.Empty, ())


register_native_spec(int, Spec.of("std.types.Integer"))
register_native_spec(str, Spec.of("std.types.Text"))
register_native_spec(float, Spec.of("std.types.Decimal"))
register_native_spec(Decimal, Spec.of("std.types.Decimal"))
register_native_spec(bool, Spec.of("std.types.Boolean"))
register_native_spec(NoneType, Spec.of("std.types.Empty"))
register_native_spec(Id, Spec.of("std.types.Id"))
register_native_spec(Anchor, Spec.of("std.types.Anchor"))


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
        Qual.of(value_type, Spec.of("std.qualifiers.FrozenSet")),
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
        Qual.of(ok_type, Spec.of("std.qualifiers.Result", err_type)),
    )


register_python_transform(dict, _map_transform)
register_python_transform(list, _list_transform)
register_python_transform(set, _set_transform)
register_python_transform(frozenset, _frozenset_transform)
register_python_transform(tuple, _tuple_transform)
register_python_transform(Result, _result_transform)
