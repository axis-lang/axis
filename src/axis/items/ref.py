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


def scope_ref_from_item(item: syn.Item) -> dom.Ref | None:
    parent = getattr(item, "parent", None)
    while isinstance(parent, syn.Item):
        if hasattr(parent, "ref"):
            return getattr(parent, "ref")
        parent = getattr(parent, "parent", None)
    return None


def _const_from_expr(node: syn.Expr, scope: dom.Ref | None) -> dom.Const:
    match node:
        case expr.Lit(value=value):
            if value is Ellipsis or value is WILDCARD:
                return dom.Const.from_literal(str(value))
            return dom.Const.from_literal(cast(dom.Data, value))
        case expr.Sym(name=name):
            return dom.Const.from_type_data(dom.Type.var(name), ("var", name))
        case expr.Member() | expr.Index() | expr.Compound() | expr.Apply():
            ref = ref_from_expr(node, scope)
            return dom.Const.from_type_data(ref.type, ref.data)
        case _:
            return dom.Const.from_literal(str(node))


def spec_from_expr(node: syn.Expr, scope: dom.Ref | None) -> dom.Tuple[str, dom.Const]:
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
        return dom.Tuple.from_keys(tuple(keys), tuple(values))
    return dom.Tuple.from_keys((None,), (_const_from_expr(node, scope),))


def spec_from_components(
    components: Iterable[syn.Expr], scope: dom.Ref | None
) -> dom.Tuple[str, dom.Const]:
    items = tuple(components)
    if not items:
        return dom.Tuple.EMPTY
    keys = (None,) * len(items)
    values = tuple(_const_from_expr(item, scope) for item in items)
    return dom.Tuple.from_keys(keys, values)


def ref_with_spec(base: dom.Ref, spec: dom.Tuple[str, dom.Const]) -> dom.Ref:
    if len(spec.values) == 0:
        return base

    base_values = tuple(
        dom.Const.from_type_data(type_, data)
        for type_, data in zip(base.type.spec.values, base.data.spec)
    )
    keys = base.type.spec.index.keys + spec.index.keys
    values = base_values + spec.values
    combined = dom.Tuple.from_keys(keys, values)
    spec_types = dom.Tuple(
        index=combined.index,
        values=tuple(value.type for value in combined.values),
    )
    return dom.Ref(
        type=dom.Ref.Type(parent=base.type.parent, spec=spec_types),
        data=dom.Ref.Data(
            parent=base.data.parent,
            member=base.data.member,
            spec=tuple(value.data for value in combined.values),
        ),
    )


def ref_from_expr(node: syn.Expr, scope: dom.Ref | None = None) -> dom.Ref:
    match node:
        case expr.Compound(components=components):
            if len(components) == 0:
                raise ValueError("Empty compound expression")
            base = ref_from_expr(components[0], scope)
            spec = spec_from_components(components[1:], scope)
            return ref_with_spec(base, spec)
        case expr.Sym(name=name):
            if scope is None:
                return dom.Ref.root(name)
            return scope.child(name)
        case expr.Member(of=of_expr, name=name):
            base = ref_from_expr(of_expr, scope)
            return base.child(name)
        case expr.Index(origin=origin_expr, indices=indices):
            base = ref_from_expr(origin_expr, scope)
            spec = spec_from_expr(indices, scope)
            return ref_with_spec(base, spec)
        case expr.Apply(function=function_expr):
            return ref_from_expr(function_expr, scope)
        case _:
            raise ValueError(f"Unsupported ref expression: {node}")
