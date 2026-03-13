from __future__ import annotations

from typing import cast

import protomorph as pm

from axis import expr, syn, log
from axis.literals import Wildcard

from .scope import ScopeLike


def build_bound(bound_expr: syn.Expr | None, scope: ScopeLike) -> pm.Val | None:
    """Build the semantic bound value associated with a bound expression.

    This transforms a bound expression into a partial morph value suitable for
    specialization and parameter bounds. Unsupported forms degrade to `pm.Err`.
    """
    if bound_expr is None:
        return None

    match bound_expr:
        case expr.Sym() as sym:
            return scope.lookup(sym)
        case expr.Member(of=of_expr, name=name):
            of_val = build_bound(of_expr, scope)
            if isinstance(of_val, pm.Err):
                return of_val
            if isinstance(of_val, pm.Anchor):
                return cast(pm.Anchor, of_val).child(name)
            return _unsupported_bound(
                bound_expr,
                f"member access requires an Anchor base, got {_val_type_name(of_val)}",
            )
        case expr.Index(origin=origin_expr, indices=indices_expr):
            origin_val = build_bound(origin_expr, scope)
            if isinstance(origin_val, pm.Err):
                return origin_val
            args = _build_spec_args(indices_expr, scope)
            if isinstance(origin_val, pm.Anchor):
                return cast(pm.Anchor, origin_val).specialize(args)
            return _unsupported_bound(
                bound_expr,
                f"specialization requires an Anchor base, got {_val_type_name(origin_val)}",
            )
        case expr.Apply():
            return _unsupported_bound(
                bound_expr,
                "function application cannot be used to construct bounds yet",
            )
        case expr.Lit(value=value):
            if value is Wildcard or value is Ellipsis:
                return _unsupported_bound(bound_expr, f"unsupported literal {value!r}")
            return pm.literal(value)
        case expr.Compound(components=components):
            return _build_compound_bound(components, scope)
        case expr.Tuple(elements=elements):
            positional: list[pm.Const | pm.Var] = []
            nominal: dict[str, pm.Const | pm.Var] = {}
            for element in elements:
                built = _build_tuple_element_bound(element, scope)
                if built is None:
                    continue
                key, value = built
                if key is None:
                    positional.append(value)
                else:
                    nominal[key] = value
            return pm.struct(*positional, **nominal)
        case _:
            return _unsupported_bound(bound_expr, "unsupported bound expression")


def build_default(default_expr: syn.Expr | None, scope: ScopeLike) -> pm.Val | None:
    """Build the semantic default value associated with a default expression.

    Defaults currently share the same construction rules as bounds.
    """
    return build_bound(default_expr, scope)


def _build_compound_bound(
    components: tuple[syn.Expr, ...],
    scope: ScopeLike,
) -> pm.Val:
    if not components:
        return _unsupported_bound(None, "empty compound expression")

    *head_components, underlying_expr = components
    if not head_components:
        return build_bound(underlying_expr, scope)

    qualifier_expr = head_components[0] if len(head_components) == 1 else expr.Compound(
        components=tuple(head_components)
    )
    qualifier_val = build_bound(qualifier_expr, scope)
    underlying_val = build_bound(underlying_expr, scope)

    if isinstance(qualifier_val, pm.Err):
        return qualifier_val
    if isinstance(underlying_val, pm.Err):
        return underlying_val

    qualifier_ref = _as_qualifier_ref(qualifier_val, qualifier_expr)
    if isinstance(qualifier_ref, pm.Err):
        return qualifier_ref

    underlying_type = _as_type_bound_val(underlying_val, underlying_expr)
    if isinstance(underlying_type, pm.Err):
        return underlying_type

    args = qualifier_ref._args_const() if isinstance(qualifier_ref, pm.Spec) else None
    return pm.val(
        pm.nominal_qual(
            qualifier_ref.anchor if isinstance(qualifier_ref, pm.Spec) else qualifier_ref,
            args,
            underlying=underlying_type,
        )
    )


def _build_spec_args(indices_expr: syn.Expr, scope: ScopeLike) -> pm.Const | None:
    if not isinstance(indices_expr, expr.Tuple):
        indices_expr = expr.Tuple(elements=(expr.Tuple.Positional(value=indices_expr),))

    positional: list[pm.Const | pm.Var] = []
    nominal: dict[str, pm.Const | pm.Var] = {}
    for element in indices_expr.elements:
        built = _build_tuple_element_bound(element, scope)
        if built is None:
            continue
        key, value = built
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value

    if not positional and not nominal:
        return None

    return pm.struct(*positional, **nominal)


def _build_tuple_element_bound(
    element: expr.Tuple.Element,
    scope: ScopeLike,
) -> tuple[str | None, pm.Const | pm.Var] | None:
    match element:
        case expr.Tuple.Positional(value=value_expr):
            value = build_bound(value_expr, scope)
            return None if value is None else (None, _as_const_or_var(value, value_expr))
        case expr.Tuple.Nominal(key=key_expr, value=value_expr):
            if value_expr is None:
                value_expr = key_expr
            value = build_bound(value_expr, scope)
            return (
                expr.to_slot_name(key_expr),
                _as_const_or_var(value, value_expr),
            )
        case _:
            return None


def _as_const_or_var(value: pm.Val | None, origin: syn.Expr | None) -> pm.Const | pm.Var:
    if isinstance(value, (pm.Const, pm.Var)):
        return value
    if isinstance(value, (pm.Anchor, pm.Spec)):
        return pm.val(value)
    raise _unsupported_bound_exception(
        origin,
        f"tuple/spec element must build a Const or Var, got {_val_type_name(value)}",
    )


def _as_qualifier_ref(
    bound_val: pm.Val,
    origin: syn.Expr | None,
) -> pm.Anchor | pm.Spec | pm.Err:
    if isinstance(bound_val, (pm.Anchor, pm.Spec)):
        return bound_val
    return _unsupported_bound(
        origin,
        f"qualifier base must be Anchor or Spec, got {_val_type_name(bound_val)}",
    )


def _as_type_bound_val(
    bound_val: pm.Val,
    origin: syn.Expr | None,
) -> pm.Type | pm.Err:
    if isinstance(bound_val, pm.Type):
        return bound_val
    if isinstance(bound_val, pm.Const) and isinstance(bound_val.data, pm.Type):
        return cast(pm.Type, bound_val.data)
    if isinstance(bound_val, pm.Anchor):
        return pm.nominal_type(bound_val)
    if isinstance(bound_val, pm.Spec):
        return pm.nominal_type(bound_val.anchor, bound_val._args_const())
    return _unsupported_bound(
        origin,
        f"expected a type-like bound, got {_val_type_name(bound_val)}",
    )


def _val_type_name(value: object | None) -> str:
    return type(value).__name__ if value is not None else "None"


def _unsupported_bound(bound: syn.Expr | None, message: str) -> pm.Err:
    return log.error("Unsupported bound expression").label(
        bound,
        message,
    ).tag(pm.Err())


def _unsupported_bound_exception(bound: syn.Expr | None, message: str) -> TypeError:
    return TypeError(f"{message}: {bound!r}" if bound is not None else message)
