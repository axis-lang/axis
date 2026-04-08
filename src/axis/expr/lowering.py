from __future__ import annotations

from typing import Any, NoReturn, cast

import protomorph as pm

from axis import log, syn
from axis.literals import Wildcard
from axis.sem.binding import BindingStruct

CONFORMS_FACT = "std.facts.Conforms"
EXTENDS_FACT = "std.facts.Extends"
type BoundResult = pm.Result[log.Report, Any]
type SpecResult = pm.Result[log.Report, pm.Spec]
type TupleResult = pm.Result[log.Report, pm.Tuple]


class _TupleElementBound(pm.Builtin):
    key: str | None
    value: pm.Val


def build_compound_bound(
    components: tuple[syn.Expr, ...],
    scope: syn.ScopeLike,
) -> BoundResult:
    if not components:
        return _error_result(None, "empty compound expression")

    *qualifier_exprs, underlying_expr = components
    if not qualifier_exprs:
        return underlying_expr.to_bound(scope)

    underlying_result = underlying_expr.to_bound(scope)
    if underlying_result.is_err:
        return underlying_result

    underlying_type_result = as_type_bound_val(underlying_result.unwrap().fetch(), underlying_expr)
    if underlying_type_result.is_err:
        return cast(BoundResult, underlying_type_result)

    current = cast(pm.Type, underlying_type_result.unwrap().fetch())
    for qualifier_expr in reversed(qualifier_exprs):
        qualifier_result = qualifier_expr.to_bound(scope)
        if qualifier_result.is_err:
            return qualifier_result

        qualifier_spec_result = as_qualifier_ref(qualifier_result.unwrap().fetch(), qualifier_expr)
        if qualifier_spec_result.is_err:
            return cast(BoundResult, qualifier_spec_result)

        current = cast(pm.Type, pm.Qual.of(current, cast(pm.Spec, qualifier_spec_result.unwrap().fetch())))

    return _ok_result(current)


def build_term(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> BoundResult | None:
    if bound_expr is None:
        return None

    try:
        return bound_expr.to_bound(scope)
    except syn.BoundLoweringError as exc:
        return _error_result(bound_expr, str(exc))


def build_bound(bound_expr: syn.Expr | None, scope: syn.ScopeLike) -> BoundResult | None:
    return build_term(bound_expr, scope)


def build_default(default_expr: syn.Expr | None, scope: syn.ScopeLike) -> BoundResult | None:
    return build_term(default_expr, scope)


def build_extends_fact(
    bound_expr: syn.Expr | None,
    scope: syn.ScopeLike,
) -> SpecResult | None:
    if bound_expr is None:
        return None

    term_result = build_term(bound_expr, scope)
    if term_result is None or term_result.is_err:
        return cast(SpecResult | None, term_result)

    from axis import expr as expr_module

    self_result = scope.lookup(expr_module.Sym(name="Self"), origin=bound_expr)
    if self_result.is_err:
        return cast(SpecResult, self_result)

    return _ok_result(
        pm.Spec.of(
            EXTENDS_FACT,
            self_result.unwrap().fetch(),
            **{"from": _fact_target_term(term_result.unwrap().fetch())},
        )
    )


def build_fact(
    fact_expr: syn.Expr | None,
    scope: syn.ScopeLike,
    *,
    scope_ref: pm.Anchor | None = None,
) -> SpecResult | None:
    if fact_expr is None:
        return None

    from axis import expr as expr_module

    match fact_expr:
        case expr_module.Index(origin=origin_expr, indices=indices_expr):
            args_result = build_spec_args(indices_expr, scope)
            if args_result is not None and args_result.is_err:
                return cast(SpecResult, args_result)

            anchor = origin_expr.to_anchor(scope_ref)
            positional: list[object] = []
            nominal: dict[str, object] = {}
            if args_result is not None:
                args = cast(pm.Tuple, args_result.unwrap())
                descriptor = args.descriptor
                if isinstance(descriptor, pm.IndexedType):
                    for key, value in zip(descriptor.index.content, args.content):
                        if key is None:
                            positional.append(value)
                        else:
                            nominal[str(key)] = value
                else:
                    positional.extend(args.content)
            return _ok_result(pm.Spec.of(anchor, *positional, **nominal))
        case expr_module.Sym() | expr_module.Member():
            return _ok_result(pm.Spec.of(fact_expr.to_anchor(scope_ref)))

    term_result = build_term(fact_expr, scope)
    if term_result is None or term_result.is_err:
        return cast(SpecResult | None, term_result)

    term = term_result.unwrap().fetch()
    if isinstance(term, pm.Spec):
        return _ok_result(term)
    if isinstance(term, pm.Anchor):
        return _ok_result(pm.Spec.of(term))
    return _error_result(fact_expr, "Claim head must be a fact-like expression")


def build_goal(
    goal_expr: syn.Expr | None,
    scope: syn.ScopeLike,
    *,
    scope_ref: pm.Anchor | None = None,
) -> SpecResult | None:
    return build_fact(goal_expr, scope, scope_ref=scope_ref)


def build_binding_pattern(bindings: BindingStruct, scope: syn.ScopeLike) -> BoundResult:
    if bindings.spread is not None or bindings.open_tail:
        return _error_result(
            bindings.spread.origin if bindings.spread is not None else None,
            "spread/open-tail binding patterns are not implemented yet",
        )

    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for field in bindings.fields:
        built = build_tuple_element_bound(field.origin, scope)
        if built is None:
            continue
        if built.is_err:
            return cast(BoundResult, built)
        item = cast(_TupleElementBound, built.unwrap().fetch())
        key, value = item.key, item.value
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return _ok_result(pm.VaryingType.new(*positional, **nominal))


def bound_as_type(
    bound: object | None,
    *,
    bridge: object | None = None,
) -> pm.Type | None:
    _ = bridge
    if bound is None:
        return None
    if isinstance(bound, pm.Type):
        return bound
    if isinstance(bound, pm.Anchor):
        return pm.Spec.of(bound)
    if isinstance(bound, pm.Val):
        value = bound.fetch()
        if isinstance(value, pm.Type):
            return value
        if isinstance(value, pm.Anchor):
            return pm.Spec.of(value)
    return None


def build_spec_args(indices_expr: syn.Expr, scope: syn.ScopeLike) -> TupleResult | None:
    from axis import expr as expr_module

    if not isinstance(indices_expr, expr_module.Tuple):
        indices_expr = expr_module.Tuple(
            elements=(expr_module.Tuple.Positional(value=indices_expr),)
        )

    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for element in indices_expr.elements:
        built = build_tuple_element_bound(element, scope)
        if built is None:
            continue
        if built.is_err:
            return cast(TupleResult, built)
        item = cast(_TupleElementBound, built.unwrap().fetch())
        key, value = item.key, item.value
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value

    if not positional and not nominal:
        return None

    return _ok_result(pm.VaryingType.new(*positional, **nominal))


def build_tuple_bound(
    elements: tuple[syn.Node, ...],
    scope: syn.ScopeLike,
) -> BoundResult:
    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for element in elements:
        built = build_tuple_element_bound(element, scope)
        if built is None:
            continue
        if built.is_err:
            return cast(BoundResult, built)
        item = cast(_TupleElementBound, built.unwrap().fetch())
        key, value = item.key, item.value
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return _ok_result(pm.VaryingType.new(*positional, **nominal))


def build_tuple_element_bound(
    element: syn.Node,
    scope: syn.ScopeLike,
) -> pm.Result[log.Report, _TupleElementBound] | None:
    from axis import expr as expr_module

    match element:
        case expr_module.Tuple.Positional(value=value_expr):
            value_result = build_term(value_expr, scope)
            if value_result is None:
                return None
            if value_result.is_err:
                return cast(pm.Result[log.Report, _TupleElementBound], value_result)
            return _ok_result(_TupleElementBound(key=None, value=value_result.unwrap()))
        case expr_module.Tuple.Nominal(key=key_expr, value=value_expr):
            if value_expr is None:
                value_expr = key_expr
            value_result = build_term(value_expr, scope)
            if value_result is None:
                return None
            if value_result.is_err:
                return cast(pm.Result[log.Report, _TupleElementBound], value_result)
            return _ok_result(
                _TupleElementBound(
                    key=expr_module.to_slot_name(key_expr),
                    value=value_result.unwrap(),
                )
            )
        case _:
            return None


def literal_to_bound(literal: object, origin: syn.Expr) -> BoundResult:
    if literal is Wildcard:
        return _ok_result(pm.WILDCARD)
    if literal is Ellipsis:
        return _ok_result(pm.ELLIPSIS)
    if not isinstance(literal, (int, float, str, bool, type(None))):
        return _error_result(origin, f"unsupported literal type {type(literal).__name__}")
    return _ok_result(pm.val(literal))


def as_qualifier_ref(
    bound_val: object,
    origin: syn.Expr | None,
) -> SpecResult:
    if isinstance(bound_val, pm.Spec):
        return _ok_result(bound_val)
    if isinstance(bound_val, pm.Anchor):
        return _ok_result(pm.Spec.of(bound_val))
    if isinstance(bound_val, pm.Val):
        fetched = bound_val.fetch()
        if isinstance(fetched, pm.Spec):
            return _ok_result(fetched)
        if isinstance(fetched, pm.Anchor):
            return _ok_result(pm.Spec.of(fetched))
    return _error_result(
        origin,
        f"qualifier base must be Anchor or Spec, got {val_type_name(bound_val)}",
    )


def as_type_bound_val(
    bound_val: object,
    origin: syn.Expr | None,
) -> pm.Result[log.Report, pm.Type]:
    bound_type = bound_as_type(bound_val)
    if bound_type is not None:
        return _ok_result(bound_type)
    return _error_result(
        origin,
        f"expected a type-like bound, got {val_type_name(bound_val)}",
    )


def val_type_name(value: object | None) -> str:
    return type(value).__name__ if value is not None else "None"


def unsupported_bound(bound: syn.Expr | None, message: str) -> NoReturn:
    _ = bound
    raise syn.BoundLoweringError(message)


def unsupported_bound_exception(bound: syn.Expr | None, message: str) -> syn.BoundLoweringError:
    return syn.BoundLoweringError(f"{message}: {bound!r}" if bound is not None else message)


def _binding_bound(binding: BindingStruct.Field, scope: syn.ScopeLike) -> BoundResult | None:
    return build_bound(binding.bound_expr, scope)


def _fact_target_term(term: object) -> object:
    type_ = bound_as_type(term)
    return term if type_ is None else type_

def _error_result(origin: syn.Node | None, message: str) -> pm.Result[log.Report, Any]:
    report = log.error("Unsupported bound expression").label(origin, message).build()
    return pm.Result.err(pm.val(report))


def _ok_result[T](value: T) -> pm.Result[log.Report, T]:
    return pm.Result.ok(pm.val(value))
