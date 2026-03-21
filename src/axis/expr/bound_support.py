from __future__ import annotations

from typing import cast

import protomorph as pm

from axis import log, syn
from axis.literals import Wildcard
from axis.sem.binding import BindingStruct

CONFORMS_FACT = "std.facts.Conforms"
EXTENDS_FACT = "std.facts.Extends"


def build_compound_bound(
    components: tuple[syn.Expr, ...],
    scope: syn.ScopeLike,
) -> pm.Val:
    if not components:
        return unsupported_bound(None, "empty compound expression")

    *qualifier_exprs, underlying_expr = components
    if not qualifier_exprs:
        value = underlying_expr.to_bound(scope)
        if value is None:
            return unsupported_bound(underlying_expr, "expression did not produce a bound")
        return value

    underlying_val = underlying_expr.to_bound(scope)
    if underlying_val is None:
        return unsupported_bound(underlying_expr, "underlying expression did not produce a bound")
    if isinstance(underlying_val, pm.Err):
        return underlying_val

    underlying_type = as_type_bound_val(underlying_val, underlying_expr)
    if isinstance(underlying_type, pm.Err):
        return underlying_type

    current = underlying_type
    for qualifier_expr in reversed(qualifier_exprs):
        qualifier_val = qualifier_expr.to_bound(scope)
        if qualifier_val is None:
            return unsupported_bound(
                qualifier_expr,
                "qualifier expression did not produce a bound",
            )
        if isinstance(qualifier_val, pm.Err):
            return qualifier_val

        qualifier_ref = as_qualifier_ref(qualifier_val, qualifier_expr)
        if isinstance(qualifier_ref, pm.Err):
            return qualifier_ref

        if isinstance(qualifier_ref, pm.Anchor):
            current = pm.nominal_qual(qualifier_ref, underlying=current)
        else:
            current = pm.NominalQualifier(spec_ref=qualifier_ref, underlying=current)

    return pm.val(current)


def build_term(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    if bound_expr is None:
        return None

    try:
        return bound_expr.to_bound(scope)
    except syn.BoundLoweringError as exc:
        return (
            log.error("Unsupported bound expression")
            .label(bound_expr, str(exc))
            .show()
            .tag(pm.Err())
        )


def build_bound(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return build_term(bound_expr, scope)


def build_default(default_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Val | None:
    return build_term(default_expr, scope)


def build_extends_fact(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Spec | pm.Err | None:
    if bound_expr is None:
        return None

    term = build_term(bound_expr, scope)
    if term is None or isinstance(term, pm.Err):
        return term

    from axis import expr as expr_module

    self_term = scope.lookup(expr_module.Sym(name="Self"), origin=bound_expr)
    if isinstance(self_term, pm.Err):
        return self_term

    return pm.spec_ref(
        EXTENDS_FACT,
        pm.struct(self_term, **{"from": _fact_target_term(term)}),
    )


def build_fact(fact_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Spec | pm.Err | None:
    if fact_expr is None:
        return None

    term = build_term(fact_expr, scope)
    if term is None or isinstance(term, pm.Err):
        return term
    if isinstance(term, pm.Spec):
        return term
    if isinstance(term, pm.Anchor):
        return pm.spec_ref(term)
    return (
        log.error("Claim head must be a fact-like expression")
        .label(fact_expr)
        .tag(pm.Err())
    )


def build_goal(goal_expr: syn.Expr | None, scope: syn.ScopeLike) -> pm.Spec | pm.Err | None:
    return build_fact(goal_expr, scope)


def build_binding_pattern(bindings: BindingStruct, scope: syn.ScopeLike) -> pm.Val:
    prefix_entries = tuple((binding.slot_key, _binding_bound(binding, scope)) for binding in bindings.prefix)
    suffix_entries = tuple((binding.slot_key, _binding_bound(binding, scope)) for binding in bindings.suffix)

    if bindings.spread is None and not bindings.open_tail:
        entries = prefix_entries + suffix_entries
        return pm.struct(*_positional_values(entries), **_nominal_values(entries))

    if bindings.spread is None:
        middle = pm.ANY
    else:
        middle = _binding_bound(bindings.spread, scope)

    return pm.variadic_struct(
        prefix=pm.Struct.from_iter(prefix_entries),
        middle=middle,
        suffix=pm.Struct.from_iter(suffix_entries),
    )


def bound_as_type(
    bound: pm.Val | None,
    *,
    bridge: pm.SemanticBridge | None = None,
) -> pm.Type | None:
    if bound is None or isinstance(bound, pm.Err):
        return None

    bridge = pm.BRIDGE.get(pm.DEFAULT_BRIDGE) if bridge is None else bridge

    if isinstance(bound, pm.Op):
        operator = bound.__data__
        if isinstance(operator, pm.Satisfy):
            return _satisfy_as_type(operator.goal, bridge=bridge)
        if isinstance(operator, pm.ViewAs):
            return bound_as_type(operator.pattern, bridge=bridge)
        if isinstance(operator, pm.QualifierSuffix):
            return bound_as_type(operator.suffix, bridge=bridge)

    direct = bound.as_type()
    if direct is not None:
        return direct
    return None


def build_spec_args(indices_expr: syn.Expr, scope: syn.ScopeLike) -> pm.Const | pm.Err | None:
    from axis import expr as expr_module

    if not isinstance(indices_expr, expr_module.Tuple):
        indices_expr = expr_module.Tuple(
            elements=(expr_module.Tuple.Positional(value=indices_expr),)
        )

    positional: list[pm.Const | pm.Var] = []
    nominal: dict[str, pm.Const | pm.Var] = {}
    for element in indices_expr.elements:
        built = build_tuple_element_bound(element, scope)
        if isinstance(built, pm.Err):
            return built
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
        if isinstance(built, pm.Err):
            return built
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
) -> tuple[str | None, pm.Const | pm.Var] | pm.Err | None:
    from axis import expr as expr_module

    match element:
        case expr_module.Tuple.Positional(value=value_expr):
            value = build_term(value_expr, scope)
            if isinstance(value, pm.Err):
                return value
            return None if value is None else (None, as_const_or_var(value, value_expr))
        case expr_module.Tuple.Nominal(key=key_expr, value=value_expr):
            if value_expr is None:
                value_expr = key_expr
            value = build_term(value_expr, scope)
            if isinstance(value, pm.Err):
                return value
            return (
                expr_module.to_slot_name(key_expr),
                as_const_or_var(value, value_expr),
            )
        case _:
            return None


def literal_to_bound(literal: object, origin: syn.Expr) -> pm.Val:
    if literal is Wildcard or literal is Ellipsis:
        return unsupported_bound(origin, f"unsupported literal {literal!r}")
    if not isinstance(literal, (int, float, str, bool, type(None))):
        return unsupported_bound(origin, f"unsupported literal type {type(literal).__name__}")
    return pm.literal(literal)


def as_const_or_var(value: pm.Val | None, origin: syn.Expr | None) -> pm.Const | pm.Var:
    if isinstance(value, (pm.Const, pm.Var)):
        return value
    if isinstance(value, (pm.Anchor, pm.Spec)):
        type_ = value.as_type()
        if type_ is not None:
            return cast(pm.Const | pm.Var, pm.val(type_))
        return cast(pm.Const | pm.Var, pm.val(value))
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
    bound_type = bound_val.as_type()
    if bound_type is not None:
        return bound_type
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


def _binding_bound(binding: BindingStruct.Field, scope: syn.ScopeLike) -> pm.Val:
    bound = build_bound(binding.bound_expr, scope)
    return pm.ANY if bound is None else bound


def _satisfy_as_type(
    goal: pm.Spec,
    *,
    bridge: pm.SemanticBridge,
) -> pm.Type | None:
    if goal.anchor.path == CONFORMS_FACT:
        args = goal.args or pm.Struct.Empty
        target = args.get("to", default=None)
        return bound_as_type(target, bridge=bridge)
    _ = bridge
    return None


def _fact_target_term(term: pm.Val) -> pm.Val:
    type_ = term.as_type()
    if type_ is None:
        return term
    if isinstance(type_, pm.Val):
        return type_
    return pm.val(type_)


def _positional_values(
    entries: tuple[tuple[str | None, pm.Val], ...],
) -> tuple[pm.Val, ...]:
    return tuple(value for key, value in entries if key is None)


def _nominal_values(
    entries: tuple[tuple[str | None, pm.Val], ...],
) -> dict[str, pm.Val]:
    return {key: value for key, value in entries if key is not None}
