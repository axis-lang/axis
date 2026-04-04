from __future__ import annotations

from typing import cast

from protobase import Consed, flux, _

import protomorph as pm
from protomorph import reasoning as urs

from axis import log, sem, syn


class Facet(Consed, abstract=True):
    pass


class Entity(Consed):
    anchor: pm.Anchor
    contributions: frozenset[sem.Context.Contribution]

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

        def _check(self) -> None:
            self.spec_scope
            self.lowered_spec_bindings
            self.spec_binding_ir

    class SpecVar(pm.SimpleVar):
        ctx: "Entity.SpecContribution"
        id: str

    class FactFacet(Facet, SpecContribution):
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
                    else pm.Result.ok(pm.wrap(cast(pm.Var, self._param_binder(field))))
                ),
                origin_label="parameter",
                allow_defaults=True,
            )

        def _check(self) -> None:
            self.overload_scope
            self.lowered_spec_bindings
            self.lowered_param_bindings
            self.param_constraints

    class ParamVar(pm.SimpleVar):
        ctx: "Entity.OverloadContribution"
        id: str

    class ClassFacet(Facet, OverloadContribution):
        pass

    class ResultContribution(OverloadContribution, abstract=True):
        result_bound_expr: syn.Expr | None = _

        @flux.property
        def result_bound(self) -> pm.Val | None:
            return sem.build_bound(self.result_bound_expr, self.overload_scope)

        @flux.property
        def result_constraint(self) -> sem.Constraint | None:
            bound = self.result_bound
            return None if bound is None else sem.constraint_from_term(Entity.ParamVar(self, "self"), bound)

        def __invariant__(self):
            if self.result_bound_expr is None:
                log.warn("ResultContribution without returns").label(self.origin).emit()

    class FunctionFacet(Facet, ResultContribution):
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
        def underlying_constraint(self) -> sem.Constraint | None:
            bound = self.underlying_bound
            return None if bound is None else sem.constraint_from_term(Entity.ParamVar(self, "self"), bound)

        def _check(self) -> None:
            self.spec_scope
            self.lowered_spec_bindings
            self.lowered_param_bindings
            self.underlying_bound
            self.underlying_constraint

    @flux.method
    def facet(self, cls: type[sem.Context.Contribution]) -> frozenset[sem.Context.Contribution]:
        if not issubclass(cls, sem.Context.Contribution):
            raise TypeError(f"Expected Contribution subtype, got {cls!r}")
        return frozenset(contrib for contrib in self.contributions if isinstance(contrib, cls))

    @flux.property
    def facts(self) -> frozenset[pm.Spec]:
        return frozenset(fact for contrib in self.contributions for fact in contrib.facts)

    @flux.property
    def rules(self) -> frozenset[urs.Rule]:
        return frozenset(rule for contrib in self.contributions for rule in contrib.rules)

    @flux.property
    def spec_pattern(self) -> pm.Carrier | None:
        specs = tuple(
            contrib for contrib in self.contributions if isinstance(contrib, Entity.SpecContribution)
        )
        if not specs:
            return None
        return pm.compile(
            {contrib.spec_binding_ir.admission: frozenset((contrib,)) for contrib in specs}
        )

    @flux.method
    def spec_pattern_for(self, cls: type[SpecContribution]) -> pm.Carrier | None:
        specs = tuple(contrib for contrib in self.contributions if isinstance(contrib, cls))
        if not specs:
            return None
        return pm.compile(
            {contrib.spec_binding_ir.admission: frozenset((contrib,)) for contrib in specs}
        )

    @flux.method
    def check(self):
        pass
