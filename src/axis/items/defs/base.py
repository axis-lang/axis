from __future__ import annotations

from typing import ClassVar, Literal, Optional

from protobase import flux

from axis import dom, expr, syn
from axis.log import report as log
from axis.sem import Entity, ParamVar, Scope, SpecVar, Var

from ..blocks import TupleBlock
from ..item import Item
from ..scopes import parent_scope


def _emit_diag(message: str, node: syn.Node | None) -> None:
    log.error(message).label(node).emit()


def _throw_diag(message: str, node: syn.Node | None) -> None:
    log.error(message).label(node).throw()

def _element_name(element: expr.Tuple.Element) -> str:
    match element:
        case expr.Tuple.Nominal(key=key):
            return expr.to_slot_name(key)
        case expr.Tuple.Positional(value=value):
            if value is None:
                _throw_diag("Positional element requires a value", element)
            assert value is not None
            return expr.to_name(value)
        case _:
            _throw_diag("Unsupported tuple element", element)
    raise ValueError("Unreachable")


def _inline_prefix(inline_expr: expr.Tuple) -> tuple[tuple[expr.Tuple.Element, ...], bool]:
    elements = inline_expr.elements
    spread_index: int | None = None
    for index, element in enumerate(elements):
        if element.is_spread:
            if index != len(elements) - 1:
                _throw_diag("Variadic marker must be final element", element)
            spread_index = index
            break
    if spread_index is None:
        return elements, False
    return elements[:spread_index], True


def merge_inline_block_tuple(
    inline_expr: expr.Tuple | None,
    block_expr: expr.Tuple | None,
    *,
    var_cls: type[Var],
) -> dom.Struct[str, Var]:
    if block_expr is None:
        if inline_expr is not None:
            _emit_diag("Inline tuple ignored; block required", inline_expr)
        return dom.Struct.from_keys((), ())

    if inline_expr is not None:
        prefix, variadic = _inline_prefix(inline_expr)
        if not variadic and len(block_expr.elements) != len(prefix):
            _throw_diag("Block must match inline prefix exactly", block_expr)
        if variadic and len(block_expr.elements) < len(prefix):
            _throw_diag("Block shorter than inline prefix", block_expr)
        for index, prefix_elem in enumerate(prefix):
            block_elem = block_expr.elements[index]
            if _element_name(prefix_elem) != _element_name(block_elem):
                _throw_diag("Inline prefix does not match block", block_elem)

    keys: list[str | None] = []
    values: list[Var] = []
    for element in block_expr.elements:
        match element:
            case expr.Tuple.Nominal(key=key, bound=bound, value=value):
                if bound is None:
                    _throw_diag("Tuple element requires a bound", element)
                assert bound is not None
                sym = expr.to_sym(key)
                var = var_cls(sym=sym, bound=bound, default=value)
                keys.append(expr.to_slot_name(key))
                values.append(var)
            case _:
                _throw_diag("Unsupported tuple element in block", element)

    return dom.Struct.from_keys(tuple(keys), tuple(values))


def unify_spec_where(
    inline_expr: expr.Tuple | None, block_expr: Def.Where | None
) -> dom.Struct[str, Var]:
    block_tuple = block_expr if block_expr is not None else None
    return merge_inline_block_tuple(inline_expr, block_tuple, var_cls=SpecVar)


def unify_args_takes(
    inline_expr: expr.Tuple | None, block_expr: Def.Takes | None
) -> dom.Struct[str, Var]:
    block_tuple = block_expr if block_expr is not None else None
    return merge_inline_block_tuple(inline_expr, block_tuple, var_cls=ParamVar)


class Def(Item, syn.ClassMatcher):
    class Where(TupleBlock):
        outline_keyword: ClassVar = "where"

    class Takes(TupleBlock):
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
                    expr_node, sep = None, ":"
                case (expr_node, ":"):
                    expr_node, sep = expr_node, ":"
                case _:
                    raise ValueError(f"Invalid args for {cls.__name__}: {args}")

            return super().build(kw, sep, expr=expr_node, **kwargs)

    class Returns(syn.Block):
        outline_keyword: ClassVar = "returns"
        expr: syn.Expr | None = None

        @classmethod
        def build(
            cls,
            kw: Literal["returns"],
            expr_node: syn.Expr,
            *,
            children: syn.Block.Children,
            **kwargs,
        ):
            kwargs.pop("realm", None)
            return cls(expr=expr_node, **kwargs)

    outline_keyword: ClassVar = "def"
    outline_children: ClassVar = {
        Where: False,
        Takes: False,
        Returns: False,
    }

    origin: syn.Expr | None = None
    where: Optional[Where] = None
    takes: tuple[Takes, ...] = ()
    returns: tuple[Returns, ...] = ()

    @classmethod
    def build(
        cls,
        kw: Literal["def"],
        expr_node: syn.Expr,
        *,
        children: tuple[syn.Block, ...],
        **kwargs,
    ) -> Def:
        assert (
            kw == cls.outline_keyword
        ), f"Expected keyword {cls.outline_keyword}, got {kw}"

        where: Optional[Def.Where] = None
        takes: list[Def.Takes] = []
        returns: list[Def.Returns] = []
        for child in children:
            match child:
                case cls.Where() as w:
                    where = w
                case cls.Takes() as t:
                    takes.append(t)
                case cls.Returns() as r:
                    returns.append(r)

        self = cls.match(
            expr_node,
            origin=expr_node,
            where=where,
            takes=tuple(takes),
            returns=tuple(returns),
            **kwargs,
        )
        if self is None:
            _throw_diag(
                f"Expression does not match any pattern for {cls.__name__}",
                expr_node,
            )
            raise AssertionError("Unreachable")
        return self

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        raise NotImplementedError("Def.contributions must be implemented per subclass")

    @flux.property
    def scope(self) -> Scope:
        scope_name = expr.to_name(self.origin) if self.origin is not None else None
        builder = Scope.Builder(name=scope_name, parent=parent_scope(self))
        for takes in self.takes:
            _define_tuple_bindings(builder, takes)
        if self.where is not None:
            _define_tuple_bindings(builder, self.where)
        return builder.build()


def _define_tuple_bindings(builder: Scope.Builder, tup: expr.Tuple) -> None:
    for element in tup.elements:
        match element:
            case expr.Tuple.Nominal(key=key):
                sym = expr.to_sym(key)
            case expr.Tuple.Positional(value=value):
                if value is None:
                    continue
                sym = expr.to_sym(value)
            case _:
                continue
        builder.define(sym, dom.Var.from_id(sym.name))


class CastDef(Def):
    match_patterns: ClassVar = (
        syn.Expr.from_str("$from_ -> $to"),
        syn.Expr.from_str("$from_ => $to"),
    )

    from_: syn.Expr | None = None
    to: syn.Expr | None = None

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset()
