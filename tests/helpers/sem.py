from __future__ import annotations

from typing import cast

import protomorph as pm

from axis import log, syn
from axis.expr.ir.bound import bound_as_type, build_bound, build_default, build_term


def _unwrap_result[T](value: pm.Result["log.Report", T], source: str):
    if value.is_err:
        raise AssertionError(f"Expected successful semantic value from {source!r}, got {value!r}")
    return value.unwrap().fetch()


def parse(source: str) -> syn.Expr:
    return syn.Expr.from_str(source)


def bound(source: str, scope) -> pm.Val:
    value = build_bound(parse(source), scope)
    assert value is not None
    return _unwrap_result(value, source)


def default(source: str, scope) -> pm.Val:
    value = build_default(parse(source), scope)
    assert value is not None
    return _unwrap_result(value, source)


def term(source: str, scope) -> pm.Val:
    value = build_term(parse(source), scope)
    assert value is not None
    return _unwrap_result(value, source)


def type_bound(source: str, scope) -> pm.Type:
    value = bound(source, scope)
    resolved = bound_as_type(value)
    if resolved is None:
        raise AssertionError(f"Expected type-like bound from {source!r}, got {value!r}")
    return resolved


def project(type_source: str, key: str | int, scope, *, pkg) -> pm.Type:
    return pkg.project(type_bound(type_source, scope), key)


def layout(type_source: str, scope, *, pkg) -> pm.Layout | None:
    return pkg.layout(type_bound(type_source, scope))


def bound_type_data(source: str, scope) -> pm.Type:
    value = build_term(parse(source), scope)
    assert value is not None
    value = _unwrap_result(value, source)
    if not isinstance(value, pm.Const):
        raise AssertionError(f"Expected Const from {source!r}, got {value!r}")
    if not isinstance(value.__data__, pm.Type):
        raise AssertionError(f"Expected Const[type] from {source!r}, got {value!r}")
    return cast(pm.Type, value.__data__)
