from __future__ import annotations

from protobase import Consed, flux, frozendict, _
import protomorph as pm

from axis import expr, syn, log
from axis.expr.ir import build_bound, build_default
from axis.expr.ir import Scope


from .context import Context


class Entity(Consed):
    anchor: pm.Anchor
    contributions: frozenset[Context.Contribution]

    # @classmethod
    # def from_contributions(
    #     cls,
    #     anchor: dom.Anchor,
    #     contributions: Iterable[Context.Contribution],
    # ) -> "Entity":
    #     return cls(anchor=anchor, contributions=frozenset(contributions))

    class Bucket(Consed):
        def check(self):
            pass

    class SpecContribution(Context.Contribution):
        class SpecBinding(Context.Binding):
            pass

        spec_bindings: pm.Struct[str, SpecBinding] = _

        @flux.property
        def spec_scope(self) -> Scope:
            """Scope populated with SpecVars for each spec binding.

            Parented to the context scope so bound expressions can build
            bounds from names in the enclosing module/block.
            """

            builder = Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            builder.define("Self", pm.var(Entity.SpecVar, self, "Self"), origin=self.origin)
            for binding in self.spec_bindings:
                name = expr.to_slot_name(binding.key)
                var = pm.var(Entity.SpecVar, self, name)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def spec_bounds(self) -> pm.Struct[str, pm.Val | None]:
            """Build bound values for each specialization binding.

            Uses spec_scope so that SpecVars and enclosing context names
            are available while constructing bounds.
            """
            scope = self.spec_scope
            return self.spec_bindings.map(
                lambda binding: build_bound(binding.bound_expr, scope)
            )

        @flux.property
        def spec_defaults(self) -> pm.Struct[str, pm.Val | None]:
            scope = self.spec_scope
            return self.spec_bindings.map(
                lambda binding: build_default(binding.default_expr, scope)
            )

        @flux.method
        def check(self):
            # Trigger scope construction and bound creation
            self.spec_scope
            self.spec_bounds
            self.spec_defaults

    class SpecVar(pm.VarType[SpecContribution]): ...

    class SpecBucket(Bucket):
        specs: frozenset[Entity.SpecContribution]
        

        @flux.property
        def overload_by_shape(
            self,
        ) -> frozendict[pm.Struct.Shape, Entity.OverloadBucket]:
            return _overload_by_shape_bucket(self.specs)

    @flux.property
    def spec_by_shape(self) -> frozendict[pm.Struct.Shape, SpecBucket]:
        return _spec_by_shape_bucket(self.contributions)

    class OverloadContribution(SpecContribution):
        class ParamBinding(Context.Binding):
            pass

        param_bindings: pm.Struct[str, ParamBinding] = _

        @flux.property
        def overload_scope(self) -> Scope:
            """Scope with spec_scope as parent, populated with ParamVars."""
            builder = Scope.Builder(name=self.anchor.name, parent=self.spec_scope)
            builder.define("self", pm.var(Entity.ParamVar, self, "self"), origin=self.origin)
            for binding in self.param_bindings:
                name = expr.to_slot_name(binding.key)
                var = pm.var(Entity.ParamVar, self, name)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def param_bounds(self) -> pm.Struct[str, pm.Val | None]:
            """Build bound values for each parameter binding.

            Uses overload_scope so that SpecVars, ParamVars, and enclosing
            context names are all available while constructing bounds.
            """
            scope = self.overload_scope
            return self.param_bindings.map(
                lambda binding: build_bound(binding.bound_expr, scope)
            )

        @flux.property
        def param_defaults(self) -> pm.Struct[str, pm.Val | None]:
            scope = self.overload_scope
            return self.param_bindings.map(
                lambda binding: build_default(binding.default_expr, scope)
            )

        @flux.method
        def check(self):
            # Trigger scope construction and bound creation for both levels
            self.overload_scope
            self.spec_bounds
            self.spec_defaults
            self.param_bounds
            self.param_defaults

    class ParamVar(pm.VarType[OverloadContribution]): ...

    class OverloadBucket(Bucket):
        overloads: frozenset[Entity.OverloadContribution]

        # @flux.property
        # def impl_by_result(self) -> frozendict[syn.Expr | None, Entity.ImplBucket]:
        #     return _impl_by_result_bucket(self.overloads)

    @flux.property
    def overload_by_shape(self) -> frozendict[pm.Struct.Shape, OverloadBucket]:
        return _overload_by_shape_bucket(self.contributions)

    class ImplContribution(OverloadContribution):
        returns: syn.Expr | None = _

        def __invariant__(self):
            if self.returns is None:
                log.warn("ImplContribution without returns").label(self.origin).emit()

    class ImplBucket(Bucket):
        impls: frozenset[Entity.ImplContribution]

    @flux.property
    def impl_by_result(self) -> frozendict[syn.Expr | None, ImplBucket]:
        return _impl_by_result_bucket(self.contributions)

    @flux.method
    def check(self):
        pass
def _spec_by_shape_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[pm.Struct.Shape, Entity.SpecBucket]:
    specs: dict[pm.Struct.Shape, list[Entity.SpecContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.SpecContribution):
            specs.setdefault(contrib.spec_bindings.shape, []).append(contrib)

    return frozendict(
        (
            (shape, Entity.SpecBucket(specs=frozenset(spec)))
            for shape, spec in specs.items()
        )
    )


def _overload_by_shape_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[pm.Struct.Shape, Entity.OverloadBucket]:
    overloads: dict[pm.Struct.Shape, list[Entity.OverloadContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.OverloadContribution):
            overloads.setdefault(contrib.param_bindings.shape, []).append(contrib)

    return frozendict(
        (
            (shape, Entity.OverloadBucket(overloads=frozenset(overload)))
            for shape, overload in overloads.items()
        )
    )


def _impl_by_result_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[syn.Expr | None, Entity.ImplBucket]:
    impls: dict[syn.Expr | None, list[Entity.ImplContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.ImplContribution):
            if contrib.param_bindings.index.is_empty:
                impls.setdefault(contrib.returns, []).append(contrib)

    return frozendict(
        (
            (returns, Entity.ImplBucket(impls=frozenset(impl)))
            for returns, impl in impls.items()
        )
    )
