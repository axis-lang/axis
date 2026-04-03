from __future__ import annotations

from collections.abc import Iterable
from typing import cast

from protobase import frozendict, mutate

import protomorph_ as pm

__all__ = [
    "Subst",
    "MatchState",
    "UnifyResult",
    "match",
    "unify",
    "satisfies",
    "normalize",
    "meet",
    "intersect",
    "subsumes",
]


class Subst(pm.Builtin):
    ANCHOR = "std.algebra.Subst"

    bindings: frozendict[pm.Var, pm.Val] = frozendict()


class MatchState(Subst):
    ANCHOR = "std.match.State"


class UnifyResult(pm.Builtin):
    ANCHOR = "std.algebra.UnifyResult"

    subst: Subst = Subst()


def match(
    lhs: pm.Val,
    rhs: pm.Val,
    *,
    state: MatchState | None = None,
    bridge: pm.SemanticBridge | None = None,
) -> Iterable[MatchState]:
    state = MatchState() if state is None else state
    bridge = _bridge_or_default(bridge)
    norm_lhs = cast(pm.Val, normalize(lhs, bridge=bridge))
    norm_rhs = cast(pm.Val, normalize(rhs, bridge=bridge))

    if isinstance(norm_lhs, pm.Op):
        return norm_lhs.__data__.satisfy(norm_rhs, state, bridge)

    return tuple(
        MatchState(bindings=result.subst.bindings)
        for result in unify(norm_lhs, norm_rhs, subst=state, bridge=bridge)
    )


def unify(
    left: pm.Val | pm.Type,
    right: pm.Val | pm.Type,
    *,
    subst: Subst | None = None,
    bridge: pm.SemanticBridge | None = None,
) -> tuple[UnifyResult, ...]:
    bridge = _bridge_or_default(bridge)
    subst = Subst() if subst is None else Subst(bindings=subst.bindings)
    results = _unify_object(left, right, subst=subst, bridge=bridge)
    return tuple(UnifyResult(subst=item) for item in results)


def satisfies(
    actual: pm.Val | pm.Type,
    expected: pm.Val | pm.Type,
    *,
    subst: Subst | None = None,
    bridge: pm.SemanticBridge | None = None,
) -> tuple[UnifyResult, ...]:
    return unify(actual, expected, subst=subst, bridge=bridge)


def normalize(
    value: pm.Val | pm.Type,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Val | pm.Type:
    bridge = _bridge_or_default(bridge)

    if isinstance(value, pm.Op):
        return value.__data__.normalize(bridge)

    if isinstance(value, pm.Spec):
        args = value.args or pm.Struct.Empty
        normalized_args = _normalize_struct(args, bridge=bridge)
        if normalized_args == args:
            return value
        return pm.spec_ref(value.anchor, _struct_const(normalized_args))

    if isinstance(value, pm.Const):
        struct_fields = _const_struct_fields(value)
        if struct_fields is not None:
            normalized_fields = _normalize_struct(struct_fields, bridge=bridge)
            return value if normalized_fields == struct_fields else _struct_const(normalized_fields)

        if isinstance(value.__data__, pm.Type):
            normalized_type = _normalize_type(value.__data__, bridge=bridge)
            return value if normalized_type == value.__data__ else pm.val(normalized_type)
        return value

    if isinstance(value, pm.Type):
        return _normalize_type(value, bridge=bridge)

    return value


def meet(
    left: pm.Val | pm.Type,
    right: pm.Val | pm.Type,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Val | pm.Type | None:
    bridge = _bridge_or_default(bridge)
    left = normalize(left, bridge=bridge)
    right = normalize(right, bridge=bridge)
    results = unify(left, right, bridge=bridge)
    if not results:
        return None
    resolved_left = _apply_subst(left, results[0].subst)
    resolved_right = _apply_subst(right, results[0].subst)
    return resolved_left if resolved_left == resolved_right else resolved_right


def intersect(
    left: pm.Val,
    right: pm.Val,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Val | None:
    result = meet(left, right, bridge=bridge)
    return result if isinstance(result, pm.Val) else None


def subsumes(
    left: pm.Val | pm.Type,
    right: pm.Val | pm.Type,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> bool:
    return bool(satisfies(right, left, bridge=bridge))


def _bridge_or_default(bridge: pm.SemanticBridge | None) -> pm.SemanticBridge:
    return pm.BRIDGE.get(pm.DEFAULT_BRIDGE) if bridge is None else bridge


def _unify_object(
    left: object,
    right: object,
    *,
    subst: Subst,
    bridge: pm.SemanticBridge,
) -> tuple[Subst, ...]:
    left = _apply_subst_object(left, subst)
    right = _apply_subst_object(right, subst)

    if left == right:
        return (subst,)

    if isinstance(left, pm.Var):
        return _bind_var(left, right, subst=subst, bridge=bridge)
    if isinstance(right, pm.Var):
        return _bind_var(right, left, subst=subst, bridge=bridge)

    if left == pm.ANY or right == pm.ANY:
        return (subst,)

    if isinstance(left, pm.Op) and isinstance(right, pm.Val):
        return tuple(
            Subst(bindings=state.bindings)
            for state in left.__data__.satisfy(right, MatchState(bindings=subst.bindings), bridge)
        )
    if isinstance(right, pm.Op) and isinstance(left, pm.Val):
        return tuple(
            Subst(bindings=state.bindings)
            for state in right.__data__.satisfy(left, MatchState(bindings=subst.bindings), bridge)
        )

    if isinstance(left, pm.Spec) and isinstance(right, pm.Spec):
        if left.anchor != right.anchor:
            return ()
        return _unify_structs(left.args or pm.Struct.Empty, right.args or pm.Struct.Empty, subst=subst, bridge=bridge)

    if isinstance(left, pm.Const) and isinstance(right, pm.Const):
        left_fields = _const_struct_fields(left)
        right_fields = _const_struct_fields(right)
        if left_fields is not None or right_fields is not None:
            if left_fields is None or right_fields is None:
                return ()
            return _unify_structs(left_fields, right_fields, subst=subst, bridge=bridge)
        if isinstance(left.__data__, pm.Type) and isinstance(right.__data__, pm.Type):
            return _unify_types(left.__data__, right.__data__, subst=subst, bridge=bridge)
        return ()

    left_type = _as_type_object(left)
    right_type = _as_type_object(right)
    if left_type is not None and right_type is not None:
        return _unify_types(left_type, right_type, subst=subst, bridge=bridge)

    if isinstance(left, pm.Anchor) and isinstance(right, pm.Anchor):
        return (subst,) if left == right else ()

    return ()


def _unify_structs(
    left: pm.Struct[str | None, pm.Val],
    right: pm.Struct[str | None, pm.Val],
    *,
    subst: Subst,
    bridge: pm.SemanticBridge,
) -> tuple[Subst, ...]:
    if left.index.keys != right.index.keys:
        return ()

    substs: tuple[Subst, ...] = (subst,)
    for left_value, right_value in zip(left.values, right.values):
        next_substs = tuple(
            next_subst
            for current in substs
            for next_subst in _unify_object(left_value, right_value, subst=current, bridge=bridge)
        )
        if not next_substs:
            return ()
        substs = next_substs
    return substs


def _unify_types(
    left: pm.Type,
    right: pm.Type,
    *,
    subst: Subst,
    bridge: pm.SemanticBridge,
) -> tuple[Subst, ...]:
    left = _normalize_type(left, bridge=bridge)
    right = _normalize_type(right, bridge=bridge)

    if left == right:
        return (subst,)

    if isinstance(left, pm.Val) and isinstance(right, pm.Val):
        return _unify_object(left, right, subst=subst, bridge=bridge)

    left_fields = _structural_fields(left, bridge=bridge)
    right_fields = _structural_fields(right, bridge=bridge)
    if left_fields is not None and right_fields is not None:
        return _unify_type_structs(left_fields, right_fields, subst=subst, bridge=bridge)

    if isinstance(left, pm.NominalQualifier) and isinstance(right, pm.NominalQualifier):
        spec_substs = _unify_object(left.spec_ref, right.spec_ref, subst=subst, bridge=bridge)
        return tuple(
            next_subst
            for current in spec_substs
            for next_subst in _unify_types(left.underlying, right.underlying, subst=current, bridge=bridge)
        )

    if isinstance(left, pm.NominalType) and isinstance(right, pm.NominalType):
        return _unify_object(left.spec_ref, right.spec_ref, subst=subst, bridge=bridge)

    if isinstance(left, pm.UnionType) and isinstance(right, pm.UnionType):
        return (subst,) if left.types == right.types else ()

    return ()


def _unify_type_structs(
    left: pm.Struct[str, pm.Type],
    right: pm.Struct[str, pm.Type],
    *,
    subst: Subst,
    bridge: pm.SemanticBridge,
) -> tuple[Subst, ...]:
    if left.index.keys != right.index.keys:
        return ()

    substs: tuple[Subst, ...] = (subst,)
    for left_value, right_value in zip(left.values, right.values):
        next_substs = tuple(
            next_subst
            for current in substs
            for next_subst in _unify_types(left_value, right_value, subst=current, bridge=bridge)
        )
        if not next_substs:
            return ()
        substs = next_substs
    return substs


def _bind_var(
    var: pm.Var,
    value: object,
    *,
    subst: Subst,
    bridge: pm.SemanticBridge,
) -> tuple[Subst, ...]:
    existing = subst.bindings.get(var)
    if existing is not None:
        return _unify_object(existing, value, subst=subst, bridge=bridge)

    if not isinstance(value, (pm.Val, pm.Type)):
        return ()
    if _occurs(var, value, subst):
        return ()
    return (Subst(bindings=frozendict({**subst.bindings, var: _coerce_bound_value(var, value)})),)


def _coerce_bound_value(var: pm.Var, value: pm.Val | pm.Type) -> pm.Val:
    if isinstance(value, pm.Val):
        return value
    as_val = pm.val(value)
    if not isinstance(as_val, pm.Val):
        raise TypeError(f"Cannot bind {type(value).__name__} as protomorph value")
    return as_val


def _occurs(var: pm.Var, value: object, subst: Subst) -> bool:
    value = _apply_subst_object(value, subst)
    if value == var:
        return True

    if isinstance(value, pm.Spec):
        return any(_occurs(var, item, subst) for item in (value.args or pm.Struct.Empty).values)
    if isinstance(value, pm.Const):
        fields = _const_struct_fields(value)
        if fields is not None:
            return any(_occurs(var, item, subst) for item in fields.values)
        if isinstance(value.__data__, pm.Type):
            return _occurs(var, value.__data__, subst)
        return False
    if isinstance(value, pm.NominalQualifier):
        return _occurs(var, value.spec_ref, subst) or _occurs(var, value.underlying, subst)
    if isinstance(value, pm.NominalType):
        return _occurs(var, value.spec_ref, subst)
    if isinstance(value, pm.StructType):
        return any(_occurs(var, item, subst) for item in value.meta_attrs.values)
    if isinstance(value, pm.UnionType):
        return any(_occurs(var, item, subst) for item in value.types)
    if isinstance(value, tuple):
        return any(_occurs(var, item, subst) for item in value)
    if isinstance(value, frozenset):
        return any(_occurs(var, item, subst) for item in value)
    if isinstance(value, dict):
        return any(_occurs(var, item, subst) for item in value.values())
    return False


def _apply_subst(value: pm.Val | pm.Type, subst: Subst) -> pm.Val | pm.Type:
    def env(item: pm.Val) -> pm.Val | None:
        if not isinstance(item, pm.Var):
            return None
        return subst.bindings.get(cast(pm.Var, item))

    if isinstance(value, pm.Val):
        return pm.subst_val(value, env)
    return pm._subst_type(value, env)


def _apply_subst_object(value: object, subst: Subst) -> object:
    if isinstance(value, (pm.Val, pm.Type)):
        return _apply_subst(value, subst)
    return value


def _as_type_object(value: object) -> pm.Type | None:
    if isinstance(value, pm.Type):
        return value
    if isinstance(value, pm.Val):
        return value.as_type()
    return None


def _normalize_struct(
    struct: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> pm.Struct[str | None, pm.Val]:
    values: tuple[pm.Val, ...] = tuple(
        cast(pm.Val, normalize(value, bridge=bridge)) for value in struct.values
    )
    if values == struct.values:
        return struct
    return struct.with_values(values)


def _normalize_type(
    type_: pm.Type,
    *,
    bridge: pm.SemanticBridge,
) -> pm.Type:
    if isinstance(type_, pm.Placeholder):
        return type_

    if isinstance(type_, pm.Val):
        return type_

    if isinstance(type_, pm.NominalQualifier):
        spec = normalize(type_.spec_ref, bridge=bridge)
        underlying = _normalize_type(type_.underlying, bridge=bridge)
        if spec == type_.spec_ref and underlying == type_.underlying:
            return type_
        return mutate(type_, spec_ref=spec, underlying=underlying)

    if isinstance(type_, pm.NominalType):
        spec = normalize(type_.spec_ref, bridge=bridge)
        return type_ if spec == type_.spec_ref else mutate(type_, spec_ref=spec)

    if isinstance(type_, pm.StructType):
        attrs = type_.meta_attrs.map(lambda meta_attr: _normalize_type(meta_attr, bridge=bridge))
        return type_ if attrs == type_.meta_attrs else mutate(type_, meta_attrs=attrs)

    if isinstance(type_, pm.UnionType):
        members = frozenset(_normalize_type(member, bridge=bridge) for member in type_.types)
        return type_ if members == type_.types else pm.UnionType(types=members)

    return type_


def _structural_fields(type_: pm.Type, *, bridge: pm.SemanticBridge) -> pm.Struct[str, pm.Type] | None:
    if isinstance(type_, pm.StructType):
        return type_.meta_attrs

    layout = bridge.layout(type_)
    if isinstance(layout, pm.StructLayout):
        return layout.fields

    return None


def _const_struct_fields(value: pm.Const) -> pm.Struct[str | None, pm.Val] | None:
    return pm.Struct.from_const(value)


def _struct_const(struct: pm.Struct[str | None, pm.Val]) -> pm.Const:
    return struct.as_const()
