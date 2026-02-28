from __future__ import annotations
from itertools import combinations
from typing import ClassVar, Iterable, Literal, Optional

from protobase import flux

from axis import dom, syn, expr
from axis.sem import Database
from .blocks import TupleBlock


from .item import Item
from .ref import ref_from_expr, scope_ref_from_item, slot_name_from_key


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
    origin: syn.Expr
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
        if self is not None:
            return self

        return cls(
            expr=expr, **kwargs, where=where, takes=tuple(takes), returns=tuple(returns)
        )

    @flux.property
    def contributions(self) -> frozenset[Database.Contribution]:
        if self.origin is None:
            return frozenset()

        scope_ref = scope_ref_from_item(self)
        owner = ref_from_expr(self.origin, scope_ref)
        contributions: list[Database.Contribution] = []

        where_expr = self.where
        if self.takes:
            for takes in self.takes:
                takes_expr = takes.expr
                if takes_expr is None:
                    continue

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

                for takes_candidate in takes_shapes:
                    for where_candidate in where_shapes:
                        contributions.append(
                            Database.Overload(
                                anchor=owner,
                                takes_shape=takes_candidate,
                                where_shape=where_candidate,
                                origin=takes_expr,
                                ctx=self,
                            )
                        )

                        if self.returns:
                            for ret in self.returns:
                                if ret.expr is None:
                                    continue
                                contributions.append(
                                    Database.Returns(
                                        anchor=owner,
                                        takes_shape=takes_candidate,
                                        where_shape=where_candidate,
                                        returns_shape=_shape_from_expr(ret.expr),
                                        origin=ret.expr,
                                        ctx=self,
                                    )
                                )
        elif self.returns:
            where_shape = _shape_from_expr(where_expr) if where_expr else None
            where_defaults = (
                _defaults_from_tuple(where_expr)
                if isinstance(where_expr, expr.Tuple)
                else ()
            )
            where_shapes = (
                _expand_default_shapes(where_shape, where_defaults)
                if where_shape
                else (None,)
            )

            for where_candidate in where_shapes:
                for ret in self.returns:
                    if ret.expr is None:
                        continue
                    contributions.append(
                        Database.Returns(
                            anchor=owner,
                            takes_shape=None,
                            where_shape=where_candidate,
                            returns_shape=_shape_from_expr(ret.expr),
                            origin=ret.expr,
                            ctx=self,
                        )
                    )

        if self.where is not None:
            for elem in self.where.elements:
                contributions.append(
                    Database.Constraint(
                        anchor=owner,
                        predicate=elem,
                        origin=elem,
                        ctx=self,
                    )
                )

        return frozenset(contributions)

    # def ingest(self, ingestor: Ingestor):
    #     ...

    # class Kind(syn.ClassMatcher, abstract=True): ...

    # class InfixKind(Kind):
    #     """
    #     def a + b
    #     takes:
    #         val a: T
    #         val b: T
    #     where:
    #         val T: Numeric
    #     """

    #     op: expr.Infix.Op
    #     lhs: expr.Sym
    #     rhs: expr.Sym

    # class PrefixKind(Kind):
    #     """
    #     def -a
    #     takes:
    #         val a: T
    #     where:
    #         val T: Numeric
    #     """

    #     op: expr.Prefix.Op
    #     rhs: expr.Sym

    # class QualKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym $qualified@Sym"),
    #         syn.Expr.from_str("$sym@Sym[..$generics] $qualified@Sym"),
    #     )

    #     qualified: expr.Sym
    #     generics: Optional[expr.Tuple] = None

    # class ClassKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym"),
    #         syn.Expr.from_str("$sym@Sym[..$generics]"),
    #     )

    #     generics: Optional[expr.Tuple] = None

    # class FunctionKind(Kind):
    #     match_patterns: ClassVar[tuple[syn.Expr, ...]] = (
    #         syn.Expr.from_str("$sym@Sym(..$params)"),
    #         syn.Expr.from_str("$sym@Sym[..$generics](..$params)"),
    #         syn.Expr.from_str("$context.$sym(..$params)"),
    #         syn.Expr.from_str("$context.$sym[..$generics](..$params)"),
    #     )

    #     params: Optional[expr.Tuple] = None
    #     context: Optional[syn.Expr] = None

    # @cached_property
    # def kind(self):
    #     match self.expr:
    #         case expr.Sym(at=at) as sym:
    #             return self.ClassKind(sym=sym)
    #         case expr.Index(origin=expr.Sym() as sym, index=expr.Tuple() as generics):
    #             return self.ClassKind(sym=sym, generics=generics)
    #         case expr.Infix(op=op) as infix:
    #             ...
    #         case expr.Prefix(op=op) as prefix:
    #             ...
    #         case expr.Apply(function=function, argument=arguments):
    #             ...

    #     kind = self.Kind.match(self.expr)
    #     if kind is None:

    #         with log.error(
    #             f"Definition expression does not match any known kind: {self.expr}"
    #         ) as err:
    #             err.with_label(self.as_label("Unknown def kind"))

    #         raise ValueError(f"Invalid definition expression: {self.expr}")
    #     return kind


class QualDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$sym $target"),
        syn.Expr.from_str("$sym[..$spec] $target"),
    )

    sym: expr.Sym
    # target y spec son parametros (takes)
    spec: Optional[expr.Tuple] = None
    target: syn.Expr


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

    sym: expr.Sym
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

    sym: expr.Sym
    ret: syn.Expr
    args: expr.Tuple
    spec: Optional[expr.Tuple] = None
    ctx: Optional[syn.Expr] = None

    # def __invariants__(self):
    #     assert len(self.returns) == 0, "FnDef cannot have returns"

class CastDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$from_ -> $to"), # implicit soft casting
        syn.Expr.from_str("$from_ => $to"), # explicit hard coercion
    )

    from_: syn.Expr
    to: syn.Expr


def _shape_from_tuple(tup: expr.Tuple) -> dom.Tuple[str, syn.Expr]:
    keys: list[str | None] = []
    values: list[syn.Expr] = []
    for element in tup.elements:
        match element:
            case expr.Tuple.Positional(value=value):
                if value is None:
                    raise ValueError("Tuple positional element requires a value")
                keys.append(None)
                values.append(value)
            case expr.Tuple.Nominal(key=key, bound=bound, value=_):
                if bound is None:
                    raise ValueError("Tuple nominal element requires a bound")
                keys.append(slot_name_from_key(key))
                values.append(bound)
            case _:
                raise ValueError(f"Unsupported tuple element: {element}")

    return dom.Tuple.from_keys(tuple(keys), tuple(values))


def _shape_from_expr(node: syn.Expr) -> dom.Tuple[str, syn.Expr]:
    if isinstance(node, expr.Tuple):
        return _shape_from_tuple(node)
    return dom.Tuple.from_keys((None,), (node,))


def _defaults_from_tuple(tup: expr.Tuple) -> tuple[int | str, ...]:
    defaults: list[int | str] = []
    for pos, element in enumerate(tup.elements):
        match element:
            case expr.Tuple.Nominal(key=key, value=value) if value is not None:
                defaults.append(slot_name_from_key(key))
    return tuple(defaults)


def _normalize_default_positions(
    shape: dom.Tuple[str, syn.Expr], defaults: Iterable[int | str]
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
    shape: dom.Tuple[str, syn.Expr], positions: set[int]
) -> dom.Tuple[str, syn.Expr]:
    keys = tuple(k for i, k in enumerate(shape.index.keys) if i not in positions)
    values = tuple(v for i, v in enumerate(shape.values) if i not in positions)
    return dom.Tuple.from_keys(keys, values)


def _expand_default_shapes(
    shape: dom.Tuple[str, syn.Expr], defaults: Iterable[int | str]
) -> tuple[dom.Tuple[str, syn.Expr], ...]:
    positions = _normalize_default_positions(shape, defaults)
    if not positions:
        return (shape,)

    expanded: list[dom.Tuple[str, syn.Expr]] = []
    positions_list = list(positions)
    for r in range(len(positions_list) + 1):
        for combo in combinations(positions_list, r):
            expanded.append(_shape_without_positions(shape, set(combo)))
    return tuple(expanded)

if __name__ == "__main__":
    from rich import print

    print(Def._match_tree())
