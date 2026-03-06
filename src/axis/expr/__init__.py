from __future__ import annotations

import builtins
from typing import Iterable, Tuple as TypingTuple, cast

from axis import dom, syn
from axis.log import report as log
from axis.literals import Wildcard

from .apply import *
from .infix import *
from .prefix import *
from .index import *
from .sym import *
from .member import *
from .tuple import *
from .lit import *
from .compound import *
from .trail import *


def as_anchor(ast: syn.Expr, scope_ref: dom.Anchor | None) -> dom.Anchor:
    match ast:
        case Sym(name=name, at=at):
            if at is not None:
                log.warn("Anchor cannot @-qualify a symbol").label(ast).emit()
            return dom.Anchor.root(name) if scope_ref is None else scope_ref.child(name)
        case Member(of=of, name=name):
            return as_anchor(of, scope_ref).child(name)
        case _:
            log.error(f"Unsupported anchor expression type ({type(ast)})").label(
                ast
            ).throw()


def _emit_diag(message: str, node: syn.Node | None) -> None:
    report = log.error(message)
    span = getattr(node, "span", None) if node is not None else None
    if span is not None and node is not None:
        try:
            if span.source.lines:
                report = report.label(node, message)
        except Exception:
            pass
    report.emit()


def _throw_diag(message: str, node: syn.Node | None) -> None:
    report = log.error(message)
    span = getattr(node, "span", None) if node is not None else None
    if span is not None and node is not None:
        try:
            if span.source.lines:
                report = report.label(node, message)
        except Exception:
            pass
    report.throw()


def to_slot_name(key: syn.Expr) -> str:
    match key:
        case Sym(name=name):
            return name
        case _:
            log.error("Unsupported tuple key expression").label(key).throw()


def name_of(node: syn.Expr) -> str:
    match node:
        case Member(name=name):
            return name
        case Sym(name=name):
            return name
        case Compound(components=components) if components:
            return name_of(components[0])
        case Index(origin=origin_expr):
            return name_of(origin_expr)
        case Apply(function=function_expr):
            return name_of(function_expr)
        case _:
            log.error("Cannot derive name from expression").label(node).throw()


def as_sym(node: syn.Expr) -> Sym:
    match node:
        case Sym() as sym:
            return sym
        # case Member() as member:
        #     return Sym(name=member.name).with_span_of(node)
        # case Compound(components=components) if components:
        #     return as_sym(components[0]).with_span_of(node)
        # case Index(origin=origin_expr):
        #     return as_sym(origin_expr).with_span_of(node)
        # case Apply(function=function_expr):
        #     return as_sym(function_expr).with_span_of(node)
        case _:
            return Sym(name=name_of(node)).with_span_of(node)


def to_anchor_ref(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Anchor | None:
    match node:
        case Compound(components=components):
            if len(components) == 0:
                _emit_diag("Empty compound expression", node)
                return None
            base = to_anchor_ref(components[0], scope)
            if base is None:
                return None
            if len(components) > 1:
                _emit_diag("Specialization ignored for anchor resolution", node)
            return base
        case Sym(name=name):
            if scope is None:
                return dom.Anchor.from_str(name)
            return scope.child(name)
        case Member(of=of_expr, name=name):
            base = to_spec_ref(of_expr, scope)
            if base is None:
                return None
            if isinstance(base, dom.Spec):
                _emit_diag("Cannot access member of a specialized ref", node)
                return base.anchor
            return cast(dom.Anchor, base).child(name)
        case Index(origin=origin_expr, indices=_):
            base = to_anchor_ref(origin_expr, scope)
            if base is None:
                return None
            _emit_diag("Specialization ignored for anchor resolution", node)
            return base
        case Apply(function=function_expr):
            return to_anchor_ref(function_expr, scope=scope)
        case _:
            _emit_diag("Unsupported ref expression", node)
            return None


def to_spec_ref(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Ref | None:
    match node:
        case Compound(components=components):
            if len(components) == 0:
                _emit_diag("Empty compound expression", node)
                return None
            base = to_spec_ref(components[0], scope)
            if base is None:
                return None
            spec = to_spec_components(components[1:], scope)
            if spec is None:
                return base
            if isinstance(base, dom.Spec):
                _emit_diag("Cannot access member of a specialized ref", node)
                return base
            return cast(dom.Anchor, base).specialize(spec)
        case Sym(name=name):
            if scope is None:
                return dom.Anchor.from_str(name)
            return scope.child(name)
        case Member(of=of_expr, name=name):
            base = to_spec_ref(of_expr, scope)
            if base is None:
                return None
            if isinstance(base, dom.Spec):
                _emit_diag("Cannot access member of a specialized ref", node)
                return base
            return cast(dom.Anchor, base).child(name)
        case Index(origin=origin_expr, indices=indices):
            base = to_spec_ref(origin_expr, scope)
            if base is None:
                return None
            if isinstance(base, dom.Spec):
                _emit_diag("Cannot specialize an already specialized ref", node)
                return base
            spec = to_spec(indices, scope)
            if spec is None:
                return base
            return cast(dom.Anchor, base).specialize(spec)
        case Apply(function=function_expr):
            return to_spec_ref(function_expr, scope=scope)
        case _:
            _emit_diag("Unsupported ref expression", node)
            return None


def _struct_const_from_values(
    keys: TypingTuple[str | None, ...], values: TypingTuple[dom.Const, ...]
) -> dom.Const:
    index = dom.Struct.Index(builtins.tuple(keys))
    fields = dom.Struct(
        index=index, values=builtins.tuple(value.type for value in values)
    )
    struct_type = dom.StructType(fields=cast(dom.Struct[str, dom.Type], fields))
    return dom.Const(
        type=struct_type, data=builtins.tuple(value.data for value in values)
    )


def to_const(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Const:
    match node:
        case Lit(value=value):
            if value is Ellipsis or value is Wildcard:
                return dom.Const.of_literal(str(value))
            return dom.Const.of_literal(cast(dom.Literal, value))
        case Sym():
            _throw_diag("Cannot evaluate symbol to constant", node)
        case Member() | Index() | Compound() | Apply():
            ref = to_spec_ref(node, scope)
            if ref is None:
                _throw_diag("Cannot resolve ref for constant", node)
            assert ref is not None
            return dom.Const(type=ref.type, data=ref.data)
        case _:
            _throw_diag("Unsupported expression for constant evaluation", node)
    raise ValueError("Unreachable")


def to_spec(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Const | None:
    if isinstance(node, Tuple):
        keys: list[str | None] = []
        values: list[dom.Const] = []
        for element in node.elements:
            match element:
                case Tuple.Positional(value=value):
                    if value is None:
                        continue
                    keys.append(None)
                    values.append(to_const(value, scope))
                case Tuple.Nominal(key=key, bound=_, value=value):
                    value_expr = value if value is not None else key
                    keys.append(to_slot_name(key))
                    values.append(to_const(value_expr, scope))
                case _:
                    _throw_diag("Unsupported tuple element", element)
        if not values:
            return None
        return _struct_const_from_values(builtins.tuple(keys), builtins.tuple(values))
    return _struct_const_from_values((None,), (to_const(node, scope),))


def to_spec_components(
    components: Iterable[syn.Expr], scope: dom.Anchor | None = None
) -> dom.Const | None:
    items = builtins.tuple(components)
    if not items:
        return None
    keys = (None,) * len(items)
    values = builtins.tuple(to_const(item, scope) for item in items)
    return _struct_const_from_values(keys, values)
