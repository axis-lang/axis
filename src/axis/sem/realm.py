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

        contribution, spec_args = _resolve_nominal_layout_contribution(entity, type)
        if contribution is None or spec_args is None:
            return super().layout(type)

        return contribution.layout(spec_args)

    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        if isinstance(type, pm.NominalQualifier):
            projected = self.project(type.underlying, key)
            return self.lift(type, projected)

        layout = self.layout(type)
        if isinstance(layout, pm.StructLayout):
            if isinstance(key, str):
                try:
                    return layout.fields.get(key)
                except KeyError:
                    if isinstance(type, pm.NominalType):
                        contribution, _ = _resolve_nominal_layout_contribution(
                            self[type.spec_ref.anchor],
                            type,
                        )
                        if contribution is not None:
                            offset = _layout_field_offset(contribution, key)
                            if offset is not None:
                                return layout.fields[offset]
                    raise
            if isinstance(key, int):
                return layout.fields[key]
            raise TypeError(f"Unsupported key type: {type(key)}")

        return super().project(type, key)

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        if isinstance(qualifier, pm.NominalQualifier):
            return pm.nominal_qual(
                qualifier.spec_ref.anchor,
                qualifier.spec_ref._args_const(),
                underlying=result,
            )

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


def _resolve_nominal_layout_contribution(
    entity: Entity,
    type_: pm.NominalType,
) -> tuple[
    Entity.OverloadContribution | Entity.QualContribution | None,
    pm.Struct[str, pm.Val] | None,
]:
    matches: list[
        tuple[Entity.OverloadContribution | Entity.QualContribution, pm.Struct[str, pm.Val]]
    ] = []
    for contrib in entity.contributions:
        if not isinstance(contrib, (Entity.OverloadContribution, Entity.QualContribution)):
            continue

        spec_args = _spec_args_for_overload(contrib, type_.spec_ref)
        if spec_args is None:
            continue

        matches.append((contrib, spec_args))

    if len(matches) != 1:
        return None, None

    return matches[0]


def _spec_args_for_overload(
    contribution: Entity.SpecContribution,
    spec_ref: pm.Spec,
) -> pm.Struct[str, pm.Val] | None:
    if contribution.spec_bindings.open_tail:
        return None

    spec_args = spec_ref.args
    bindings = contribution.spec_bindings.values
    if spec_args is None:
        return pm.Struct.Empty if not bindings else None

    positional_args = [
        value
        for key, value in zip(spec_args.index.keys, spec_args.values)
        if key is None
    ]
    nominal_args = {
        key: value
        for key, value in zip(spec_args.index.keys, spec_args.values)
        if key is not None
    }
    matched_nominal_keys: set[str] = set()
    positional_offset = 0

    entries: list[tuple[str, pm.Val]] = []
    for binding in bindings:
        value: pm.Val | None = None
        for key in (binding.slot_key, binding.binder_name):
            if key is None or key in matched_nominal_keys:
                continue
            candidate = nominal_args.get(key)
            if candidate is None:
                continue
            matched_nominal_keys.add(key)
            value = candidate
            break

        if value is None:
            if positional_offset >= len(positional_args):
                return None
            value = positional_args[positional_offset]
            positional_offset += 1

        if binding.binder_name is None:
            continue
        entries.append((binding.binder_name, value))

    if positional_offset != len(positional_args):
        return None

    if matched_nominal_keys != nominal_args.keys():
        return None

    return pm.Struct.from_iter(entries)


def _layout_field_offset(
    contribution: Entity.OverloadContribution | Entity.QualContribution,
    key: str,
) -> int | None:
    for offset, binding in enumerate(contribution.param_bindings.values):
        if binding.slot_key == key or binding.binder_name == key:
            return offset
    return None
