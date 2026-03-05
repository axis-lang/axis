from __future__ import annotations

from typing import Iterable

from protobase import Consed, flux, frozendict, _

from axis import dom, syn, sem


class Entity(Consed):
    class Context(syn.SegregatedItem, abstract=True):
        realm: sem.Realm = _

        @flux.property
        def scope(self) -> sem.Scope:
            raise NotImplementedError

        @flux.property
        def contributions(self) -> frozenset["Entity.Contribution"]:
            raise NotImplementedError
        
        # eval

    class Contribution(Consed, abstract=True):
        anchor: dom.Anchor
        origin: syn.Node
        ctx: Entity.Context

    class Member(Contribution):
        name: str
        target: dom.Ref

    ref: dom.Anchor
    contributions: frozenset[Entity.Contribution]

    @classmethod
    def from_contributions(
        cls, ref: dom.Anchor, contributions: Iterable[Entity.Contribution]
    ) -> "Entity":
        return cls(ref=ref, contributions=frozenset(contributions))

    # Specialization

    class SpecContribution(Contribution):
        spec: dom.Struct[str, dom.Bound]

    class SpecBucket(Consed):
        specs: frozenset[Entity.SpecContribution]

        @flux.property
        def overload_by_shape(
            self,
        ) -> frozendict[dom.Struct.Shape, Entity.OverloadBucket]:
            return _overload_by_shape_bucket(self.specs)

        # direct impl by result

    @flux.property
    def spec_by_shape(self) -> frozendict[dom.Struct.Shape, SpecBucket]:
        return _spec_by_shape_bucket(self.contributions)

    # Parametrization

    class OverloadContribution(SpecContribution):
        params: dom.Struct[str, dom.Bound]

    class OverloadBucket(Consed):
        overloads: frozenset[Entity.OverloadContribution]

        @flux.property
        def impl_by_result(self):
            return _impl_by_result_bucket(self.overloads)

    @flux.property
    def overload_by_shape(self) -> frozendict[dom.Struct.Shape, OverloadBucket]:
        return _overload_by_shape_bucket(self.contributions)

    # Implementation

    class ImplContribution(OverloadContribution):
        returns: dom.Bound

    class ImplBucket(Consed):
        impls: frozenset[Entity.ImplContribution]

    @flux.property
    def impl_by_result(self) -> frozendict[dom.Bound, ImplBucket]:
        return _impl_by_result_bucket(self.contributions)


def _spec_by_shape_bucket(
    contributions: frozenset[Entity.Contribution],
) -> frozendict[dom.Struct.Shape, Entity.SpecBucket]:
    specs: dict[dom.Struct.Shape, list[Entity.SpecContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.SpecContribution):
            # for shape in contrib.spec_shapes:
            specs.setdefault(contrib.spec.shape, []).append(contrib)

    return frozendict(
        (
            (shape, Entity.SpecBucket(specs=frozenset(spec)))
            for shape, spec in specs.items()
        )
    )


def _overload_by_shape_bucket(
    contributions: frozenset[Entity.Contribution],
) -> frozendict[dom.Struct.Shape, Entity.OverloadBucket]:
    overloads: dict[dom.Struct.Shape, list[Entity.OverloadContribution]] = {}
    for contrib in contributions:
        if isinstance(contrib, Entity.OverloadContribution):
            # for shape in contrib.params_shapes:
            overloads.setdefault(contrib.params.shape, []).append(contrib)

    return frozendict(
        (
            (shape, Entity.OverloadBucket(overloads=frozenset(overload)))
            for shape, overload in overloads.items()
        )
    )


def _impl_by_result_bucket(
    contributions: frozenset[Entity.Contribution],
) -> frozendict[dom.Bound, Entity.ImplBucket]:
    impls: dict[dom.Bound, list[Entity.ImplContribution]] = {}
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
