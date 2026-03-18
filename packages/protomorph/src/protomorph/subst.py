from __future__ import annotations

from collections.abc import Callable
from typing import cast

from protobase import attrs_of, mutate

import protomorph as pm

__all__ = [
    "SubstEnv",
    "as_type",
    "subst_val",
]


type SubstEnv = Callable[[pm.Val], pm.Val | None]


def as_type(value: pm.Val | pm.Type | None) -> pm.Type | None:
    if value is None:
        return None
    if isinstance(value, pm.Type):
        return value
    if isinstance(value, pm.Const) and isinstance(value.__data__, pm.Type):
        return cast(pm.Type, value.__data__)
    if isinstance(value, pm.Anchor):
        return pm.nominal_type(value)
    if isinstance(value, pm.Spec):
        return pm.nominal_type(value.anchor, value._args_const())
    return None


def subst_val(value: pm.Val, env: SubstEnv) -> pm.Val:
    resolved = env(value)
    if resolved is not None:
        return resolved

    if isinstance(value, pm.Op):
        return _subst_op(value, env)

    if isinstance(value, pm.Spec):
        return _subst_spec(value, env)

    if isinstance(value, pm.Const):
        return _subst_const(value, env)

    return value


def _subst_op(value: pm.Op, env: SubstEnv) -> pm.Val:
    operator = _subst_builtin(value.__data__, env)
    if operator is value.__data__:
        return value
    assert isinstance(operator, pm.Operator)
    return pm.op(operator)


def _subst_builtin(value: pm.Builtin, env: SubstEnv) -> pm.Builtin:
    updates: dict[str, object] = {}
    for attr, attr_value in attrs_of(value).items():
        resolved = _subst_object(attr_value, env)
        if resolved != attr_value:
            updates[attr] = resolved
    return value if not updates else mutate(value, **updates)


def _subst_object(value: object, env: SubstEnv) -> object:
    if isinstance(value, pm.Val):
        return subst_val(value, env)
    if isinstance(value, pm.Type):
        return _subst_type(value, env)
    if isinstance(value, tuple):
        items = tuple(_subst_object(item, env) for item in value)
        return value if items == value else items
    if isinstance(value, frozenset):
        items = frozenset(_subst_object(item, env) for item in value)
        return value if items == value else items
    if isinstance(value, dict):
        items = {key: _subst_object(item, env) for key, item in value.items()}
        return value if items == value else items
    return value


def _subst_const(value: pm.Const, env: SubstEnv) -> pm.Val:
    data = value.__data__
    if isinstance(data, pm.Type):
        resolved_type = _subst_type(cast(pm.Type, data), env)
        if resolved_type is data:
            return value
        return pm.val(resolved_type)

    fields = _const_struct_fields(value)
    if fields is not None:
        resolved_fields = tuple(subst_val(field_value, env) for field_value in fields.values)
        if resolved_fields == fields.values:
            return value
        return _struct_const(pm.Struct.from_keys(fields.index.keys, resolved_fields))

    return value


def _const_struct_fields(value: pm.Const) -> pm.Struct[str | None, pm.Val] | None:
    if not isinstance(value.__type__, pm.StructType) or not isinstance(value.__data__, tuple):
        return None
    meta_attrs = value.__type__.meta_attrs
    values = tuple(
        field_type._wrap(field_data)
        for field_type, field_data in zip(meta_attrs.values, value.__data__)
    )
    return pm.Struct.from_keys(meta_attrs.index.keys, values)


def _subst_spec(spec: pm.Spec, env: SubstEnv) -> pm.Spec:
    args = spec.args
    if args is None or args.index.is_empty:
        return spec

    resolved_values = tuple(subst_val(value, env) for value in args.values)
    if resolved_values == args.values:
        return spec

    resolved_args = pm.Struct.from_keys(args.index.keys, resolved_values)
    return pm.spec_ref(spec.anchor, _struct_const(resolved_args))


def _subst_type(type_: pm.Type, env: SubstEnv) -> pm.Type:
    if isinstance(type_, pm.Val):
        resolved = subst_val(type_, env)
        if isinstance(resolved, pm.Type):
            return resolved
        resolved_type = as_type(resolved)
        return type_ if resolved_type is None else resolved_type

    if isinstance(type_, pm.NominalQualifier):
        new_spec = _subst_spec(type_.spec_ref, env)
        new_underlying = _subst_type(type_.underlying, env)
        if new_spec is type_.spec_ref and new_underlying is type_.underlying:
            return type_
        return mutate(type_, spec_ref=new_spec, underlying=new_underlying)

    if isinstance(type_, pm.NominalType):
        new_spec = _subst_spec(type_.spec_ref, env)
        if new_spec is type_.spec_ref:
            return type_
        return mutate(type_, spec_ref=new_spec)

    if isinstance(type_, pm.StructType):
        new_attrs = type_.meta_attrs.map(lambda meta_attr: _subst_type(meta_attr, env))
        if new_attrs is type_.meta_attrs:
            return type_
        return mutate(type_, meta_attrs=new_attrs)

    if isinstance(type_, pm.UnionType):
        new_types = frozenset(_subst_type(member, env) for member in type_.types)
        if new_types == type_.types:
            return type_
        return pm.UnionType(types=new_types)

    return type_


def _struct_const(struct: pm.Struct[str | None, pm.Val]) -> pm.Const:
    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for key, value in zip(struct.index.keys, struct.values):
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return pm.struct(*positional, **nominal)
