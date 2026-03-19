from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar, Literal, cast

import protomorph as pm
from protobase import _, flux, slot_cached_property

from axis import expr, log, sem, syn

from .blocks import tuple as tuple_blocks
from .item import Item
from .defs.base import build_binding_struct


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
                kwargs.pop("realm", None)
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
            kwargs.pop("realm", None)
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
                pm.var(
                    cast(type[pm.VarType[pm.ContextProto]], sem.Context.LogicVar),
                    cast(pm.ContextProto, self),
                    name,
                ),
                origin=binding.key_expr,
            )

    @flux.property
    def head_fact(self) -> pm.Spec | pm.Err | None:
        return _build_claim_spec(self.head, self.scope)

    @flux.property
    def body_goals(self) -> tuple[pm.Spec, ...] | pm.Err:
        implicit = sem.binding_constraint_goals(
            self.bindings,
            self.scope,
            subject_for_binding=lambda binding: self.scope.lookup(expr.to_sym(binding.key_expr), origin=binding.key_expr)
            if binding.binder_name is not None
            else None,
            origin_label="where",
        )
        if isinstance(implicit, pm.Err):
            return implicit

        if not self.when:
            return implicit

        goals: list[pm.Spec] = list(implicit)
        for clause in self.when[0].clauses:
            goal = _build_claim_spec(clause.expr, self.scope)
            if not isinstance(goal, pm.Spec):
                return pm.Err() if goal is None else goal
            goals.append(goal)
        return tuple(goals)

    @flux.property
    def contributions(self) -> frozenset[sem.Context.Contribution]:
        head = self.head_fact
        if not isinstance(head, pm.Spec):
            return frozenset()

        body_goals = self.body_goals
        if isinstance(body_goals, pm.Err):
            return frozenset()

        if not body_goals:
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
                    _clauses=frozenset((pm.Clause(head=head, body=body_goals),)),
                ),
            )
        )

    @flux.method
    def check(self):
        self.scope

        head = self.head_fact
        _raise_claim_error(head, origin=self.head, message="Invalid claim head")
        assert isinstance(head, pm.Spec)

        entity = self.realm.entities_by_anchor[head.anchor] if head.anchor in self.realm.entities_by_anchor else None
        if entity is None or not entity.spec_index.facet(sem.Entity.PredicateFacet):
            log.error("Claim target must have predicate facet").label(self.head).throw()

        body_goals = self.body_goals
        _raise_claim_error(body_goals, origin=self.when[0] if self.when else self.head, message="Invalid claim condition")
        assert not isinstance(body_goals, pm.Err)

        if not entity.exists_spec(head, sem.Entity.PredicateFacet):
            log.error("Claim head is not admitted by any declared predicate spec").label(self.head).throw()

        if not body_goals:
            return

        head_vars = _logic_vars((head,), self)
        body_vars = _logic_vars(body_goals, self)
        unsafe = tuple(sorted(var for var in head_vars if var not in body_vars))
        if not unsafe:
            return

        names = ", ".join(unsafe)
        report = log.error("Conditional claim must be range-restricted")
        report = report.label(self.head, f"head variables must appear in when: {names}")
        for clause in self.when[0].clauses:
            report = report.label(clause, "when body grounds claim variables")
        report.throw()


def _build_claim_spec(expr_node: syn.Expr, scope: sem.Scope) -> pm.Spec | pm.Err | None:
    try:
        return expr.build_fact(expr_node, scope)
    except log.Report.Exception as exc:
        return exc.report.tag(pm.Err())
    except TypeError as exc:
        return log.error("Unsupported claim expression").label(expr_node, str(exc)).tag(pm.Err())


def _raise_claim_error(
    value: tuple[pm.Spec, ...] | pm.Spec | pm.Err | None,
    *,
    origin: syn.Node,
    message: str,
) -> None:
    err = value if isinstance(value, pm.Err) else None
    if err is None:
        return

    report = log.Report.of(err)
    if report is not None:
        if report.message.startswith("Unbound symbol: "):
            symbol = report.message.removeprefix("Unbound symbol: ")
            wrapped = log.error("Claim references an unresolved symbol").label(
                origin,
                f"declare `{symbol}` in where: or bring it into scope",
            )
            for label in report.labels:
                wrapped = wrapped.label(label.ast, label.message, style=label.style)
            wrapped.note(report.message).throw()
        report.throw()
    log.error(message).label(origin).throw()


def _logic_vars(values: Iterable[pm.Spec], claim: Claim) -> frozenset[str]:
    found: set[str] = set()
    for value in values:
        _collect_logic_vars(value, claim, found)
    return frozenset(found)


def _collect_logic_vars(value: object, claim: Claim, found: set[str]) -> None:
    if isinstance(value, pm.Var):
        if isinstance(value.__type__, sem.Context.LogicVar) and value.__type__.ctx is claim:
            if isinstance(value.__data__, str):
                found.add(value.__data__)
        return

    if isinstance(value, pm.Spec):
        _collect_logic_vars(value.anchor, claim, found)
        args = value.args
        if args is not None:
            for item in args.values:
                _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.Const):
        attrs = value.attrs
        if attrs is not None:
            for item in attrs.values:
                _collect_logic_vars(item, claim, found)
            return
        if isinstance(value.__data__, pm.Type):
            _collect_logic_vars(value.__data__, claim, found)
        return

    if isinstance(value, pm.NominalQualifier):
        _collect_logic_vars(value.spec_ref, claim, found)
        _collect_logic_vars(value.underlying, claim, found)
        return

    if isinstance(value, pm.NominalType):
        _collect_logic_vars(value.spec_ref, claim, found)
        return

    if isinstance(value, pm.StructType):
        for item in value.meta_attrs.values:
            _collect_logic_vars(item, claim, found)
        return

    if isinstance(value, pm.UnionType):
        for item in value.types:
            _collect_logic_vars(item, claim, found)
