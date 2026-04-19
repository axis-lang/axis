from __future__ import annotations

import builtins as _builtins

import protomorph.core as _pm

from .type_ import *
from .placeholder import *
from .tuple_like import *
from .uniform import *
from .union import *
from .varying import *
from .indexed import *
from .shape import *
from .spec import *
from .qual import *


any: Spec
tuple: Spec
index: Spec
never: Spec
integer: Spec
text: Spec
decimal: Spec
boolean: Spec
empty: Spec
id: Spec
anchor: Spec


def _as_type(value: _pm.Type | _pm.Val[_pm.Type]) -> _pm.Type:
    return value.content if isinstance(value, _pm.Val) else value


def named(anchor: _pm.Anchor | str, *args, **kwargs) -> Spec:
    return Spec.of(anchor, *args, **kwargs)


def qualify(*qualifiers: Spec, under: _pm.Type | _pm.Val[_pm.Type]) -> Qual:
    return Qual.of(_as_type(under), *qualifiers)


def optional(inner: _pm.Type | _pm.Val[_pm.Type]) -> Qual:
    return qualify(Spec.of(_pm.anchors.optional), under=inner)


# def list(inner: _pm.Type | _pm.Val[_pm.Type]) -> Qual:
#     return qualify(Spec.of(_pm.anchors.list), under=inner)


def set(inner: _pm.Type | _pm.Val[_pm.Type]) -> Qual:
    return qualify(Spec.of(_pm.anchors.set), under=inner)


def map(
    value: _pm.Type | _pm.Val[_pm.Type],
    *,
    key: _pm.Type | _pm.Val[_pm.Type] | None = None,
) -> Qual:
    key_type = any if key is None else _as_type(key)
    return qualify(Spec.of(_pm.anchors.map, key_type), under=value)


def result(
    ok: _pm.Type | _pm.Val[_pm.Type],
    *,
    err: _pm.Type | _pm.Val[_pm.Type] | None = None,
) -> Qual:
    err_type = never if err is None else _as_type(err)
    return qualify(Spec.new(_pm.anchors.result, Err=_pm.val(err_type)), under=ok)


def union(*variants: _pm.Type | _pm.Val[_pm.Type]) -> _pm.Type:
    normalized = _builtins.tuple(
        _as_type(variant) for variant in variants
    )
    return Union.of(*normalized)


def uniform(
    element: _pm.Type | _pm.Val[_pm.Type],
    *,
    unique: bool = False,
) -> Uniform:
    return Uniform(_as_type(element), unique=unique)


def varying(*items: _pm.Type | _pm.Val[_pm.Type]) -> Varying:
    return Varying.of(*(_as_type(item) for item in items))


def indexed(*items: _pm.Type | _pm.Val[_pm.Type], **named_items: _pm.Type | _pm.Val[_pm.Type]) -> Indexed:
    normalized_items = _builtins.tuple(_as_type(item) for item in items)
    normalized_named_items = {
        key: _as_type(value)
        for key, value in named_items.items()
    }
    return Indexed.of(*normalized_items, **normalized_named_items)


__all__ = [
    "Type",
    "compatible",
    "Placeholder",
    "Var",
    "Mark",
    "Op",
    "WildcardMark",
    "EllipsisMark",
    "SelfMark",
    "PlaceholderMetatype",
    "SimpleVar",
    "var",
    "WILDCARD",
    "ELLIPSIS",
    "SELF",
    "TupleLike",
    "Uniform",
    "Union",
    "Varying",
    "Indexed",
    "Shape",
    "Spec",
    "Qual",
    "any",
    "tuple",
    "index",
    "never",
    "integer",
    "text",
    "decimal",
    "boolean",
    "empty",
    "id",
    "anchor",
    "named",
    "qualify",
    "optional",
    #"list",
    "set",
    "map",
    "result",
    "union",
    "uniform",
    "varying",
    "indexed",
]
