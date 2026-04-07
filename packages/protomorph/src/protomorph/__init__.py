from __future__ import annotations

from typing import Any, cast

from protobase import flux 

from . import match
from .abstract import contract
from .abstract.contract import Item
from .domain import *

from .carriers import *
from .constraint import Constraint
from .native import *
#from .native import _bootstrap_defaults
from .realm import *
from .traversal import *
from .unification import *


NATIVE_REALM = NativeRealm()
REALM = flux.contextvar("pm.REALM", default=NATIVE_REALM)

#_bootstrap_defaults()


assert issubclass(Type, contract.Descriptor)


VaryingType.Empty = VaryingType(())
Tuple.Empty = Tuple._new(pm.VaryingType.Empty, ())



register_native_spec(int, protomorph.Spec.of("std.types.Integer"))
register_native_spec(str, protomorph.Spec.of("std.types.Text"))
register_native_spec(float, protomorph.Spec.of("std.types.Decimal"))
register_native_spec(Decimal, protomorph.Spec.of("std.types.Decimal"))
register_native_spec(bool, protomorph.Spec.of("std.types.Boolean"))
register_native_spec(NoneType, protomorph.Spec.of("std.types.Empty"))
register_native_spec(Id, protomorph.Spec.of("std.types.Id"))
register_native_spec(Anchor, protomorph.Spec.of("std.types.Anchor"))


def _set_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.Set")))


def _map_transform(key_type: protomorph.Type, value_type: protomorph.Type) -> protomorph.Type:
    return cast(
        protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.Map", key_type))
    )


def _list_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.List")))


def _frozenset_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.FrozenSet")))


def _tuple_transform(*types: protomorph.Type | object) -> protomorph.Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(protomorph.Type, protomorph.UniformType(cast(protomorph.Type, types[0])))
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(protomorph.Type, protomorph.VaryingType(cast(tuple[protomorph.Type, ...], types)))


def _result_transform(err_type: protomorph.Type, ok_type: protomorph.Type) -> protomorph.Type:
    return cast(
        protomorph.Type,
        protomorph.Qual.of(ok_type, protomorph.Spec.of("std.qualifiers.Result", err_type)),
    )


register_python_transform(dict, _map_transform)
register_python_transform(list, _list_transform)
register_python_transform(set, _set_transform)
register_python_transform(frozenset, _frozenset_transform)
register_python_transform(tuple, _tuple_transform)
register_python_transform(protomorph.Result, _result_transform)
