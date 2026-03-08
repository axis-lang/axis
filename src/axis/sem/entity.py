from __future__ import annotations

from protobase import Consed, flux, frozendict, _

from axis import dom, expr, syn, log
from axis.log import report as logr

from .context import Context
from .scope import Scope


class Entity(Consed):
    anchor: dom.Anchor
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

        spec: dom.Struct[str, SpecBinding] = _

        @flux.property
        def spec_scope(self) -> Scope:
            """Scope populated with Var.spec for each spec binding.

            Parented to the context scope so bound expressions can resolve
            names from the enclosing module/block.
            """
            builder = Scope.Builder(name=self.anchor.name, parent=self.ctx.scope)
            # TODO: Agg a 'Self' definition here for the entity itself, so it can be referenced in specs?
            builder.define("Self", dom.Var.spec("Self", contribution=self), origin=self.origin)
            for binding in self.spec:
                name = expr.to_slot_name(binding.key)
                var = dom.Var.spec(name, contribution=self)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def resolved_spec(self) -> dom.Struct[str, dom.Val | None]:
            """Resolve bound expressions for each spec binding.

            Uses spec_scope so that earlier spec vars and enclosing
            context names are available for bound resolution.
            """
            scope = self.spec_scope
            return self.spec.map(lambda b: resolve_bound(b.bound, scope))

        @flux.method
        def check(self):
            # Trigger scope construction and bound resolution
            self.spec_scope
            self.resolved_spec

    class SpecBucket(Bucket):
        specs: frozenset[Entity.SpecContribution]

        @flux.property
        def overload_by_shape(
            self,
        ) -> frozendict[dom.Struct.Shape, Entity.OverloadBucket]:
            return _overload_by_shape_bucket(self.specs)

    @flux.property
    def spec_by_shape(self) -> frozendict[dom.Struct.Shape, SpecBucket]:
        return _spec_by_shape_bucket(self.contributions)

    class OverloadContribution(SpecContribution):
        class ParamBinding(Context.Binding):
            pass

        params: dom.Struct[str, ParamBinding] = _

        @flux.property
        def overload_scope(self) -> Scope:
            """Scope with spec_scope as parent, populated with Var.param for each param."""
            builder = Scope.Builder(name=self.anchor.name, parent=self.spec_scope)
            builder.define("self", dom.Var.param("self", contribution=self), origin=self.origin)
            for binding in self.params:
                name = expr.to_slot_name(binding.key)
                var = dom.Var.param(name, contribution=self)
                builder.define(name, var, origin=binding.key)
            return builder.build()

        @flux.property
        def resolved_params(self) -> dom.Struct[str, dom.Val | None]:
            """Resolve bound expressions for each param binding.

            Uses overload_scope so that spec vars, param vars, and
            enclosing context names are all available for bound resolution.
            """
            scope = self.overload_scope
            return self.params.map(lambda b: resolve_bound(b.bound, scope))

        @flux.method
        def check(self):
            # Trigger scope construction and bound resolution for both levels
            self.overload_scope
            self.resolved_spec
            self.resolved_params

    class OverloadBucket(Bucket):
        overloads: frozenset[Entity.OverloadContribution]

        # @flux.property
        # def impl_by_result(self) -> frozendict[syn.Expr | None, Entity.ImplBucket]:
        #     return _impl_by_result_bucket(self.overloads)

    @flux.property
    def overload_by_shape(self) -> frozendict[dom.Struct.Shape, OverloadBucket]:
        return _overload_by_shape_bucket(self.contributions)

    class ImplContribution(OverloadContribution):
        returns: syn.Expr | None = _

        def __invariant__(self):
            if self.returns is None:
                log.warn("ImplContribution without returns").label(self.origin).emit()

    # class ImplBucket(Bucket):
    #     impls: frozenset[Entity.ImplContribution]

    # @flux.property
    # def impl_by_result(self) -> frozendict[syn.Expr | None, ImplBucket]:
    #     return _impl_by_result_bucket(self.contributions)

    @flux.method
    def check(self):
        pass


def resolve_bound(bound: syn.Expr | None, scope: Scope) -> dom.Val | None:
    """Resolve a bound expression into a domain value using the given scope.

    Handles Sym (scope lookup) and emits errors for unsupported forms.
    Returns None when bound is absent.
    """
    if bound is None:
        return None
    match bound:
        case expr.Sym() as sym:
            return scope.lookup(sym)
        case _:
            return (
                logr.error("Unsupported bound expression")
                .label(bound, "cannot resolve this bound yet")
                .tag(dom.Err())
            )


def _spec_by_shape_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[dom.Struct.Shape, Entity.SpecBucket]:
    specs: dict[dom.Struct.Shape, list[Entity.SpecContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.SpecContribution):
            specs.setdefault(contrib.spec.shape, []).append(contrib)

    return frozendict(
        (
            (shape, Entity.SpecBucket(specs=frozenset(spec)))
            for shape, spec in specs.items()
        )
    )


def _overload_by_shape_bucket(
    contributions: frozenset[Context.Contribution],
) -> frozendict[dom.Struct.Shape, Entity.OverloadBucket]:
    overloads: dict[dom.Struct.Shape, list[Entity.OverloadContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.OverloadContribution):
            overloads.setdefault(contrib.params.shape, []).append(contrib)

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
            if contrib.params.index.is_empty:
                impls.setdefault(contrib.returns, []).append(contrib)

    return frozendict(
        (
            (returns, Entity.ImplBucket(impls=frozenset(impl)))
            for returns, impl in impls.items()
        )
    )
