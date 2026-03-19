from __future__ import annotations

from collections.abc import Iterable

from protobase import Consed, frozendict, mutate

import protomorph as pm

__all__ = [
    "Discriminant",
    "MatchState",
    "match",
    "normalize",
    "intersect",
    "subsumes",
]


class Discriminant(pm.Builtin):
    ANCHOR = "std.match.Discriminant"

    key: str
    value: pm.Data


class MatchState(pm.Builtin):
    ANCHOR = "std.match.State"

    bindings: frozendict[pm.Val, pm.Val] = frozendict()


def match(
    lhs: pm.Val,
    rhs: pm.Val,
    *,
    state: MatchState | None = None,
    bridge: pm.SemanticBridge | None = None,
) -> Iterable[MatchState]:
    state = MatchState() if state is None else state
    bridge = _bridge_or_default(bridge)
    lhs = normalize(lhs, bridge=bridge)
    rhs = normalize(rhs, bridge=bridge)

    if isinstance(lhs, pm.Var):
        return _match_var(lhs, rhs, state=state, bridge=bridge)

    if isinstance(lhs, pm.Any):
        return (state,)

    if isinstance(lhs, pm.Op):
        return lhs.__data__.satisfy(rhs, state, bridge)

    return _match_exact(lhs, rhs, state=state, bridge=bridge)


def normalize(value: pm.Val, *, bridge: pm.SemanticBridge | None = None) -> pm.Val:
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

    if isinstance(value, pm.Anchor):
        return value

    return value


def intersect(
    left: pm.Val,
    right: pm.Val,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Val | None:
    bridge = _bridge_or_default(bridge)
    left = normalize(left, bridge=bridge)
    right = normalize(right, bridge=bridge)

    if left == right:
        return left
    if isinstance(left, pm.Any):
        return right
    if isinstance(right, pm.Any):
        return left
    if isinstance(left, pm.Var):
        return right
    if isinstance(right, pm.Var):
        return left
    if isinstance(left, pm.Op):
        return left.__data__.intersect(right, bridge)
    if isinstance(right, pm.Op):
        return right.__data__.intersect(left, bridge)

    if isinstance(left, pm.Spec) and isinstance(right, pm.Spec):
        if left.anchor != right.anchor:
            return None
        args = _intersect_structs(left.args or pm.Struct.Empty, right.args or pm.Struct.Empty, bridge=bridge)
        return None if args is None else pm.spec_ref(left.anchor, _struct_const(args))

    if isinstance(left, pm.Const) and isinstance(right, pm.Const):
        left_fields = _const_struct_fields(left)
        right_fields = _const_struct_fields(right)
        if left_fields is not None and right_fields is not None:
            fields = _intersect_structs(left_fields, right_fields, bridge=bridge)
            return None if fields is None else _struct_const(fields)
        return left if left == right else None

    if isinstance(left, pm.NominalType) and isinstance(right, pm.NominalType):
        spec = intersect(left.spec_ref, right.spec_ref, bridge=bridge)
        return None if not isinstance(spec, pm.Spec) else mutate(left, spec_ref=spec)

    if isinstance(left, pm.NominalQualifier) and isinstance(right, pm.NominalQualifier):
        spec = intersect(left.spec_ref, right.spec_ref, bridge=bridge)
        if not isinstance(spec, pm.Spec):
            return None
        underlying = _intersect_types(left.underlying, right.underlying, bridge=bridge)
        if underlying is None:
            return None
        return mutate(left, spec_ref=spec, underlying=underlying)

    if isinstance(left, pm.Anchor) and isinstance(right, pm.Anchor):
        return left if left == right else None

    return None


def subsumes(
    left: pm.Val,
    right: pm.Val,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> bool:
    bridge = _bridge_or_default(bridge)
    left = normalize(left, bridge=bridge)
    right = normalize(right, bridge=bridge)

    if left == right:
        return True
    if isinstance(left, (pm.Any, pm.Var)):
        return True
    if isinstance(left, pm.Op):
        return left.__data__.subsumes(right, bridge)
    if isinstance(right, (pm.Any, pm.Var, pm.Op)):
        return False

    if isinstance(left, pm.Spec) and isinstance(right, pm.Spec):
        return left.anchor == right.anchor and _subsumes_structs(
            left.args or pm.Struct.Empty,
            right.args or pm.Struct.Empty,
            bridge=bridge,
        )

    if isinstance(left, pm.Const) and isinstance(right, pm.Const):
        left_fields = _const_struct_fields(left)
        right_fields = _const_struct_fields(right)
        if left_fields is not None and right_fields is not None:
            return _subsumes_structs(left_fields, right_fields, bridge=bridge)
        return False

    if isinstance(left, pm.NominalType) and isinstance(right, pm.NominalType):
        return subsumes(left.spec_ref, right.spec_ref, bridge=bridge)

    if isinstance(left, pm.NominalQualifier) and isinstance(right, pm.NominalQualifier):
        return subsumes(left.spec_ref, right.spec_ref, bridge=bridge) and _subsumes_types(
            left.underlying,
            right.underlying,
            bridge=bridge,
        )

    return False


def _bridge_or_default(bridge: pm.SemanticBridge | None) -> pm.SemanticBridge:
    return pm.BRIDGE.get(pm.DEFAULT_BRIDGE) if bridge is None else bridge


def _match_var(
    lhs: pm.Var,
    rhs: pm.Val,
    *,
    state: MatchState,
    bridge: pm.SemanticBridge,
) -> Iterable[MatchState]:
    bound = state.bindings.get(lhs)
    if bound is None:
        yield MatchState(bindings=frozendict((*state.bindings.items(), (lhs, rhs))))
        return
    yield from match(bound, rhs, state=state, bridge=bridge)


def _match_exact(
    lhs: pm.Val,
    rhs: pm.Val,
    *,
    state: MatchState,
    bridge: pm.SemanticBridge,
) -> Iterable[MatchState]:
    if isinstance(lhs, pm.Spec):
        if not isinstance(rhs, pm.Spec) or lhs.anchor != rhs.anchor:
            return ()
        return _match_struct(
            lhs.args or pm.Struct.Empty,
            rhs.args or pm.Struct.Empty,
            state=state,
            bridge=bridge,
        )

    if isinstance(lhs, pm.Const):
        if not isinstance(rhs, pm.Const):
            return ()
        lhs_fields = _const_struct_fields(lhs)
        rhs_fields = _const_struct_fields(rhs)
        if lhs_fields is not None or rhs_fields is not None:
            if lhs_fields is None or rhs_fields is None:
                return ()
            return _match_struct(lhs_fields, rhs_fields, state=state, bridge=bridge)
        if isinstance(lhs.__data__, pm.Type) and isinstance(rhs.__data__, pm.Type):
            return _match_type(lhs.__data__, rhs.__data__, state=state, bridge=bridge)
        return (state,) if lhs == rhs else ()

    if isinstance(lhs, pm.NominalType):
        if not isinstance(rhs, pm.NominalType):
            return ()
        return _match_exact(lhs.spec_ref, rhs.spec_ref, state=state, bridge=bridge)

    if isinstance(lhs, pm.NominalQualifier):
        if not isinstance(rhs, pm.NominalQualifier):
            return ()
        states = _match_exact(lhs.spec_ref, rhs.spec_ref, state=state, bridge=bridge)
        result: list[MatchState] = []
        for next_state in states:
            result.extend(
                _match_type(lhs.underlying, rhs.underlying, state=next_state, bridge=bridge)
            )
        return tuple(result)

    return (state,) if lhs == rhs else ()


def _match_type(
    lhs: pm.Type,
    rhs: pm.Type,
    *,
    state: MatchState,
    bridge: pm.SemanticBridge,
) -> Iterable[MatchState]:
    if isinstance(lhs, pm.Val) and isinstance(rhs, pm.Val):
        return match(lhs, rhs, state=state, bridge=bridge)

    if isinstance(lhs, pm.NominalType) and isinstance(rhs, pm.NominalType):
        return _match_exact(lhs.spec_ref, rhs.spec_ref, state=state, bridge=bridge)

    if isinstance(lhs, pm.NominalQualifier) and isinstance(rhs, pm.NominalQualifier):
        states = _match_exact(lhs.spec_ref, rhs.spec_ref, state=state, bridge=bridge)
        result: list[MatchState] = []
        for next_state in states:
            result.extend(
                _match_type(lhs.underlying, rhs.underlying, state=next_state, bridge=bridge)
            )
        return tuple(result)

    return (state,) if lhs == rhs else ()


def _match_struct(
    lhs: pm.Struct[str | None, pm.Val],
    rhs: pm.Struct[str | None, pm.Val],
    *,
    state: MatchState,
    bridge: pm.SemanticBridge,
) -> Iterable[MatchState]:
    if lhs.index.keys != rhs.index.keys:
        return ()

    states: tuple[MatchState, ...] = (state,)
    for left_value, right_value in zip(lhs.values, rhs.values):
        next_states: list[MatchState] = []
        for current in states:
            next_states.extend(match(left_value, right_value, state=current, bridge=bridge))
        if not next_states:
            return ()
        states = tuple(next_states)
    return states


def _normalize_struct(
    struct: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> pm.Struct[str | None, pm.Val]:
    values = tuple(normalize(value, bridge=bridge) for value in struct.values)
    if values == struct.values:
        return struct
    return struct.with_values(values)


def _const_struct_fields(value: pm.Const) -> pm.Struct[str | None, pm.Val] | None:
    return pm.Struct.from_const(value)


def _struct_const(struct: pm.Struct[str | None, pm.Val]) -> pm.Const:
    return struct.as_const()


def _intersect_structs(
    left: pm.Struct[str | None, pm.Val],
    right: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> pm.Struct[str | None, pm.Val] | None:
    if left.index.keys != right.index.keys:
        return None

    values: list[pm.Val] = []
    for left_value, right_value in zip(left.values, right.values):
        result = intersect(left_value, right_value, bridge=bridge)
        if result is None:
            return None
        values.append(result)
    return left.with_values(tuple(values))


def _subsumes_structs(
    left: pm.Struct[str | None, pm.Val],
    right: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> bool:
    if left.index.keys != right.index.keys:
        return False
    return all(
        subsumes(left_value, right_value, bridge=bridge)
        for left_value, right_value in zip(left.values, right.values)
    )


def _normalize_type(
    type_: pm.Type,
    *,
    bridge: pm.SemanticBridge,
) -> pm.Type:
    if isinstance(type_, pm.Val):
        normalized = normalize(type_, bridge=bridge)
        return normalized if isinstance(normalized, pm.Type) else type_

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


def _intersect_types(
    left: pm.Type,
    right: pm.Type,
    *,
    bridge: pm.SemanticBridge,
) -> pm.Type | None:
    if isinstance(left, pm.Val) and isinstance(right, pm.Val):
        value = intersect(left, right, bridge=bridge)
        return value if isinstance(value, pm.Type) else None

    if isinstance(left, pm.NominalType) and isinstance(right, pm.NominalType):
        spec = intersect(left.spec_ref, right.spec_ref, bridge=bridge)
        return None if not isinstance(spec, pm.Spec) else mutate(left, spec_ref=spec)

    if isinstance(left, pm.NominalQualifier) and isinstance(right, pm.NominalQualifier):
        spec = intersect(left.spec_ref, right.spec_ref, bridge=bridge)
        if not isinstance(spec, pm.Spec):
            return None
        underlying = _intersect_types(left.underlying, right.underlying, bridge=bridge)
        if underlying is None:
            return None
        return mutate(left, spec_ref=spec, underlying=underlying)

    return left if left == right else None


def _subsumes_types(
    left: pm.Type,
    right: pm.Type,
    *,
    bridge: pm.SemanticBridge,
) -> bool:
    if isinstance(left, pm.Val) and isinstance(right, pm.Val):
        return subsumes(left, right, bridge=bridge)

    if isinstance(left, pm.NominalType) and isinstance(right, pm.NominalType):
        return subsumes(left.spec_ref, right.spec_ref, bridge=bridge)

    if isinstance(left, pm.NominalQualifier) and isinstance(right, pm.NominalQualifier):
        return subsumes(left.spec_ref, right.spec_ref, bridge=bridge) and _subsumes_types(
            left.underlying,
            right.underlying,
            bridge=bridge,
        )

    return left == right
