from __future__ import annotations

from typing import Iterable

from protobase import Consed, flux, frozendict, _

from axis import dom, syn, log

from .context import Context


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

    class SpecContribution(Context.Contribution):
        class SpecBinding(Context.Binding):
            pass

        spec: dom.Struct[str, SpecBinding] = _

    class SpecBucket(Consed):
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

    class OverloadBucket(Consed):
        overloads: frozenset[Entity.OverloadContribution]

        @flux.property
        def impl_by_result(self) -> frozendict[syn.Expr | None, Entity.ImplBucket]:
            return _impl_by_result_bucket(self.overloads)

    @flux.property
    def overload_by_shape(self) -> frozendict[dom.Struct.Shape, OverloadBucket]:
        return _overload_by_shape_bucket(self.contributions)

    class ImplContribution(OverloadContribution):
        returns: syn.Expr | None = _

        def __invariant__(self):
            if self.returns is None:
                log.warn("ImplContribution without returns").label(self.origin).emit()

    class ImplBucket(Consed):
        impls: frozenset[Entity.ImplContribution]

    @flux.property
    def impl_by_result(self) -> frozendict[syn.Expr | None, ImplBucket]:
        return _impl_by_result_bucket(self.contributions)


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
