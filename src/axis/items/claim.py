from __future__ import annotations

from collections.abc import Iterable
from typing import Any, ClassVar, Literal, cast

import protomorph as pm
from protomorph import reasoning as urs
from protobase import _, flux, slot_cached_property

from axis import expr, log, sem, syn

from .blocks import tuple as tuple_blocks
from .item import Item
from .defs.base import build_binding_struct


type SpecResult = pm.Result[log.Report, pm.Spec]
type ConstraintTupleResult = pm.Result[log.Report]
type GoalTupleResult = pm.Result[log.Report]


class Claim(Item):
    class Where(tuple_blocks.TupleBlock):
        outline_keyword: ClassVar = "where"

    class When(syn.Block):
        outline_keyword: ClassVar = "when"

        class Clause(syn.Block):
            outline_keyword: ClassVar = "-"
            outline_keyword_sep: ClassVar = " \t"

            expr: syn.Expr = _

            @classmethod
            def build(
                cls,
                kw: Literal["-"],
                expr_node: syn.Expr,
                *,
                children: syn.Block.Children,
                **kwargs,
            ):
                kwargs.pop("package", None)
                _ = children
                return cls(expr=expr_node, **kwargs)

        outline_children: ClassVar = {Clause: True}
        clauses: tuple[Clause, ...] = ()

        @classmethod
        def build(
            cls,
            kw: Literal["when"],
            sep: Literal[":"],
            *,
            children: syn.Block.Children,
            **kwargs,
        ):
            kwargs.pop("package", None)
            assert kw == cls.outline_keyword
            assert sep == ":"
            return cls(clauses=tuple(child for child in children if isinstance(child, cls.Clause)))

    outline_keyword: ClassVar = "claim"
    outline_children: ClassVar = {
        Where: False,
        When: False,
    }

    head: syn.Expr = _
    where: tuple[Where, ...] = _
    when: tuple[When, ...] = _

    @classmethod
    def build(
        cls,
        kw: Literal["claim"],
        head: syn.Expr,
        *,
        children: syn.OutlineChildren,
        **kwargs,
    ) -> "Claim":
        assert kw == cls.outline_keyword, f"Expected keyword {cls.outline_keyword}, got {kw}"

        where = tuple(child for child in children if isinstance(child, cls.Where))
        when = tuple(child for child in children if isinstance(child, cls.When))

        if len(where) > 1:
            report = log.error("Claim cannot declare multiple where blocks")
            for block in where:
                report = report.label(block)
            report.throw()

        if len(when) > 1:
            report = log.error("Claim cannot declare multiple when blocks")
            for block in when:
                report = report.label(block)
            report.throw()

        return cls(head=head, where=where, when=when, **kwargs)

    @slot_cached_property
    def anchor(self) -> pm.Anchor:
        match self.head:
            case expr.Index(origin=origin_expr):
                return origin_expr.to_anchor(
                    self.parent.anchor if self.parent is not None else None
                )
            case _:
                return self.head.to_anchor(
                    self.parent.anchor if self.parent is not None else None
                )

    @slot_cached_property
    def name(self) -> str | None:
        return self.anchor.name

    @flux.property
    def bindings(self) -> sem.BindingStruct:
        where = self.where[0] if self.where else None
        return build_binding_struct(None, where)

    def _build_scope(self, scope_builder: sem.Scope.Builder) -> None:
        for binding in self.bindings:
            name = binding.binder_name
            if name is None:
                continue
            scope_builder.define(
                name,
                sem.Context.LogicVar(self, name),
                origin=binding.key_expr,
            )

    @flux.property
    def head_fact(self) -> SpecResult | None:
        return _build_claim_spec(self.head, self.scope, scope_ref=self.parent.anchor if self.parent else None)

    @flux.property
    def where_constraints(self) -> ConstraintTupleResult:
        return sem.binding_constraints(
            self.bindings,
            self.scope,
            subject_for_binding=self._subject_for_binding,
            origin_label="where",
        )

    @flux.property
    def body_goals(self) -> GoalTupleResult:
        implicit_constraints = self.where_constraints
        if implicit_constraints.is_err:
            return cast(GoalTupleResult, implicit_constraints)

        implicit = tuple(
            constraint.goal
            for constraint in cast(tuple[sem.Constraint, ...], implicit_constraints.unwrap().fetch())
        )

        if not self.when:
            return pm.Result.ok(_tuple_carrier(*implicit))

        goals: list[pm.Spec] = list(implicit)
        for clause in self.when[0].clauses:
            goal_result = _build_claim_spec(
                clause.expr,
                self.scope,
                scope_ref=self.parent.anchor if self.parent else None,
            )
            if goal_result is None:
                report = log.error("Claim condition must be a fact-like expression").label(clause.expr).build()
                return pm.Result.err(pm.wrap(report))
            if goal_result.is_err:
                return cast(GoalTupleResult, goal_result)
            goals.append(cast(pm.Spec, goal_result.unwrap().fetch()))
        return pm.Result.ok(_tuple_carrier(*goals))

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        head_result = self.head_fact
        if head_result is None or head_result.is_err:
            return frozenset()
        head = cast(pm.Spec, head_result.unwrap().fetch())

        body_goals_result = self.body_goals
        if body_goals_result.is_err:
            return frozenset()
        body_goals = cast(tuple[pm.Spec, ...], body_goals_result.unwrap().fetch())

        if not self.when:
            return frozenset(
                (
                    sem.Context.ClaimContribution(
                        anchor=head.anchor,
                        origin=self.head,
                        ctx=self,
                        _facts=frozenset((head,)),
                    ),
                )
            )

        return frozenset(
            (
                sem.Context.ClaimContribution(
                    anchor=head.anchor,
                    origin=self.head,
                    ctx=self,
                    _facts=frozenset(),
                    _rules=frozenset((urs.Rule(head=head, body=body_goals),)),
                ),
            )
        )

    def _subject_for_binding(self, binding: sem.BindingStruct.Field) -> sem.ScopeLookupResult | None:
        if binding.binder_name is None:
            return None
        return self.scope.lookup(expr.to_sym(binding.key_expr), origin=binding.key_expr)


def _build_claim_spec(
    expr_node: syn.Expr,
    scope: sem.Scope,
    *,
    scope_ref: pm.Anchor | None,
) -> SpecResult | None:
    return expr.build_fact(expr_node, scope, scope_ref=scope_ref)


def _tuple_carrier(*values: object) -> pm.Carrier:
    if not values:
        return pm.Tuple.Empty
    carriers = tuple(pm.wrap(value) for value in values)
    return pm.Tuple(pm.VaryingType.of(*(carrier.descriptor for carrier in carriers)), carriers)


def _logic_vars(values: Iterable[pm.Spec], claim: Claim) -> frozenset[str]:
    found: set[str] = set()
    for value in values:
        _collect_logic_vars(value, claim, found)
    return frozenset(found)


def _collect_logic_vars(value: object, claim: Claim, found: set[str]) -> None:
    if isinstance(value, pm.Var):
        if isinstance(value, sem.Context.LogicVar) and value.ctx is claim:
            found.add(value.id)
        return

    if isinstance(value, pm.Spec):
        _collect_logic_vars(value.anchor, claim, found)
        args = value.args
        if args is not None:
            for item in args.content:
                _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.Qual):
        _collect_logic_vars(value.underlying, claim, found)
        for item in value.qualifiers.content:
            _collect_logic_vars(item.fetch(), claim, found)
        return

    if isinstance(value, pm.VaryingType):
        for item in value.values:
            _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.UniformType):
        _collect_logic_vars(value.element_type, claim, found)
        return

    if isinstance(value, pm.IndexedType):
        indexed_value = cast(Any, value)
        _collect_logic_vars(indexed_value.inner, claim, found)
        for item in indexed_value.index.content:
            if item is not None:
                _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.Carrier):
        if not value.is_leaf:
            for item in value:
                _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.UnionType):
        for item in value.variants:
            _collect_logic_vars(item, claim, found)
