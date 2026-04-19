from __future__ import annotations

import builtins as _builtins
from typing import cast

from protobase import flux as _flux

from decimal import Decimal
from types import NoneType

from . import anchors
from .foundation import *
from . import types
from .types import (
    Schema,
    Type,
    compatible,
    Placeholder,
    Var,
    Mark,
    Op,
    WildcardMark,
    EllipsisMark,
    SelfMark,
    PlaceholderMetatype,
    SimpleVar,
    var,
    WILDCARD,
    ELLIPSIS,
    SELF,
    TupleLike,
    Uniform,
    Union,
    Varying,
    Indexed,
    Shape,
    Spec,
    Qual,
)
from .values import *
from .native import *
from .realm import *
from .traversal import *


NATIVE_REALM = NativeRealm()
REALM = _flux.contextvar("pm.REALM", default=cast(Realm, NATIVE_REALM))


Varying.Empty = Varying(())
Tuple.Empty = Tuple._new(Varying.Empty, ())
types.any = Spec.of(anchors.any)
types.tuple = Spec.of(anchors.tuple)
types.index = Spec.of(anchors.index)
types.never = Spec.of(anchors.never)
types.integer = Spec.of(anchors.integer)
types.text = Spec.of(anchors.text)
types.decimal = Spec.of(anchors.decimal)
types.boolean = Spec.of(anchors.boolean)
types.empty = Spec.of(anchors.empty)
types.id = Spec.of(anchors.id)
types.anchor = Spec.of(anchors.anchor)

Spec.Any = types.any
Spec.Tuple = types.tuple
Spec.Index = types.index
Spec.Never = types.never
Spec.Integer = types.integer
Spec.Text = types.text
Spec.Decimal = types.decimal
Spec.Boolean = types.boolean
Spec.Empty = types.empty
Spec.Id = types.id
Spec.Anchor = types.anchor


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
        types.set(value_type),
    )


def _map_transform(key_type: Type, value_type: Type) -> Type:
    return types.map(value_type, key=key_type)


# def _list_transform(value_type: Type) -> Type:
#     return types.list(value_type)


def _frozenset_transform(value_type: Type) -> Type:
    return cast(
        Type,
        types.set(value_type),
    )


def _tuple_transform(*items: Type | object) -> Type:
    if len(items) == 2 and items[1] is Ellipsis:
        return cast(Type, Uniform(cast(Type, items[0])))
    if _builtins.any(type_ is Ellipsis for type_ in items):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(
        Type,
        Varying(cast(tuple, items)),
    )


def _result_transform(err_type: Type, ok_type: Type) -> Type:
    return cast(
        Type,
        types.result(ok_type, err=err_type),
    )


register_python_transform(_builtins.dict, _map_transform)
#register_python_transform(_builtins.list, _list_transform)
register_python_transform(_builtins.set, _set_transform)
register_python_transform(_builtins.frozenset, _frozenset_transform)
register_python_transform(_builtins.tuple, _tuple_transform)
register_python_transform(Result, _result_transform)


Wildcard = val(WILDCARD)
