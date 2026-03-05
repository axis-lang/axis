from __future__ import annotations

from typing import Iterable, cast

from axis import dom, expr, syn
from axis.literals import WILDCARD


def slot_name_from_key(key: syn.Expr) -> str:
    if isinstance(key, expr.Sym):
        return key.name
    return str(key)


def name_from_expr(node: syn.Expr) -> str:
    match node:
        case expr.Compound(components=components) if components:
            return name_from_expr(components[0])
        case expr.Sym(name=name):
            return name
        case expr.Member(name=name):
            return name
        case expr.Index(origin=origin_expr):
            return name_from_expr(origin_expr)
        case expr.Apply(function=function_expr):
            return name_from_expr(function_expr)
        case _:
            return str(node)


def sym_from_expr(node: syn.Expr) -> expr.Sym:
    match node:
        case expr.Sym() as sym:
            return sym
        case expr.Member() as member:
            return member.as_sym()
        case expr.Compound(components=components) if components:
            return sym_from_expr(components[0]).with_span_of(node)
        case expr.Index(origin=origin_expr):
            return sym_from_expr(origin_expr).with_span_of(node)
        case expr.Apply(function=function_expr):
            return sym_from_expr(function_expr).with_span_of(node)
        case _:
            return expr.Sym(name=name_from_expr(node)).with_span_of(node)


def scope_ref_from_item(item: syn.Item) -> dom.Anchor | None:
    parent = getattr(item, "parent", None)
    while isinstance(parent, syn.Item):
        if hasattr(parent, "ref"):
            ref = getattr(parent, "ref")
            if isinstance(ref, dom.Ref):
                return ref.anchor
            return ref
        parent = getattr(parent, "parent", None)
    return None


def _const_from_expr(node: syn.Expr, scope: dom.Anchor | None) -> dom.Const:
    match node:
        case expr.Lit(value=value):
            if value is Ellipsis or value is WILDCARD:
                return dom.Const.new_literal(str(value))
            return dom.Const.new_literal(cast(dom.Literal, value))
        case expr.Sym(name=name):
            return dom.Const(type=dom.Var.Type(id=name), data=name)
        case expr.Member() | expr.Index() | expr.Compound() | expr.Apply():
            ref = ref_from_expr(node, scope)
            return dom.Const(type=ref.type, data=ref.data)
        case _:
            return dom.Const.new_literal(str(node))


def _struct_const_from_values(
    keys: tuple[str | None, ...], values: tuple[dom.Const, ...]
) -> dom.Const:
    index = dom.Struct.Index(keys)
    fields = dom.Struct(index=index, values=tuple(value.type for value in values))
    struct_type = dom.StructType(fields=cast(dom.Struct[str, dom.Type], fields))
    return dom.Const(type=struct_type, data=tuple(value.data for value in values))


def spec_from_expr(node: syn.Expr, scope: dom.Anchor | None) -> dom.Const | None:
    if isinstance(node, expr.Tuple):
        keys: list[str | None] = []
        values: list[dom.Const] = []
        for element in node.elements:
            match element:
                case expr.Tuple.Positional(value=value):
                    if value is None:
                        continue
                    keys.append(None)
                    values.append(_const_from_expr(value, scope))
                case expr.Tuple.Nominal(key=key, bound=_, value=value):
                    value_expr = value if value is not None else key
                    keys.append(slot_name_from_key(key))
                    values.append(_const_from_expr(value_expr, scope))
                case _:
                    raise ValueError(f"Unsupported tuple element: {element}")
        if not values:
            return None
        return _struct_const_from_values(tuple(keys), tuple(values))
    return _struct_const_from_values((None,), (_const_from_expr(node, scope),))


def bound_from_expr(node: syn.Expr, scope: dom.Anchor | None) -> dom.Bound:
    match node:
        case expr.Lit(value=value):
            if value is Ellipsis or value is WILDCARD:
                return dom.Bound.from_literal(str(value))
            return dom.Bound.from_literal(cast(dom.Literal, value))
        case expr.Sym(name=name):
            return dom.Bound.var(name)
        case expr.Member() | expr.Index() | expr.Compound() | expr.Apply():
            ref = ref_from_expr(node, scope)
            return dom.Bound.from_ref(ref)
        case _:
            return dom.Bound.from_literal(str(node))


def spec_from_components(
    components: Iterable[syn.Expr], scope: dom.Anchor | None
) -> dom.Const | None:
    items = tuple(components)
    if not items:
        return None
    keys = (None,) * len(items)
    values = tuple(_const_from_expr(item, scope) for item in items)
    return _struct_const_from_values(keys, values)


def ref_with_spec(base: dom.Anchor, spec: dom.Const | None) -> dom.Spec:
    if not isinstance(base, dom.Anchor):
        raise TypeError("ref_with_spec requires an Anchor base")
    return base.specialize(spec)


def ref_from_expr(node: syn.Expr, scope: dom.Anchor | None = None) -> dom.Ref:
    match node:
        case expr.Compound(components=components):
            if len(components) == 0:
                raise ValueError("Empty compound expression")
            base = ref_from_expr(components[0], scope)
            spec = spec_from_components(components[1:], scope)
            if spec is None:
                return base
            if isinstance(base, dom.Spec):
                return base
            return ref_with_spec(cast(dom.Anchor, base), spec)
        case expr.Sym(name=name):
            if scope is None:
                return dom.Anchor.from_str(name)
            return scope.child(name)
        case expr.Member(of=of_expr, name=name):
            base = ref_from_expr(of_expr, scope)
            if isinstance(base, dom.Spec):
                raise ValueError("Cannot access member of a specialized ref")
            return cast(dom.Anchor, base).child(name)
        case expr.Index(origin=origin_expr, indices=indices):
            base = ref_from_expr(origin_expr, scope)
            if isinstance(base, dom.Spec):
                raise ValueError("Cannot specialize an already specialized ref")
            spec = spec_from_expr(indices, scope)
            return ref_with_spec(cast(dom.Anchor, base), spec)
        case expr.Apply(function=function_expr):
            return ref_from_expr(function_expr, scope)
        case _:
            raise ValueError(f"Unsupported ref expression: {node}")
