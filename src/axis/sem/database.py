from __future__ import annotations

from itertools import combinations
from typing import Iterable, Optional, TYPE_CHECKING, TypeAlias

from protobase import Record, frozendict

from axis import expr, syn

from .entity import Entity, OverloadBucket, ReturnEntry
from .ref_shape import RefShape
from .shapes import SlotShape, TupleShape



class Database(Record, frozen=True):
    type EntitiesByShape = frozendict[RefShape, Entity]
    type MembersByScope = frozendict[RefShape, frozendict[str, RefShape]]

    entities_by_shape: EntitiesByShape
    members_by_scope: MembersByScope

    def specialize(self, ref: RefShape) -> Entity.View | None:
        base = self.entities_by_shape.get(ref)
        if base is None:
            base = next(
                (
                    entity
                    for shape, entity in self.entities_by_shape.items()
                    if shape.segments == ref.segments
                ),
                None,
            )
        if base is None:
            return None
        return base.view(ref)

    class Builder:
        def __init__(self) -> None:
            self._entities: dict[RefShape, Entity.Builder] = {}
            self._members_by_scope: dict[RefShape, dict[str, RefShape]] = {}
            self._root_scope: RefShape = RefShape(segments=())

        def _builder(self, ref_shape: RefShape):
            builder = self._entities.get(ref_shape)
            if builder is None:
                builder = Entity.Builder(ref_shape)
                self._entities[ref_shape] = builder
            return builder

        def ref_shape_from_expr(
            self, node: syn.Expr, scope: Optional[RefShape] = None
        ) -> RefShape:
            match node:
                case expr.Compound(components=components):
                    if len(components) == 0:
                        raise ValueError("Empty compound expression")
                    base = self.ref_shape_from_expr(components[0], scope)
                    params_tuple = tuple(components[1:])
                    return RefShape(
                        segments=base.segments,
                        params_exprs=base.params_exprs + params_tuple,
                        scope=base.scope,
                    )
                case expr.Sym(name=name):
                    segments = (name,) if scope is None else scope.segments + (name,)
                    return RefShape(segments=segments, scope=scope)
                case expr.Member(of=of_expr, name=name):
                    base = self.ref_shape_from_expr(of_expr, scope)
                    return RefShape(segments=base.segments + (name,), scope=base)
                case expr.Index(origin=origin_expr, indices=indices):
                    base = self.ref_shape_from_expr(origin_expr, scope)
                    if isinstance(indices, expr.Tuple):
                        params_tuple = tuple(
                            elem.value
                            if isinstance(elem, expr.Tuple.Positional)
                            else elem.key
                            for elem in indices.elements
                            if (isinstance(elem, expr.Tuple.Positional) and elem.value is not None)
                            or isinstance(elem, expr.Tuple.Nominal)
                        )
                    else:
                        params_tuple = (indices,)
                    return RefShape(
                        segments=base.segments,
                        params_exprs=base.params_exprs + params_tuple,
                        scope=base.scope,
                    )
                case expr.Apply(function=function_expr):
                    return self.ref_shape_from_expr(function_expr, scope)
                case _:
                    raise ValueError(f"Unsupported ref expression: {node}")

        def scope_from_ctx(self, ctx: syn.Item) -> RefShape:
            parent = getattr(ctx, "parent", None)
            if isinstance(parent, syn.Item):
                return self.ref_shape_from_item(parent)
            return self._root_scope

        def ref_shape_from_item(self, item: syn.Item) -> RefShape:
            scope = self.scope_from_ctx(item)
            if hasattr(item, "path"):
                path = getattr(item, "path")
                if isinstance(path, syn.Expr):
                    return self.ref_shape_from_expr(path, scope)
            if hasattr(item, "expr"):
                expr_node = getattr(item, "expr")
                if isinstance(expr_node, syn.Expr):
                    return self.ref_shape_from_expr(expr_node, scope)
            if hasattr(item, "key"):
                key = getattr(item, "key")
                if isinstance(key, syn.Expr):
                    return self.ref_shape_from_expr(key, scope)
            raise ValueError(f"Cannot derive RefShape for item {type(item).__name__}")

        def namespace(self, scope_expr: syn.Expr, origin: syn.Node, ctx: syn.Item) -> None:
            scope = self.ref_shape_from_expr(scope_expr, self.scope_from_ctx(ctx))
            self._builder(scope)

        def member(self, member_expr: syn.Expr, origin: syn.Node, ctx: syn.Item) -> None:
            scope = self.scope_from_ctx(ctx)
            name = _name_from_expr(member_expr)
            target = self.ref_shape_from_expr(member_expr, scope)
            self._members_by_scope.setdefault(scope, {})[name] = target
            self._builder(scope).add_member(name, target, origin, ctx)

        def overload(
            self,
            owner_expr: syn.Expr,
            takes_expr: syn.Expr,
            where_expr: Optional[syn.Expr],
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            owner = self.ref_shape_from_expr(owner_expr, self.scope_from_ctx(ctx))
            takes_shape = _shape_from_expr(takes_expr)
            takes_defaults = (
                _defaults_from_tuple(takes_expr)
                if isinstance(takes_expr, expr.Tuple)
                else ()
            )
            where_shape = _shape_from_expr(where_expr) if where_expr else None
            where_defaults = (
                _defaults_from_tuple(where_expr)
                if isinstance(where_expr, expr.Tuple)
                else ()
            )

            takes_shapes = _expand_default_shapes(takes_shape, takes_defaults)
            where_shapes = (
                _expand_default_shapes(where_shape, where_defaults)
                if where_shape
                else (None,)
            )

            builder = self._builder(owner)
            for ts in takes_shapes:
                for ws in where_shapes:
                    builder.add_overload(ts, ws, origin, ctx)

        def returns(
            self,
            owner_expr: syn.Expr,
            takes_expr: Optional[syn.Expr],
            where_expr: Optional[syn.Expr],
            returns_expr: syn.Expr,
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            owner = self.ref_shape_from_expr(owner_expr, self.scope_from_ctx(ctx))
            takes_shape = _shape_from_expr(takes_expr) if takes_expr else None
            takes_defaults = (
                _defaults_from_tuple(takes_expr)
                if isinstance(takes_expr, expr.Tuple)
                else ()
            )
            where_shape = _shape_from_expr(where_expr) if where_expr else None
            where_defaults = (
                _defaults_from_tuple(where_expr)
                if isinstance(where_expr, expr.Tuple)
                else ()
            )
            returns_shape = _shape_from_expr(returns_expr)

            takes_shapes = (
                _expand_default_shapes(takes_shape, takes_defaults)
                if takes_shape
                else (None,)
            )
            where_shapes = (
                _expand_default_shapes(where_shape, where_defaults)
                if where_shape
                else (None,)
            )

            builder = self._builder(owner)
            for ts in takes_shapes:
                for ws in where_shapes:
                    builder.add_return(ts, ws, returns_shape, origin, ctx)

        def constraint(
            self,
            owner_expr: syn.Expr,
            predicate: syn.Node,
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            owner = self.ref_shape_from_expr(owner_expr, self.scope_from_ctx(ctx))
            self._builder(owner).add_constraint(predicate, origin, ctx)

        def fact(
            self,
            owner_expr: syn.Expr,
            args: tuple[syn.Expr, ...],
            origin: syn.Node,
            ctx: syn.Item,
        ) -> None:
            owner = self.ref_shape_from_expr(owner_expr, self.scope_from_ctx(ctx))
            self._builder(owner).add_fact(args, origin, ctx)

        def build(self) -> "Database":
            entities = {ref: builder.build() for ref, builder in self._entities.items()}
            members_by_scope = {
                scope: frozendict(members)
                for scope, members in self._members_by_scope.items()
            }
            return Database(
                entities_by_shape=frozendict(entities),
                members_by_scope=frozendict(members_by_scope),
            )


def _slot_name_from_key(key: syn.Expr) -> Optional[str]:
    if isinstance(key, expr.Sym):
        return key.name
    return str(key)


def _shape_from_tuple(tup: expr.Tuple) -> TupleShape:
    slots: list[SlotShape] = []
    for pos, element in enumerate(tup.elements):
        match element:
            case expr.Tuple.Positional(value=value):
                slots.append(SlotShape(name=None, pos=pos, bound=value))
            case expr.Tuple.Nominal(key=key, bound=bound, value=_):
                slots.append(
                    SlotShape(
                        name=_slot_name_from_key(key),
                        pos=pos,
                        bound=bound,
                    )
                )
            case _:
                raise ValueError(f"Unsupported tuple element: {element}")

    return TupleShape(slots=tuple(slots))


def _shape_from_expr(node: syn.Expr) -> TupleShape:
    if isinstance(node, expr.Tuple):
        return _shape_from_tuple(node)
    return TupleShape(slots=(SlotShape(name=None, pos=0, bound=node),))


def _defaults_from_tuple(tup: expr.Tuple) -> tuple[int | str, ...]:
    defaults: list[int | str] = []
    for pos, element in enumerate(tup.elements):
        match element:
            case expr.Tuple.Nominal(key=key, value=value) if value is not None:
                name = _slot_name_from_key(key)
                defaults.append(name if name is not None else pos)
    return tuple(defaults)


def _normalize_default_positions(
    shape: TupleShape, defaults: Iterable[int | str]
) -> tuple[int, ...]:
    name_to_pos = {slot.name: slot.pos for slot in shape.slots if slot.name is not None}
    positions: list[int] = []
    for default in defaults:
        if isinstance(default, int):
            positions.append(default)
        else:
            pos = name_to_pos.get(default)
            if pos is None:
                continue
            positions.append(pos)
    return tuple(dict.fromkeys(positions))


def _shape_without_positions(shape: TupleShape, positions: set[int]) -> TupleShape:
    slots = tuple(slot for slot in shape.slots if slot.pos not in positions)
    return TupleShape(slots=slots)


def _expand_default_shapes(
    shape: TupleShape, defaults: Iterable[int | str]
) -> tuple[TupleShape, ...]:
    positions = _normalize_default_positions(shape, defaults)
    if not positions:
        return (shape,)

    expanded: list[TupleShape] = []
    positions_list = list(positions)
    for r in range(len(positions_list) + 1):
        for combo in combinations(positions_list, r):
            expanded.append(_shape_without_positions(shape, set(combo)))
    return tuple(expanded)


def _name_from_expr(node: syn.Expr) -> str:
    match node:
        case expr.Sym(name=name):
            return name
        case expr.Member(name=name):
            return name
        case expr.Index(origin=origin_expr):
            return _name_from_expr(origin_expr)
        case expr.Apply(function=function_expr):
            return _name_from_expr(function_expr)
        case _:
            return str(node)
