from __future__ import annotations

from typing import Iterable, cast

from axis import dom, syn
from axis.log import report as log
from axis.literals import Wildcard

from .apply import *
from .infix import *
from .prefix import *
from .index import *
from .sym import *
from .member import *
from .tuple_ import *
from .lit import *
from .compound import *
from .trail import *


def as_anchor(ast: syn.Expr, scope_ref: dom.Anchor | None) -> dom.Anchor:
    """Resolve an anchor path from a simple name/member expression."""
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


def to_slot_name(key: syn.Expr) -> str:
    """Extract a slot/field name from a nominal tuple key expression."""
    match key:
        case Sym(name=name):
            return name
        case _:
            log.error("Unsupported tuple key expression").label(key).throw()


def name_of(node: syn.Expr) -> str:
    """Derive a stable name for diagnostics from common expression shapes."""
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
    """Coerce an expression to Sym, preserving the original span."""
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
    """Resolve an expression into an anchor, ignoring specialization parts."""
    match node:
        case Compound(components=components):
            if len(components) == 0:
                log.error("Empty compound expression").label(node).emit()
                return None
            base = to_anchor_ref(components[0], scope)
            if base is None:
                return None
            if len(components) > 1:
                log.error("Specialization ignored for anchor resolution").label(node).emit()
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
                log.error("Cannot access member of a specialized ref").label(node).emit()
                return base.anchor
            return cast(dom.Anchor, base).child(name)
        case Index(origin=origin_expr, indices=_):
            base = to_anchor_ref(origin_expr, scope)
            if base is None:
                return None
            log.error("Specialization ignored for anchor resolution").label(node).emit()
            return base
        case Apply(function=function_expr):
            return to_anchor_ref(function_expr, scope=scope)
        case _:
            log.error("Unsupported ref expression").label(node).emit()
            return None


def to_spec_ref(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Ref | None:
    """Resolve an expression into a Ref (anchor or specialized ref) for types."""
    match node:
        case Compound(components=components):
            if len(components) == 0:
                log.error("Empty compound expression").label(node).emit()
                return None
            base = to_spec_ref(components[0], scope)
            if base is None:
                return None
            spec = to_spec_components(components[1:], scope)
            if spec is None:
                return base
            if isinstance(base, dom.Spec):
                log.error("Cannot access member of a specialized ref").label(node).emit()
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
                log.error("Cannot access member of a specialized ref").label(node).emit()
                return base
            return cast(dom.Anchor, base).child(name)
        case Index(origin=origin_expr, indices=indices):
            base = to_spec_ref(origin_expr, scope)
            if base is None:
                return None
            if isinstance(base, dom.Spec):
                log.error("Cannot specialize an already specialized ref").label(node).emit()
                return base
            spec = to_spec(indices, scope)
            if spec is None:
                return base
            return cast(dom.Anchor, base).specialize(spec)
        case Apply(function=function_expr):
            return to_spec_ref(function_expr, scope=scope)
        case _:
            log.error("Unsupported ref expression").label(node).emit()
            return None


def _struct_const_from_values(
    keys: tuple[str | None, ...], values: tuple[dom.Const, ...]
) -> dom.Const:
    """Build a Struct constant from aligned keys and constant values."""
    index = dom.Struct.Index(tuple(keys))
    fields = dom.Struct(
        index=index, values=tuple(value.type for value in values)
    )
    struct_type = dom.StructType(fields=cast(dom.Struct[str, dom.Type], fields))
    return dom.Const(
        type=struct_type, data=tuple(value.data for value in values)
    )


def to_const(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Const:
    """Evaluate an expression into a constant, erroring on symbols."""
    match node:
        case Lit(value=value):
            if value is Ellipsis or value is Wildcard:
                return dom.Const.of_literal(str(value))
            return dom.Const.of_literal(cast(dom.Literal, value))
        case Sym():
            log.error("Cannot evaluate symbol to constant").label(node).throw()
        case Member() | Index() | Compound() | Apply():
            ref = to_spec_ref(node, scope)
            if ref is None:
                log.error("Cannot resolve ref for constant").label(node).throw()
            assert ref is not None
            return dom.Const(type=ref.type, data=ref.data)
        case _:
            log.error("Unsupported expression for constant evaluation").label(node).throw()
    raise ValueError("Unreachable")


def to_spec(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Const | None:
    """Build a specialization constant from tuples or a single expression."""
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
                    log.error("Unsupported tuple element").label(element).throw()
        if not values:
            return None
        return _struct_const_from_values(tuple(keys), tuple(values))
    return _struct_const_from_values((None,), (to_const(node, scope),))


def to_spec_components(
    components: Iterable[syn.Expr], scope: dom.Anchor | None = None
) -> dom.Const | None:
    """Build a struct constant from ordered specialization components."""
    items = tuple(components)
    if not items:
        return None
    keys = (None,) * len(items)
    values = tuple(to_const(item, scope) for item in items)
    return _struct_const_from_values(keys, values)
