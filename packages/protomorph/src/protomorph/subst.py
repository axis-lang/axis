from __future__ import annotations

from typing import Callable, cast

from protobase import mutate

import protomorph as pm

__all__ = [
    "SubstEnv",
    "as_type",
    "subst_val",
]


type SubstEnv = Callable[[pm.Var], pm.Val | None]


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
    if isinstance(value, pm.Var):
        resolved = env(value)
        return value if resolved is None else resolved

    if isinstance(value, pm.Spec):
        return _subst_spec(value, env)

    if isinstance(value, pm.Const):
        return _subst_const(value, env)

    return value


def _subst_const(value: pm.Const, env: SubstEnv) -> pm.Val:
    data = value.__data__
    if isinstance(data, pm.Type):
        resolved_type = _subst_type(cast(pm.Type, data), env)
        if resolved_type is data:
            return value
        return pm.val(resolved_type)

    if isinstance(value.__type__, pm.StructType) and isinstance(data, tuple):
        return _subst_struct_const(value, cast(tuple, data), env)

    return value


def _subst_struct_const(
    value: pm.Const,
    data: tuple,
    env: SubstEnv,
) -> pm.Val:
    struct_type = cast(pm.StructType, value.__type__)
    keys = struct_type.meta_attrs.index.keys
    resolved_values = tuple(
        subst_val(field_type._wrap(field_data), env)
        for field_type, field_data in zip(struct_type.meta_attrs.values, data)
    )
    resolved_types = tuple(rv.__type__ for rv in resolved_values)
    resolved_data = tuple(rv.__data__ for rv in resolved_values)
    if resolved_types == struct_type.meta_attrs.values and resolved_data == data:
        return value
    return pm.Const(
        pm.StructType(meta_attrs=pm.Struct.from_keys(keys, resolved_types)),
        resolved_data,
    )


def _subst_spec(spec: pm.Spec, env: SubstEnv) -> pm.Spec:
    args = spec.args
    if args is None or args.index.is_empty:
        return spec

    positional: list[pm.Const | pm.Var] = []
    nominal: dict[str, pm.Const | pm.Var] = {}
    changed = False
    for key, value in zip(args.index.keys, args.values):
        resolved = subst_val(value, env)
        if resolved is not value:
            changed = True
        resolved_arg = _as_const_or_var(resolved)
        if key is None:
            positional.append(resolved_arg)
        else:
            nominal[key] = resolved_arg

    if not changed:
        return spec
    return pm.spec_ref(spec.anchor, pm.struct(*positional, **nominal))


def _subst_type(type_: pm.Type, env: SubstEnv) -> pm.Type:
    if isinstance(type_, pm.Var):
        resolved = as_type(env(type_))
        return type_ if resolved is None else resolved

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


def _as_const_or_var(value: pm.Val) -> pm.Const | pm.Var:
    if isinstance(value, (pm.Const, pm.Var)):
        return value
    return cast(pm.Const | pm.Var, pm.val(value))
