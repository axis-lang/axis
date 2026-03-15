from __future__ import annotations

from typing import cast

import protomorph as pm

from axis import log, syn
from axis.literals import Wildcard


def build_compound_bound(
    components: tuple[syn.Expr, ...],
    scope: syn.ScopeLike,
) -> pm.Val:
    from axis import expr as expr_module

    if not components:
        return unsupported_bound(None, "empty compound expression")

    *head_components, underlying_expr = components
    if not head_components:
        return underlying_expr.to_bound(scope)

    qualifier_expr = (
        head_components[0]
        if len(head_components) == 1
        else expr_module.Compound(components=tuple(head_components))
    )
    qualifier_val = qualifier_expr.to_bound(scope)
    underlying_val = underlying_expr.to_bound(scope)

    if isinstance(qualifier_val, pm.Err):
        return qualifier_val
    if isinstance(underlying_val, pm.Err):
        return underlying_val

    qualifier_ref = as_qualifier_ref(qualifier_val, qualifier_expr)
    if isinstance(qualifier_ref, pm.Err):
        return qualifier_ref

    underlying_type = as_type_bound_val(underlying_val, underlying_expr)
    if isinstance(underlying_type, pm.Err):
        return underlying_type
    
    if isinstance(qualifier_ref, pm.Anchor):
        return pm.val(pm.nominal_qual(qualifier_ref, underlying=underlying_type))

    if isinstance(qualifier_ref, pm.Spec):
        return pm.val(pm.NominalQualifier(spec_ref=qualifier_ref, underlying=underlying_type))

    return unsupported_bound(None, f"unsupported qualifier type {type(qualifier_ref).__name__} in compound expression")
    
def build_spec_args(indices_expr: syn.Expr, scope: syn.ScopeLike) -> pm.Const | None:
    from axis import expr as expr_module

    if not isinstance(indices_expr, expr_module.Tuple):
        indices_expr = expr_module.Tuple(
            elements=(expr_module.Tuple.Positional(value=indices_expr),)
        )

    positional: list[pm.Const | pm.Var] = []
    nominal: dict[str, pm.Const | pm.Var] = {}
    for element in indices_expr.elements:
        built = build_tuple_element_bound(element, scope)
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


def build_tuple_bound(
    elements: tuple[syn.Node, ...],
    scope: syn.ScopeLike,
) -> pm.Val:
    positional: list[pm.Const | pm.Var] = []
    nominal: dict[str, pm.Const | pm.Var] = {}
    for element in elements:
        built = build_tuple_element_bound(element, scope)
        if built is None:
            continue
        key, value = built
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return pm.struct(*positional, **nominal)


def build_tuple_element_bound(
    element: syn.Node,
    scope: syn.ScopeLike,
) -> tuple[str | None, pm.Const | pm.Var] | None:
    from axis import expr as expr_module

    match element:
        case expr_module.Tuple.Positional(value=value_expr):
            value = value_expr.to_bound(scope)
            return None if value is None else (None, as_const_or_var(value, value_expr))
        case expr_module.Tuple.Nominal(key=key_expr, value=value_expr):
            if value_expr is None:
                value_expr = key_expr
            value = value_expr.to_bound(scope)
            return (
                expr_module.to_slot_name(key_expr),
                as_const_or_var(value, value_expr),
            )
        case _:
            return None


def literal_to_bound(literal: object, origin: syn.Expr) -> pm.Val:
    if literal is Wildcard or literal is Ellipsis:
        return unsupported_bound(origin, f"unsupported literal {literal!r}")
    return pm.literal(literal)


def as_const_or_var(value: pm.Val | None, origin: syn.Expr | None) -> pm.Const | pm.Var:
    if isinstance(value, (pm.Const, pm.Var)):
        return value
    if isinstance(value, (pm.Anchor, pm.Spec)):
        return pm.val(value)
    raise unsupported_bound_exception(
        origin,
        f"tuple/spec element must build a Const or Var, got {val_type_name(value)}",
    )


def as_qualifier_ref(
    bound_val: pm.Val,
    origin: syn.Expr | None,
) -> pm.Anchor | pm.Spec | pm.Err:
    if isinstance(bound_val, (pm.Anchor, pm.Spec)):
        return bound_val
    return unsupported_bound(
        origin,
        f"qualifier base must be Anchor or Spec, got {val_type_name(bound_val)}",
    )


def as_type_bound_val(
    bound_val: pm.Val,
    origin: syn.Expr | None,
) -> pm.Type | pm.Err:
    if isinstance(bound_val, pm.Type):
        return bound_val
    if isinstance(bound_val, pm.Const) and isinstance(bound_val.__data__, pm.Type):
        return cast(pm.Type, bound_val.__data__)
    if isinstance(bound_val, pm.Anchor):
        return pm.nominal_type(bound_val)
    if isinstance(bound_val, pm.Spec):
        return pm.nominal_type(bound_val.anchor, bound_val._args_const())
    return unsupported_bound(
        origin,
        f"expected a type-like bound, got {val_type_name(bound_val)}",
    )


def val_type_name(value: object | None) -> str:
    return type(value).__name__ if value is not None else "None"


def unsupported_bound(bound: syn.Expr | None, message: str) -> pm.Err:
    return log.error("Unsupported bound expression").label(
        bound,
        message,
    ).tag(pm.Err())


def unsupported_bound_exception(bound: syn.Expr | None, message: str) -> TypeError:
    return TypeError(f"{message}: {bound!r}" if bound is not None else message)
