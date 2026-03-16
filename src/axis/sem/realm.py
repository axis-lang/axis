from __future__ import annotations
from typing import Iterable

from protobase import Consed, flux, frozendict
import protomorph as pm

from .context import Context
from .entity import Entity

type Namespaces = frozendict[pm.Anchor, frozenset[pm.Anchor]]


class Realm(pm.SemanticBridgeBase, Consed):

    @property
    def all_contexts(self) -> tuple[Context, ...]:
        raise NotImplementedError

    @flux.property
    def all_contributions(self) -> frozenset[Context.Contribution]:
        return frozenset(
            contribution
            for ctx in self.all_contexts
            for contribution in ctx.contributions
        )

    @flux.property
    def contributions_by_anchor(
        self,
    ) -> frozendict[pm.Anchor, frozenset[Context.Contribution]]:
        by_anchors: dict[pm.Anchor, list[Context.Contribution]] = {}
        for contribution in self.all_contributions:
            by_anchors.setdefault(contribution.anchor, []).append(contribution)
        return frozendict(
            (anchor, frozenset(contribs)) for anchor, contribs in by_anchors.items()
        )

    @flux.property
    def all_anchors(self) -> frozenset[pm.Anchor]:
        return frozenset(self.contributions_by_anchor.keys())

    @flux.property
    def namespaces_by_anchor(self) -> Namespaces:
        namespaces: dict[pm.Anchor, set[pm.Anchor]] = {}
        for anchor in self.all_anchors:
            if (parent := anchor.parent) is not None:
                namespaces.setdefault(parent, set()).add(anchor)
        return frozendict(
            (parent, frozenset(children)) for parent, children in namespaces.items()
        )

    @flux.property
    def entities_by_anchor(self) -> frozendict[pm.Anchor, Entity]:
        return frozendict(
            (anchor, Entity(anchor=anchor, contributions=contributions))
            for anchor, contributions in self.contributions_by_anchor.items()
        )

    @property
    def all_entities(self) -> Iterable[Entity]:
        return self.entities_by_anchor.values()

    def __getitem__(self, anchor: pm.Anchor | str) -> Entity:
        if isinstance(anchor, str):
            anchor = pm.Anchor.from_str(anchor)

        if anchor not in self.entities_by_anchor:
            raise KeyError(f"Anchor {anchor} not found in realm")

        return self.entities_by_anchor[anchor]

    def layout(self, type: pm.Type) -> pm.Layout | None:
        if not isinstance(type, pm.NominalType):
            return super().layout(type)

        entity = (
            self.entities_by_anchor[type.spec_ref.anchor]
            if type.spec_ref.anchor in self.entities_by_anchor
            else None
        )
        if entity is None:
            return super().layout(type)

        overload = _resolve_nominal_overload(entity, type)
        if overload is None:
            return super().layout(type)

        return overload.layout(_spec_args_for_overload(overload, type.spec_ref))

    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        return super().project(type, key)

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        return super().lift(qualifier, result)

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type:
        return super().combine(left, right, op=op)
    


    @flux.method
    def check(self):
        with self:
            for contribution in self.all_contexts:
                contribution.check()
            for contribution in self.all_contributions:
                contribution.check()
            for entity in self.all_entities:
                entity.check()


def _resolve_nominal_overload(
    entity: Entity,
    type_: pm.NominalType,
) -> Entity.OverloadContribution | None:
    target_shape = type_.spec_ref.struct_shape
    matches: list[Entity.OverloadContribution] = []
    for binding_shape, bucket in entity.spec_by_shape.items():
        struct_shape, open_tail = binding_shape
        if open_tail:
            continue
        if struct_shape != target_shape:
            continue
        for contrib in bucket.specs:
            if isinstance(contrib, Entity.OverloadContribution):
                matches.append(contrib)

    if len(matches) != 1:
        return None
    return matches[0]


def _spec_args_for_overload(
    overload: Entity.OverloadContribution,
    spec_ref: pm.Spec,
) -> pm.Struct[str, pm.Val]:
    spec_args = spec_ref.args
    if spec_args is None:
        return pm.Struct.Empty

    entries: list[tuple[str, pm.Val]] = []
    for binding, value in zip(overload.spec_bindings.values, spec_args.values):
        if binding.binder_name is None:
            continue
        entries.append((binding.binder_name, value))
    return pm.Struct.from_iter(entries)
