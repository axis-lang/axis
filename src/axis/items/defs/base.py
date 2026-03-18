from __future__ import annotations

from typing import ClassVar, Literal, Optional, cast

import protomorph as pm

from protobase import _, slot_cached_property

from axis import expr, log, sem, syn


from .. import blocks
from ..item import Item


def build_binding_struct(
    inline_expr: expr.Tuple | None,
    block_expr: blocks.TupleBlock | None,
) -> sem.BindingStruct[sem.Binding]:
    """Build the binding struct described by inline and block tuple forms."""
    return expr.build_binding_struct(inline_expr, block_expr)


def build_spec_bindings(
    inline_expr: expr.Tuple | None,
    block_expr: Def.Where | None,
) -> sem.BindingStruct[sem.Binding]:
    """Build the specialization binding struct from `where` clauses."""
    return build_binding_struct(inline_expr, block_expr)


def build_param_bindings(
    inline_expr: expr.Tuple | None,
    block_expr: Def.Takes | None,
) -> sem.BindingStruct[sem.Binding]:
    """Build the parameter binding struct from `takes` clauses."""
    return build_binding_struct(inline_expr, block_expr)


def build_logic_scope(
    ctx: sem.Context,
    *,
    scope_name: str | None,
    bindings: sem.BindingStruct[sem.Binding],
    origin: syn.Node,
    include_self: bool = False,
) -> sem.Scope:
    builder = sem.Scope.Builder(name=scope_name, parent=ctx.scope)
    if include_self:
        builder.define(
            "Self",
            pm.var(
                cast(type[pm.VarType[pm.ContextProto]], sem.Context.LogicVar),
                cast(pm.ContextProto, ctx),
                "Self",
            ),
            origin=origin,
        )

    for binding in bindings:
        name = binding.binder_name
        if name is None:
            continue
        builder.define(
            name,
            pm.var(
                cast(type[pm.VarType[pm.ContextProto]], sem.Context.LogicVar),
                cast(pm.ContextProto, ctx),
                name,
            ),
            origin=binding.key,
        )

    return builder.build()


def build_extends_fact_contribution(
    ctx: sem.Context,
    *,
    scope_name: str | None,
    bindings: sem.BindingStruct[sem.Binding],
    extends: tuple[Def.Extends, ...],
    origin: syn.Node,
) -> sem.Context.FactContribution | None:
    if not extends:
        return None

    logic_scope = build_logic_scope(
        ctx,
        scope_name=scope_name,
        bindings=bindings,
        origin=origin,
        include_self=True,
    )
    fact = expr.build_extends_fact(extends[0].expr, logic_scope)
    if not isinstance(fact, pm.Spec):
        return None

    return sem.Context.FactContribution(
        anchor=fact.anchor,
        _facts=frozenset((fact,)),
        origin=extends[0],
        ctx=ctx,
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

    class Extends(syn.Block):
        outline_keyword: ClassVar = "extends"
        expr: syn.Expr = _

        @classmethod
        def build(
            cls,
            kw: Literal["extends"],
            expr_node: syn.Expr,
            *,
            children: syn.Block.Children,
            **kwargs,
        ):
            kwargs.pop("realm", None)
            _ = children
            return cls(expr=expr_node, **kwargs)

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
        Extends: False,
        Returns: False,
    }

    origin: syn.Expr = _
    where: tuple[Where, ...] = _
    takes: tuple[Takes, ...] = _
    extends: tuple[Extends, ...] = _
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
        assert kw == cls.outline_keyword, f"Expected keyword {cls.outline_keyword}, got {kw}"

        where: list[Def.Where] = []
        takes: list[Def.Takes] = []
        extends: list[Def.Extends] = []
        returns: list[Def.Returns] = []
        others: list[syn.Block] = []

        for child in children:
            match child:
                case cls.Where() as w:
                    where.append(w)
                case cls.Takes() as t:
                    takes.append(t)
                case cls.Extends() as x:
                    extends.append(x)
                case cls.Returns() as r:
                    returns.append(r)
                case _:
                    others.append(child)

        if len(extends) > 1:
            report = log.error("Def cannot declare multiple extends blocks")
            for block in extends:
                report = report.label(block)
            report.throw()

        self = cls.match(
            expr_node,
            origin=expr_node,
            where=tuple(where),
            takes=tuple(takes),
            extends=tuple(extends),
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
#         builder.define(sym, std.Var.from_id(sym.name))


class SymDef(Def, abstract=True):
    "definicion simbolica con un sym como ancla, como class o func"

    sym: expr.Sym = _

    @slot_cached_property
    def anchor(self) -> pm.Anchor:
        return self.sym.to_anchor(self.parent.anchor if self.parent else None)

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
