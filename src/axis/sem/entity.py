from __future__ import annotations

from collections.abc import Callable
from typing import cast

from protobase import Consed, flux, _, frozendict

import protomorph as pm
from protomorph import reasoning as urs

from axis import log, sem, syn


class Facet(Consed, abstract=True):
    pass


class ContributionSet(pm.Builtin, abstract=True):
    anchor: pm.Anchor
    contributions: frozenset[sem.Context.Contribution]

    @flux.property
    def facts(self) -> frozenset[pm.Spec]:
        return frozenset(fact for contrib in self.contributions for fact in contrib.facts)

    @flux.property
    def rules(self) -> frozenset[urs.Rule]:
        return frozenset(rule for contrib in self.contributions for rule in contrib.rules)


class EntityView(ContributionSet):
    class SpecContribution(sem.Context.EntityContribution, abstract=True):
        spec_bindings: sem.BindingStruct = _

        def _spec_binder(self, field: sem.BindingStruct.Field) -> pm.Var | None:
            name = field.binder_name
            if name is None:
                return None
            return Entity.SpecVar(self, name)

        @flux.property
        def spec_scope(self) -> sem.Scope:
            builder = sem.Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            builder.define("Self", Entity.SpecVar(self, "Self"), origin=self.origin)
            for binding in self.spec_bindings.nameable_fields:
                name = binding.binder_name
                if name is None:
                    continue
                binder = self._spec_binder(binding)
                assert binder is not None
                builder.define(name, cast(pm.Var, binder), origin=binding.key_expr)
            return builder.build()

        @flux.property
        def lowered_spec_bindings(self) -> sem.LoweredBindingStruct:
            return sem.lower_binding_struct(
                self.spec_bindings,
                self.spec_scope,
                binder_for=self._spec_binder,
            )

        @flux.property
        def spec_binding_ir(self) -> sem.BindingIR:
            return sem.build_binding_ir(self.lowered_spec_bindings)

        def _spec_subject_template(self, field: sem.BindingStruct.Field) -> pm.Val | None:
            if field.binder_name is None:
                return None
            if field.is_nominal and field.slot_key is not None:
                return pm.val(urs.AttrOperator.of(pm.SELF, field.slot_key))
            positional = [item for item in self.spec_bindings.fields if item.is_positional]
            try:
                offset = positional.index(field)
            except ValueError:
                return None
            return pm.val(urs.AttrOperator.of(pm.SELF, offset))

        @flux.property
        def spec_constraint_scope(self) -> sem.Scope:
            builder = sem.Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            builder.define("Self", pm.SELF, origin=self.origin)
            for binding in self.spec_bindings.nameable_fields:
                name = binding.binder_name
                template = self._spec_subject_template(binding)
                if name is None or template is None:
                    continue
                builder.define(name, cast(pm.Datum, template.fetch()), origin=binding.key_expr)
            return builder.build()

        @flux.property
        def spec_constraint_templates(self) -> pm.Result[log.Report]:
            return sem.binding_constraints(
                self.spec_bindings,
                self.spec_constraint_scope,
                subject_for_binding=lambda field: (
                    None
                    if self._spec_subject_template(field) is None
                    else pm.Result.ok(cast(pm.Val, self._spec_subject_template(field)))
                ),
                origin_label="spec",
                allow_defaults=True,
            )

        @flux.property
        def spec_constraint_goal_templates(self) -> pm.Result[log.Report]:
            return sem.binding_constraint_goals(
                self.spec_bindings,
                self.spec_constraint_scope,
                subject_for_binding=lambda field: (
                    None
                    if self._spec_subject_template(field) is None
                    else pm.Result.ok(cast(pm.Val, self._spec_subject_template(field)))
                ),
                origin_label="spec",
                allow_defaults=True,
            )

        @flux.property
        def status(self) -> sem.Status:
            return sem.Status(children=(), reports=_reports_for(self._check))

        def _check(self) -> None:
            self.spec_scope
            self.lowered_spec_bindings
            self.spec_binding_ir
            self.spec_constraint_scope
            self.spec_constraint_templates
            self.spec_constraint_goal_templates

    class SpecVar(pm.SimpleVar):
        ctx: "EntityView.SpecContribution"
        id: str

    class FactFacet(SpecContribution, Facet):
        pass

    class OverloadContribution(SpecContribution, abstract=True):
        param_bindings: sem.BindingStruct = _

        def _param_binder(self, field: sem.BindingStruct.Field) -> pm.Var | None:
            name = field.binder_name
            if name is None:
                return None
            return Entity.ParamVar(self, name)

        @flux.property
        def overload_scope(self) -> sem.Scope:
            builder = sem.Scope.Builder(name=self.anchor.name, parent=self.spec_scope)
            builder.define("self", Entity.ParamVar(self, "self"), origin=self.origin)
            for binding in self.param_bindings.nameable_fields:
                name = binding.binder_name
                if name is None:
                    continue
                binder = self._param_binder(binding)
                assert binder is not None
                builder.define(name, cast(pm.Var, binder), origin=binding.key_expr)
            return builder.build()

        @flux.property
        def lowered_param_bindings(self) -> sem.LoweredBindingStruct:
            return sem.lower_binding_struct(
                self.param_bindings,
                self.overload_scope,
                binder_for=self._param_binder,
            )

        @flux.property
        def param_constraints(self) -> pm.Result[log.Report]:
            return sem.binding_constraints(
                self.param_bindings,
                self.overload_scope,
                subject_for_binding=lambda field: (
                    None
                    if self._param_binder(field) is None
                    else pm.Result.ok(pm.val(cast(pm.Var, self._param_binder(field))))
                ),
                origin_label="parameter",
                allow_defaults=True,
            )

        @flux.property
        def status(self) -> sem.Status:
            return sem.Status(children=(), reports=_reports_for(self._check))

        def _check(self) -> None:
            self.overload_scope
            self.lowered_spec_bindings
            self.lowered_param_bindings
            self.param_constraints

    class ParamVar(pm.SimpleVar):
        ctx: "EntityView.OverloadContribution"
        id: str

    class ClassFacet(OverloadContribution, Facet):
        pass

    class ResultContribution(OverloadContribution, abstract=True):
        result_bound_expr: syn.Expr | None = _

        @flux.property
        def result_bound(self) -> pm.Val | None:
            return sem.build_bound(self.result_bound_expr, self.overload_scope)

        @flux.property
        def result_constraint(self) -> pm.Constraint | None:
            bound = self.result_bound
            return None if bound is None else sem.constraint_from_term(Entity.ParamVar(self, "self"), bound)

        def __invariant__(self):
            if self.result_bound_expr is None:
                log.warn("ResultContribution without returns").label(self.origin).emit()

    class FunctionFacet(ResultContribution, Facet):
        pass

    class QualifierContribution(SpecContribution):
        underlying_bound_expr: syn.Expr = _
        param_bindings: sem.BindingStruct = _

        @flux.property
        def lowered_param_bindings(self) -> sem.LoweredBindingStruct:
            return sem.lower_binding_struct(
                self.param_bindings,
                self.spec_scope,
                binder_for=self._spec_binder,
            )

        @flux.property
        def underlying_bound(self) -> pm.Val | None:
            return sem.build_bound(self.underlying_bound_expr, self.spec_scope)

        @flux.property
        def underlying_constraint(self) -> pm.Constraint | None:
            bound = self.underlying_bound
            return None if bound is None else sem.constraint_from_term(Entity.ParamVar(self, "self"), bound)

        @flux.property
        def status(self) -> sem.Status:
            return sem.Status(children=(), reports=_reports_for(self._check))

        def _check(self) -> None:
            self.spec_scope
            self.lowered_spec_bindings
            self.lowered_param_bindings
            self.underlying_bound
            self.underlying_constraint

    @flux.method
    def for_(
        self,
        *,
        facet: type[sem.Context.Contribution] | None = None,
        where: Callable[[sem.Context.Contribution], bool] | None = None,
    ) -> "EntityView":
        filtered = frozenset(
            contrib
            for contrib in self.contributions
            if (facet is None or isinstance(contrib, facet)) and (where is None or where(contrib))
        )
        if not filtered:
            raise ValueError(f"EntityView for {self.anchor!r} cannot be empty")
        return EntityView(anchor=self.anchor, contributions=filtered)

    @flux.method
    def facet(self, cls: type[sem.Context.Contribution]) -> "EntityView":
        return self.for_(facet=cls)

    @flux.property
    def spec_contributions(self) -> tuple[SpecContribution, ...]:
        return tuple(
            contrib
            for contrib in self.contributions
            if isinstance(contrib, EntityView.SpecContribution)
        )

    @flux.property
    def _clusterable_spec_contributions(self) -> tuple[SpecContribution, ...]:
        return tuple(
            contrib
            for contrib in self.contributions
            if isinstance(contrib, EntityView.FactFacet) and contrib.status.is_ok
        )

    @flux.property
    def _status_contributions(self) -> tuple[sem.Context.Contribution, ...]:
        return tuple(
            contrib
            for contrib in self.contributions
            if isinstance(contrib, (EntityView.FactFacet, sem.Context.ClaimContribution))
        )

    @flux.property
    def _spec_match_cases(self) -> tuple[pm.MatchCase[SpecContribution], ...]:
        cases: list[pm.MatchCase[EntityView.SpecContribution]] = []
        for index, contrib in enumerate(self._clusterable_spec_contributions):
            summary = contrib.spec_binding_ir.admission
            cases.append(
                pm.MatchCase(
                    id=index,
                    summary=pm.MatchCaseSummary(
                        pattern=summary.pattern,
                        shape=summary.shape,
                        prefix_descriptors=summary.prefix_descriptors,
                        suffix_descriptors=summary.suffix_descriptors,
                        required_nominal_descriptors=summary.required_nominal_descriptors,
                        origin=contrib,
                    ),
                    payloads=frozenset((contrib,)),
                )
            )
        return tuple(cases)

    @flux.property
    def _spec_match_tree(self) -> pm.Val:
        cases = self._spec_match_cases
        if not cases:
            raise ValueError(f"EntityView for {self.anchor!r} has no spec contributions")
        return pm.compile({case.summary: case.payloads for case in cases})

    @flux.property
    def _spec_buckets(self) -> tuple[pm.MatchBucket, ...]:
        tree = cast(pm.MatchTree[EntityView.SpecContribution], self._spec_match_tree.fetch())
        return tree.buckets

    @flux.property
    def spec_clusters(self) -> tuple[sem.SpecCluster, ...]:
        if not self._clusterable_spec_contributions:
            return ()
        tree = cast(pm.MatchTree[EntityView.SpecContribution], self._spec_match_tree.fetch())
        cases_by_id = {case.id: case for case in tree.cases}
        clusters: list[sem.SpecCluster] = []
        for bucket in tree.buckets:
            contributions: list[EntityView.SpecContribution] = []
            templates_by_contribution: dict[EntityView.SpecContribution, tuple[pm.Constraint, ...]] = {}
            for case_id in sorted(bucket.case_ids):
                case = cases_by_id[case_id]
                origin = case.summary.origin
                if not isinstance(origin, EntityView.SpecContribution):
                    continue
                contributions.append(origin)
                templates_result = origin.spec_constraint_templates
                if not templates_result.is_err:
                    templates_by_contribution[origin] = cast(
                        tuple[pm.Constraint, ...],
                        templates_result.unwrap().fetch(),
                    )
            clusters.append(
                sem.SpecCluster(
                    anchor=self.anchor,
                    contributions=frozenset(contributions),
                    bucket=bucket,
                    templates_by_contribution=frozendict(templates_by_contribution),
                )
            )
        return tuple(clusters)

    @flux.method
    def spec_pattern_for(self, cls: type[SpecContribution]) -> pm.Val | None:
        try:
            return self.for_(facet=cls)._spec_match_tree
        except ValueError:
            return None

    def dispatch(self, spec: pm.Spec) -> SpecContribution:
        tree = cast(pm.MatchTree[EntityView.SpecContribution], self._spec_match_tree.fetch())
        subject = spec.args or pm.Tuple.Empty
        match_result = self._spec_match_tree.match(subject)
        if match_result is None or not match_result.solutions:
            raise ValueError(f"Spec {spec!r} is not admitted by {self.anchor!r}")

        structural: list[EntityView.SpecContribution] = []
        seen: set[EntityView.SpecContribution] = set()
        for solution in match_result.solutions:
            for payload in solution.payloads:
                if payload not in seen:
                    seen.add(payload)
                    structural.append(payload)

        if not structural:
            raise ValueError(f"Spec {spec!r} has no structural candidates in {self.anchor!r}")

        realm = cast(sem.Realm, pm.current_realm())
        session = realm.logic_solver.session()

        viable: list[EntityView.SpecContribution] = []
        for contrib in structural:
            templates_result = contrib.spec_constraint_templates
            if templates_result.is_err:
                continue
            templates = cast(tuple[pm.Constraint, ...], templates_result.unwrap().fetch())
            if _constraints_hold(templates, spec, session):
                viable.append(contrib)

        if len(viable) == 1:
            return viable[0]
        if not viable:
            raise ValueError(f"Spec {spec!r} is not admitted by constraints in {self.anchor!r}")
        raise ValueError(f"Spec {spec!r} is ambiguous in {self.anchor!r}: {viable!r}")

    @flux.property
    def status(self) -> sem.Status:
        return sem.Status(
            children=(
                *(contrib.status for contrib in self._status_contributions),
                *(cluster.status for cluster in self.spec_clusters),
            )
        )


class Entity(EntityView):
    pass


def _reports_for(check: Callable[[], None]) -> tuple[log.Report, ...]:
    try:
        check()
    except log.Report.Exception as raised:
        return (raised.report,)
    return ()


def _constraints_hold(
    templates: tuple[pm.Constraint, ...],
    spec: pm.Spec,
    session: urs.Session,
) -> bool:
    from protomorph.reasoning.core import _builtin_relation_answer
    from protomorph import reasoning as urs_mod

    for template in templates:
        goal = template.goal_for(spec)
        if _builtin_relation_answer(goal) is not None:
            continue
        outcome = session.solve(goal)
        if not isinstance(outcome, urs_mod.Unique):
            return False
    return True


for _cls in (
    Entity.FactFacet,
    Entity.ClassFacet,
    Entity.FunctionFacet,
    Entity.QualifierContribution,
):
    _cls.__class_check__()
