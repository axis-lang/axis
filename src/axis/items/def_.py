from __future__ import annotations
from itertools import combinations
from typing import ClassVar, Iterable, Literal, Optional

from protobase import flux, Missing

from axis import dom, syn, expr
from axis.sem import Entity, Scope
from .blocks import TupleBlock


from .item import Item
from .ref import (
    bound_from_expr,
    name_from_expr,
    ref_from_expr,
    scope_ref_from_item,
    slot_name_from_key,
    sym_from_expr,
)
from .scopes import parent_scope



class Def(Item, syn.ClassMatcher):

    class Where(TupleBlock):
        outline_keyword: ClassVar = "where"

    class Takes(TupleBlock):  # ExprBlock
        outline_keyword: ClassVar = "takes"
        expr: Optional[syn.Expr] = None

        @classmethod
        def build(
            cls,
            kw: str,
            *args,
            **kwargs,
        ):
            match args:
                case (":",):
                    expr, sep = None, ":"
                case (expr, ":"):
                    expr, sep = expr, ":"
                case _:
                    raise ValueError(f"Invalid args for {cls.__name__}: {args}")

            return super().build(kw, sep, expr=expr, **kwargs)

    class Returns(syn.Block):
        outline_keyword: ClassVar = "returns"
        expr: syn.Expr | None = None

        @classmethod
        def build(
            cls,
            kw: Literal["returns"],
            expr: syn.Expr,
            # *args,
            *,
            children: syn.Block.Children,
            **kwargs,
        ):
            kwargs.pop("realm", None)
            return cls(expr=expr, **kwargs)

    # class Expose(TupleBlock):
    #     outline_keyword: ClassVar = 'expose'

    # class Inherits(TupleBlock):
    #     outline_keyword: ClassVar = 'inherits'

    # class Derives(TupleBlock):
    #     outline_keyword: ClassVar = 'derives'

    outline_keyword: ClassVar = "def"
    outline_children: ClassVar = {
        Where: False,
        Takes: False,
        Returns: False,
        # Expose: False,
        # Inherits: False,
        # Derives: False,
    }

    # pkg: items.Package
    origin: syn.Expr | None = None
    where: Optional[Where] = None
    takes: tuple[Takes, ...] = ()
    returns: tuple[Returns, ...] = ()

    @classmethod
    def build(
        cls,
        kw: Literal["def"],
        expr: syn.Expr,
        *,
        # parent: Optional[syn.Item],
        # pkg: items.Package,
        children: tuple[syn.Block, ...],
        **kwargs,
    ):
        assert (
            kw == cls.outline_keyword
        ), f"Expected keyword {cls.outline_keyword}, got {kw}"
        # procesa las directivas where, takes, returns, expose, inherits, derive, etc..

        where: Optional[Def.Where] = None
        takes: list[Def.Takes] = []
        returns: list[Def.Returns] = []
        # expose: Optional[Def.Expose] = None
        # inherits: Optional[Def.Inherits] = None
        # derives: Optional[Def.Derives] = None
        for child in children:
            match child:
                case cls.Where() as w:
                    where = w
                case cls.Takes() as t:
                    takes.append(t)
                case cls.Returns() as r:
                    returns.append(r)
                # case cls.Expose() as e:
                #     expose = e
                # case cls.Inherits() as i:
                #     inherits = i
                # case cls.Derives() as d:
                #     derives = d

        # procesa la estructura de la expresion para determinar el tipo de definicion
        self = cls.match(
            expr,
            origin=expr,
            where=where,
            takes=tuple(takes),
            returns=tuple(returns),
            **kwargs,
        )

        if self is None: # esto debe ser un src.error y debe retornar Missing que sera ignorado.
            raise ValueError(f"Expression {expr} does not match any pattern for {cls.__name__}")

        return self
        # if self is not None:
        #     return self

        # return cls(
        #     origin=expr, **kwargs, where=where, takes=tuple(takes), returns=tuple(returns)
        # )

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        if self.origin is None:
            return frozenset()

        scope_ref = scope_ref_from_item(self)
        owner = ref_from_expr(self.origin, scope_ref)
        anchor = owner.anchor
        contributions: list[Entity.Contribution] = []

        if scope_ref is not None:
            contributions.append(
                Entity.Member(
                    anchor=scope_ref,
                    name=name_from_expr(self.origin),
                    target=owner,
                    origin=self.origin,
                    ctx=self,
                )
            )

        spec_struct = (
            _bounds_from_expr(self.where, scope_ref)
            if self.where is not None
            else _empty_bound_struct()
        )

        has_takes = bool(self.takes)
        has_returns = bool(self.returns)

        if not has_takes and not has_returns:
            if self.where is not None:
                contributions.append(
                    Entity.SpecContribution(
                        anchor=anchor,
                        spec=spec_struct,
                        origin=self.where,
                        ctx=self,
                    )
                )
            return frozenset(contributions)

        if has_takes:
            for takes in self.takes:
                takes_expr = takes.expr
                if takes_expr is None:
                    continue
                params_struct = _bounds_from_expr(takes_expr, scope_ref)
                defaults = (
                    _defaults_from_tuple(takes_expr)
                    if isinstance(takes_expr, expr.Tuple)
                    else ()
                )
                params_structs = _expand_default_shapes(params_struct, defaults)

                for params in params_structs:
                    contributions.append(
                        Entity.OverloadContribution(
                            anchor=anchor,
                            spec=spec_struct,
                            params=params,
                            origin=takes_expr,
                            ctx=self,
                        )
                    )
                    for ret in self.returns:
                        if ret.expr is None:
                            continue
                        contributions.append(
                            Entity.ImplContribution(
                                anchor=anchor,
                                spec=spec_struct,
                                params=params,
                                returns=bound_from_expr(ret.expr, scope_ref),
                                origin=ret.expr,
                                ctx=self,
                            )
                        )
        else:
            params = _empty_bound_struct()
            contributions.append(
                Entity.OverloadContribution(
                    anchor=anchor,
                    spec=spec_struct,
                    params=params,
                    origin=self.origin,
                    ctx=self,
                )
            )
            for ret in self.returns:
                if ret.expr is None:
                    continue
                contributions.append(
                    Entity.ImplContribution(
                        anchor=anchor,
                        spec=spec_struct,
                        params=params,
                        returns=bound_from_expr(ret.expr, scope_ref),
                        origin=ret.expr,
                        ctx=self,
                    )
                )

        return frozenset(contributions)

    @flux.property
    def scope(self) -> Scope:
        scope_name = name_from_expr(self.origin) if self.origin is not None else None
        builder = Scope.Builder(name=scope_name, parent=parent_scope(self))
        for takes in self.takes:
            _define_tuple_bindings(builder, takes)
        if self.where is not None:
            _define_tuple_bindings(builder, self.where)
        return builder.build()

class QualDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym $target"),
        syn.Expr.from_str("$sym[..$spec] $target"),
    )

    sym: expr.Sym | None = None
    # target y spec son parametros (takes)
    spec: Optional[expr.Tuple] = None
    target: syn.Expr | None = None


class ClassDef(Def):
    '''
    Tambien representara funciones,  
    '''
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym"),
        syn.Expr.from_str("$sym[..$spec]"),
        syn.Expr.from_str("$sym(..args)"),
        syn.Expr.from_str("$sym[..$spec](..args)"),
    )

    # spec son 

    sym: expr.Sym | None = None
    spec: Optional[expr.Tuple] = None
    args: Optional[expr.Tuple] = None

    def __invariants__(self):
        assert len(self.returns) == 0, "ClassDef cannot have returns"


class FnDef(Def):
    '''
    Tambien representara funciones,  
    '''
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym(..args) -> $ret"),
        syn.Expr.from_str("$sym[..$spec](..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym(..args) -> $ret"),
        syn.Expr.from_str("$ctx.$sym[..$spec](..args) -> $ret"),
    )

    # spec son 

    sym: expr.Sym | None = None
    ret: syn.Expr | None = None
    args: expr.Tuple | None = None
    spec: Optional[expr.Tuple] = None
    ctx: Optional[syn.Expr] = None

    # def __invariants__(self):
    #     assert len(self.returns) == 0, "FnDef cannot have returns"

class CastDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$from_ -> $to"), # implicit soft casting
        syn.Expr.from_str("$from_ => $to"), # explicit hard coercion
    )

    from_: syn.Expr | None = None
    to: syn.Expr | None = None


def _bounds_from_tuple(
    tup: expr.Tuple, scope: dom.Anchor | None
) -> dom.Struct[str, dom.Bound]:
    keys: list[str | None] = []
    values: list[dom.Bound] = []
    for element in tup.elements:
        match element:
            case expr.Tuple.Positional(value=value):
                if value is None:
                    raise ValueError("Tuple positional element requires a value")
                keys.append(None)
                values.append(bound_from_expr(value, scope))
            case expr.Tuple.Nominal(key=key, bound=bound, value=_):
                if bound is None:
                    raise ValueError("Tuple nominal element requires a bound")
                keys.append(slot_name_from_key(key))
                values.append(bound_from_expr(bound, scope))
            case _:
                raise ValueError(f"Unsupported tuple element: {element}")

    return dom.Struct.from_keys(tuple(keys), tuple(values))


def _bounds_from_expr(
    node: syn.Expr, scope: dom.Anchor | None
) -> dom.Struct[str, dom.Bound]:
    if isinstance(node, expr.Tuple):
        return _bounds_from_tuple(node, scope)
    return dom.Struct.from_keys((None,), (bound_from_expr(node, scope),))


def _empty_bound_struct() -> dom.Struct[str, dom.Bound]:
    return dom.Struct.from_keys((), ())


def _define_tuple_bindings(builder: Scope.Builder, tup: expr.Tuple) -> None:
    for element in tup.elements:
        match element:
            case expr.Tuple.Nominal(key=key):
                sym = sym_from_expr(key)
            case expr.Tuple.Positional(value=value):
                if value is None:
                    continue
                sym = sym_from_expr(value)
            case _:
                continue
        builder.define(sym, dom.Var.from_id(sym.name))


def _defaults_from_tuple(tup: expr.Tuple) -> tuple[int | str, ...]:
    defaults: list[int | str] = []
    for pos, element in enumerate(tup.elements):
        match element:
            case expr.Tuple.Nominal(key=key, value=value) if value is not None:
                defaults.append(slot_name_from_key(key))
    return tuple(defaults)


def _normalize_default_positions(
    shape: dom.Struct[str, dom.Bound], defaults: Iterable[int | str]
) -> tuple[int, ...]:
    positions: list[int] = []
    for default in defaults:
        if isinstance(default, int):
            positions.append(default)
        else:
            pos = shape.index.get(default, default=None)
            if pos is None:
                continue
            positions.append(pos)
    return tuple(dict.fromkeys(positions))


def _shape_without_positions(
    shape: dom.Struct[str, dom.Bound], positions: set[int]
) -> dom.Struct[str, dom.Bound]:
    keys = tuple(k for i, k in enumerate(shape.index.keys) if i not in positions)
    values = tuple(v for i, v in enumerate(shape.values) if i not in positions)
    return dom.Struct.from_keys(keys, values)


def _expand_default_shapes(
    shape: dom.Struct[str, dom.Bound], defaults: Iterable[int | str]
) -> tuple[dom.Struct[str, dom.Bound], ...]:
    positions = _normalize_default_positions(shape, defaults)
    if not positions:
        return (shape,)

    expanded: list[dom.Struct[str, dom.Bound]] = []
    positions_list = list(positions)
    for r in range(len(positions_list) + 1):
        for combo in combinations(positions_list, r):
            expanded.append(_shape_without_positions(shape, set(combo)))
    return tuple(expanded)

if __name__ == "__main__":
    from rich import print

    print(Def._match_tree())
