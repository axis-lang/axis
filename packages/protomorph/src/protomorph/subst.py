from __future__ import annotations

from typing import Callable, cast

from protobase import mutate

import protomorph as morph

__all__ = [
    "SubstEnv",
    "as_type",
    "subst_val",
]


type SubstEnv = Callable[[morph.Var], morph.Val | None]


def as_type(value: morph.Val | morph.Type | None) -> morph.Type | None:
    if value is None:
        return None
    if isinstance(value, morph.Type):
        return value
    if isinstance(value, morph.Const) and isinstance(value.__data__, morph.Type):
        return cast(morph.Type, value.__data__)
    if isinstance(value, morph.Anchor):
        return morph.nominal_type(value)
    if isinstance(value, morph.Spec):
        return morph.nominal_type(value.anchor, value._args_const())
    return None


def subst_val(value: morph.Val, env: SubstEnv) -> morph.Val:
    if isinstance(value, morph.Var):
        resolved = env(value)
        return value if resolved is None else resolved

    if isinstance(value, morph.Spec):
        return _subst_spec(value, env)

    if isinstance(value, morph.Const):
        return _subst_const(value, env)

    return value


def _subst_const(value: morph.Const, env: SubstEnv) -> morph.Val:
    data = value.__data__
    if isinstance(data, morph.Type):
        resolved_type = _subst_type(cast(morph.Type, data), env)
        if resolved_type is data:
            return value
        return morph.val(resolved_type)

    if isinstance(value.__type__, morph.StructType) and isinstance(data, tuple):
        return _subst_struct_const(value, cast(tuple, data), env)

    return value


def _subst_struct_const(
    value: morph.Const,
    data: tuple,
    env: SubstEnv,
) -> morph.Val:
    struct_type = cast(morph.StructType, value.__type__)
    keys = struct_type.meta_attrs.index.keys
    resolved_values = tuple(
        subst_val(field_type._wrap(field_data), env)
        for field_type, field_data in zip(struct_type.meta_attrs.values, data)
    )
    resolved_types = tuple(rv.__type__ for rv in resolved_values)
    resolved_data = tuple(rv.__data__ for rv in resolved_values)
    if resolved_types == struct_type.meta_attrs.values and resolved_data == data:
        return value
    return morph.Const(
        morph.StructType(meta_attrs=morph.Struct.from_keys(keys, resolved_types)),
        resolved_data,
    )


def _subst_spec(spec: morph.Spec, env: SubstEnv) -> morph.Spec:
    args = spec.args
    if args is None:
        return spec

    positional: list[morph.Const | morph.Var] = []
    nominal: dict[str, morph.Const | morph.Var] = {}
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
    return morph.spec_ref(spec.anchor, morph.struct(*positional, **nominal))


def _subst_type(type_: morph.Type, env: SubstEnv) -> morph.Type:
    if isinstance(type_, morph.Var):
        resolved = as_type(env(type_))
        return type_ if resolved is None else resolved

    if isinstance(type_, morph.NominalQualifier):
        new_spec = _subst_spec(type_.spec_ref, env)
        new_underlying = _subst_type(type_.underlying, env)
        if new_spec is type_.spec_ref and new_underlying is type_.underlying:
            return type_
        return mutate(type_, spec_ref=new_spec, underlying=new_underlying)

    if isinstance(type_, morph.NominalType):
        new_spec = _subst_spec(type_.spec_ref, env)
        if new_spec is type_.spec_ref:
            return type_
        return mutate(type_, spec_ref=new_spec)

    if isinstance(type_, morph.StructType):
        new_attrs = type_.meta_attrs.map(lambda meta_attr: _subst_type(meta_attr, env))
        if new_attrs is type_.meta_attrs:
            return type_
        return mutate(type_, meta_attrs=new_attrs)

    if isinstance(type_, morph.UnionType):
        new_types = frozenset(_subst_type(member, env) for member in type_.types)
        if new_types == type_.types:
            return type_
        return morph.UnionType(types=new_types)

    return type_


def _as_const_or_var(value: morph.Val) -> morph.Const | morph.Var:
    if isinstance(value, (morph.Const, morph.Var)):
        return value
    return cast(morph.Const | morph.Var, morph.val(value))
