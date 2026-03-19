from __future__ import annotations

from typing import cast

from protobase import Consed, flux, _

import protomorph as pm

from axis import log, sem, syn


class Facet(Consed, abstract=True):
    pass


def _layout_field_key(binding: sem.BindingStruct.Field | sem.LoweredBindingStruct.Field) -> str | None:
    return binding.slot_key if binding.slot_key is not None else binding.binder_name


class Entity(Consed):
    anchor: pm.Anchor
    contributions: frozenset[sem.Context.Contribution]

    class SpecContribution(sem.Context.EntityContribution, abstract=True):
        spec_bindings: sem.BindingStruct = _

        def _spec_binder(self, field: sem.BindingStruct.Field) -> pm.Var | None:
            name = field.binder_name
            if name is None:
                return None
            return pm.var(Entity.SpecVar, self, name)

        @flux.property
        def spec_scope(self) -> sem.Scope:
            builder = sem.Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            builder.define("Self", pm.var(Entity.SpecVar, self, "Self"), origin=self.origin)
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
        def spec_schema(self) -> pm.StructSchema:
            return sem.binding_schema(self.lowered_spec_bindings)

        @flux.method
        def check(self):
            self.spec_scope
            self.lowered_spec_bindings
            self.spec_schema

    class SpecVar(pm.VarType[SpecContribution]):
        pass

    class PredicateFacet(Facet, SpecContribution):
        pass

    class OverloadContribution(SpecContribution, abstract=True):
        param_bindings: sem.BindingStruct = _

        def _param_binder(self, field: sem.BindingStruct.Field) -> pm.Var | None:
            name = field.binder_name
            if name is None:
                return None
            return pm.var(Entity.ParamVar, self, name)

        @flux.property
        def overload_scope(self) -> sem.Scope:
            builder = sem.Scope.Builder(name=self.anchor.name, parent=self.spec_scope)
            builder.define("self", pm.var(Entity.ParamVar, self, "self"), origin=self.origin)
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
        def param_schema(self) -> pm.StructSchema:
            return sem.binding_schema(self.lowered_param_bindings)

        @flux.method
        def layout(self, args: pm.Struct[str | None, pm.Val]) -> pm.StructLayout | None:
            field_types = tuple(
                _bound_type(self, field.match_expr, args)
                for field in self.lowered_param_bindings.non_spread_fields
            )
            keys = tuple(field.slot_key for field in self.lowered_param_bindings.non_spread_fields)
            return pm.StructLayout(fields=pm.Struct.from_keys(keys, field_types))

        @flux.method
        def check(self):
            self.overload_scope
            self.lowered_spec_bindings
            self.spec_schema
            self.lowered_param_bindings
            self.param_schema

    class ParamVar(pm.VarType[OverloadContribution]):
        pass

    class ClassFacet(Facet, OverloadContribution):
        pass

    class ResultContribution(OverloadContribution, abstract=True):
        result_bound_expr: syn.Expr | None = _

        @flux.property
        def result_bound(self) -> pm.Val | None:
            return sem.build_bound(self.result_bound_expr, self.overload_scope)

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
        def param_schema(self) -> pm.StructSchema:
            return sem.binding_schema(self.lowered_param_bindings)

        @flux.property
        def underlying_bound(self) -> pm.Val | None:
            return sem.build_bound(self.underlying_bound_expr, self.spec_scope)

        @flux.method
        def layout(self, args: pm.Struct[str | None, pm.Val]) -> pm.StructLayout | None:
            field_types = tuple(
                _bound_type(self, field.match_expr, args)
                for field in self.lowered_param_bindings.non_spread_fields
            )
            field_keys = tuple(_layout_field_key(field) for field in self.lowered_param_bindings.non_spread_fields)
            return pm.StructLayout(fields=pm.Struct.from_keys(field_keys, field_types))

        @flux.method
        def check(self):
            self.spec_scope
            self.lowered_spec_bindings
            self.spec_schema
            self.lowered_param_bindings
            self.param_schema
            self.underlying_bound

    @flux.property
    def spec_contributions(self) -> frozenset[SpecContribution]:
        return frozenset(
            contrib for contrib in self.contributions if isinstance(contrib, Entity.SpecContribution)
        )

    @flux.property
    def spec_index(self):
        return sem.SpecIndex(contribs=self.spec_contributions)

    @flux.property
    def overload_contributions(self) -> frozenset[Entity.OverloadContribution]:
        return frozenset(
            contrib
            for contrib in self.spec_contributions
            if isinstance(contrib, Entity.OverloadContribution)
        )

    @flux.property
    def overload_index(self):
        return sem.OverloadIndex(contribs=self.overload_contributions)

    @flux.method
    def search_specs(
        self,
        spec_ref: pm.Spec,
        facet_cls: type[Facet] | None = None,
    ) -> pm.ResolveResult[Entity.SpecContribution]:
        if spec_ref.anchor != self.anchor:
            return pm.ResolveResult()
        return self.spec_index.search(spec_ref.args or pm.Struct.Empty, facet_cls=facet_cls)

    @flux.method
    def match_specs(
        self,
        spec_ref: pm.Spec,
        facet_cls: type[Facet] | None = None,
    ) -> frozenset[Entity.SpecContribution]:
        return self.search_specs(spec_ref, facet_cls=facet_cls).goals

    @flux.method
    def exists_spec(
        self,
        spec_ref: pm.Spec,
        facet_cls: type[Facet] | None = None,
    ) -> bool:
        return bool(self.match_specs(spec_ref, facet_cls=facet_cls))

    @flux.method
    def facet(self, cls: type[sem.Context.Contribution]) -> frozenset[sem.Context.Contribution]:
        if not issubclass(cls, sem.Context.Contribution):
            raise TypeError(f"Expected Contribution subtype, got {cls!r}")
        return frozenset(contrib for contrib in self.contributions if isinstance(contrib, cls))

    @flux.property
    def facts(self) -> frozenset[pm.Spec]:
        return frozenset(fact for contrib in self.contributions for fact in contrib.facts)

    @flux.property
    def clauses(self) -> frozenset[pm.Clause]:
        return frozenset(clause for contrib in self.contributions for clause in contrib.clauses)

    @flux.method
    def check(self):
        self.spec_index
        self.overload_index


def _bound_type(
    contrib: Entity.SpecContribution,
    bound: pm.Val | None,
    args: pm.Struct[str | None, pm.Val],
) -> pm.Type:
    if bound is None:
        return pm.ANY_TYPE

    resolved = bound.subst(lambda value: _resolve_spec_var(contrib, value, args))
    resolved_type = sem.bound_as_type(resolved)
    return pm.ANY_TYPE if resolved_type is None else resolved_type


def _resolve_spec_var(
    contrib: Entity.SpecContribution,
    value: pm.Val,
    args: pm.Struct[str | None, pm.Val],
) -> pm.Val | None:
    if not isinstance(value, pm.Var):
        return None
    var = value
    if not isinstance(var.__type__, Entity.SpecVar):
        return None
    if var.__type__.ctx is not contrib:
        return None
    if not isinstance(var.__data__, str):
        return None
    return args.get(cast(str, var.__data__), default=None)
