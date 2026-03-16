from __future__ import annotations

from collections.abc import Callable

from protobase import Consed, flux, frozendict, _
import protomorph as pm

from axis import syn, log


from .binding import Binding, BindingShape, BindingStruct
from .bound import build_bound, build_default
from .context import Context
from .scope import Scope


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
        spec_bindings: BindingStruct[Binding] = _

        @flux.property
        def spec_scope(self) -> Scope:
            """Scope populated with SpecVars for each spec binding.

            Parented to the context scope so bound expressions can build
            bounds from names in the enclosing module/block.
            """

            builder = Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            builder.define(
                "Self", pm.var(Entity.SpecVar, self, "Self"), origin=self.origin
            )
            for binding in self.spec_bindings:
                name = binding.binder_name
                if name is None:
                    continue
                var = pm.var(Entity.SpecVar, self, name)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def spec_bounds(self) -> BindingStruct[pm.Val | None]:
            """Build bound values for each specialization binding.

            Uses spec_scope so that SpecVars and enclosing context names
            are available while constructing bounds.
            """
            scope = self.spec_scope
            return self.spec_bindings.map(
                lambda binding: build_bound(binding.bound_expr, scope)
                # lambda binding: (
                #     binding.bound_expr.to_bound(scope)
                #     if binding.bound_expr is not None
                #     else None
                # )
            )

        @flux.property
        def spec_defaults(self) -> BindingStruct[pm.Val | None]:
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
        ) -> frozendict[BindingShape, Entity.OverloadBucket]:
            return _overload_by_shape_bucket(self.specs)

    class QualContribution(SpecContribution):
        underlying_bound_expr: syn.Expr = _

        @flux.property
        def underlying_bound(self) -> pm.Val | None:
            return build_bound(self.underlying_bound_expr, self.spec_scope)

    @flux.property
    def spec_by_shape(self) -> frozendict[BindingShape, SpecBucket]:
        return _spec_by_shape_bucket(self.contributions)

    class OverloadContribution(SpecContribution):
        param_bindings: BindingStruct[Binding] = _

        @flux.property
        def overload_scope(self) -> Scope:
            """Scope with spec_scope as parent, populated with ParamVars."""
            builder = Scope.Builder(name=self.anchor.name, parent=self.spec_scope)
            builder.define(
                "self", pm.var(Entity.ParamVar, self, "self"), origin=self.origin
            )
            for binding in self.param_bindings:
                name = binding.binder_name
                if name is None:
                    continue
                var = pm.var(Entity.ParamVar, self, name)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def param_bounds(self) -> BindingStruct[pm.Val | None]:
            """Build bound values for each parameter binding.

            Uses overload_scope so that SpecVars, ParamVars, and enclosing
            context names are all available while constructing bounds.
            """
            scope = self.overload_scope
            return self.param_bindings.map(
                lambda binding: build_bound(binding.bound_expr, scope)
            )

        @flux.property
        def param_defaults(self) -> BindingStruct[pm.Val | None]:
            scope = self.overload_scope
            return self.param_bindings.map(
                lambda binding: build_default(binding.default_expr, scope)
            )

        @flux.method
        def layout(self, args: pm.Struct[str, pm.Val]) -> pm.StructLayout | None:
            keys = self.param_bindings.index.keys
            field_types = tuple(
                _param_bound_type(self, bound, args)
                for bound in self.param_bounds.values
            )
            return pm.StructLayout(fields=pm.Struct.from_keys(keys, field_types))

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
    def overload_by_shape(self) -> frozendict[BindingShape, OverloadBucket]:
        return _overload_by_shape_bucket(self.contributions)

    class ImplContribution(OverloadContribution):
        result_bound_expr: syn.Expr | None = _

        @flux.property
        def result_bound(self) -> pm.Val | None:
            return build_bound(self.result_bound_expr, self.overload_scope)

        def __invariant__(self):
            if self.result_bound_expr is None:
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
) -> frozendict[BindingShape, Entity.SpecBucket]:
    return _group_by_shape(
        contributions,
        Entity.SpecContribution,
        lambda c: c.spec_bindings.shape,
        lambda items: Entity.SpecBucket(specs=items),
    )


def _overload_by_shape_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[BindingShape, Entity.OverloadBucket]:
    return _group_by_shape(
        contributions,
        Entity.OverloadContribution,
        lambda c: c.param_bindings.shape,
        lambda items: Entity.OverloadBucket(overloads=items),
    )


def _group_by_shape[C, K, B](
    contributions: frozenset[Context.Contribution],
    contrib_type: type[C],
    shape_key: Callable[[C], K],
    make_bucket: Callable[[frozenset[C]], B],
) -> frozendict[K, B]:
    groups: dict[K, list[C]] = {}
    for contrib in contributions:
        if isinstance(contrib, contrib_type):
            groups.setdefault(shape_key(contrib), []).append(contrib)
    return frozendict(
        (key, make_bucket(frozenset(items))) for key, items in groups.items()
    )


def _impl_by_result_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[syn.Expr | None, Entity.ImplBucket]:
    impls: dict[syn.Expr | None, list[Entity.ImplContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.ImplContribution):
            if contrib.param_bindings.index.is_empty:
                impls.setdefault(contrib.result_bound_expr, []).append(contrib)

    return frozendict(
        (
            (returns, Entity.ImplBucket(impls=frozenset(impl)))
            for returns, impl in impls.items()
        )
    )


def _param_bound_type(
    contrib: Entity.OverloadContribution,
    bound: pm.Val | None,
    args: pm.Struct[str, pm.Val],
) -> pm.Type:
    if bound is None:
        return pm.ANY_TYPE

    resolved = bound.subst(lambda var: _resolve_spec_var(contrib, var, args))
    resolved_type = resolved.as_type()
    return pm.ANY_TYPE if resolved_type is None else resolved_type


def _resolve_spec_var(
    contrib: Entity.OverloadContribution,
    var: pm.Var,
    args: pm.Struct[str, pm.Val],
) -> pm.Val | None:
    if not isinstance(var.__type__, Entity.SpecVar):
        return None
    if var.__type__.ctx is not contrib:
        return None
    return args.get(var.__data__, default=None)
