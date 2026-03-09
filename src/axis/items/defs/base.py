from __future__ import annotations

from typing import ClassVar, Literal, Optional

from protobase import flux, _, slot_cached_property


from axis import dom, expr, syn, sem, log

from .. import blocks
from ..item import Item


def merge_inline_block_tuple[B: sem.Context.Binding](
    inline_expr: expr.Tuple | None,
    block_expr: blocks.TupleBlock | None,
    *,
    binding_cls: type[B],
) -> dom.Struct[str, B]:
    """Merge inline and block tuples into binding structs, enforcing prefix rules."""
    if block_expr is None:
        if inline_expr is not None:
            log.error("Inline tuple ignored; block required").label(inline_expr).emit()
        return dom.Struct.Empty

    # if inline_expr is not None:
    #     prefix, variadic = inline_expr.inline_prefix
    #     if not variadic and len(block_expr.elements) != len(prefix):
    #         log.error("Block must match inline prefix exactly").label(
    #             block_expr
    #         ).throw()
    #     if variadic and len(block_expr.elements) < len(prefix):
    #         log.error("Block shorter than inline prefix").label(block_expr).throw()
    #     for index, prefix_elem in enumerate(prefix):
    #         block_elem = block_expr.elements[index]
    #         if prefix_elem.name != block_elem.name:
    #             log.error("Inline prefix does not match block").label(
    #                 block_elem
    #             ).throw()

    entries: list[tuple[str | None, B]] = []

    for element in block_expr.elements:
        match element:
            case expr.Tuple.Nominal(key=key, bound=bound, value=value):
                # if bound is None:
                #     log.error("Tuple element requires a bound").label(element).throw()
                # assert bound is not None
                sym = expr.to_sym(key)

                var = binding_cls(key=key, bound=bound, default=value)
                entries.append((expr.to_slot_name(key), var))
            case _:
                log.error("Unsupported tuple element in block").label(element).throw()

    return dom.Struct.from_iter(entries)


def unify_spec_where(
    inline_expr: expr.Tuple | None, block_expr: Def.Where | None
) -> dom.Struct[str, sem.Entity.SpecContribution.SpecBinding]:
    """Resolve where blocks into a spec struct, combining inline+block forms."""
    block_tuple = block_expr if block_expr is not None else None
    return merge_inline_block_tuple(
        inline_expr,
        block_tuple,
        binding_cls=sem.Entity.SpecContribution.SpecBinding,
    )


def unify_args_takes(
    inline_expr: expr.Tuple | None, block_expr: Def.Takes | None
) -> dom.Struct[str, sem.Entity.OverloadContribution.ParamBinding]:
    """Resolve takes blocks into a params struct, combining inline+block forms."""
    block_tuple = block_expr if block_expr is not None else None
    return merge_inline_block_tuple(
        inline_expr,
        block_tuple,
        binding_cls=sem.Entity.OverloadContribution.ParamBinding,
    )


class Def(Item, syn.ClassMatcher):

    class Members(syn.Block):
        outline_keyword: ClassVar = "members"


    class Where(blocks.TupleBlock):
        outline_keyword: ClassVar = "where"

    class Takes(blocks.TupleBlock):
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

    origin: syn.Expr = _
    where: tuple[Where, ...] = _
    takes: tuple[Takes, ...] = _
    returns: tuple[Returns, ...] = _
    other_blocks: tuple[syn.Block, ...] = _

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

        where: list[Def.Where] = []
        takes: list[Def.Takes] = []
        returns: list[Def.Returns] = []
        others: list[syn.Block] = []

        for child in children:
            match child:
                case cls.Where() as w:
                    where.append(w)
                case cls.Takes() as t:
                    takes.append(t)
                case cls.Returns() as r:
                    returns.append(r)
                case _:
                    others.append(child)

        self = cls.match(
            expr_node,
            origin=expr_node,
            where=tuple(where),
            takes=tuple(takes),
            returns=tuple(returns),
            other_blocks=tuple(others),
            **kwargs,
        )

        if self is None:
            (
                log.error(f"Expression does not match any pattern for {cls.__name__}")
                .label(expr_node)
                .throw()
            )

        return self

    # @flux.property
    # def contributions(self) -> frozenset[sem.Context.Contribution]:
    #     raise NotImplementedError("Def.contributions must be implemented per subclass")

    # @flux.property
    # def scope(self) -> Scope:
    #     scope_name = expr.to_name(self.origin) if self.origin is not None else None
    #     builder = Scope.Builder(name=scope_name, parent=parent_scope(self))
    #     for takes in self.takes:
    #         _define_tuple_bindings(builder, takes)
    #     if self.where is not None:
    #         _define_tuple_bindings(builder, self.where)
    #     return builder.build()


# def _define_tuple_bindings(builder: Scope.Builder, tup: expr.Tuple) -> None:
#     for element in tup.elements:
#         match element:
#             case expr.Tuple.Nominal(key=key):
#                 sym = expr.as_sym(key)
#             case expr.Tuple.Positional(value=value):
#                 if value is None:
#                     continue
#                 sym = expr.as_sym(value)
#             case _:
#                 continue
#         builder.define(sym, dom.Var.from_id(sym.name))


class SymDef(Def, abstract=True):
    "definicion simbolica con un sym como ancla, como class o func"

    sym: expr.Sym = _

    @slot_cached_property
    def anchor(self) -> dom.Anchor:
        return expr.as_anchor(self.sym, self.parent.anchor if self.parent else None)

    @slot_cached_property
    def name(self) -> str | None:
        return self.anchor.name


# class CastDef(Def):
#     match_patterns: ClassVar = (
#         syn.Expr.from_str("$from_ -> $to"),
#         syn.Expr.from_str("$from_ => $to"),
#     )

#     from_: syn.Expr | None = None
#     to: syn.Expr | None = None

#     @flux.property
#     def contributions(self) -> frozenset[Entity.Contribution]:
#         return frozenset()
