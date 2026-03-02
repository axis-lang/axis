from __future__ import annotations

from typing import Iterable

from protobase import Consed, Inmutable, flux, frozendict, _

from axis import dom, src, syn, sem

class Entity(Inmutable):
    class Context(syn.SegregatedItem, abstract=True):
        realm: sem.Realm = _

        @flux.property
        def scope(self) -> sem.Scope:
            raise NotImplementedError

        @flux.property
        def contributions(self) -> frozenset["Entity.Contribution"]:
            raise NotImplementedError

    class Contribution(Consed, abstract=True):
        anchor: dom.Anchor
        origin: syn.Node
        ctx: Entity.Context

    class Member(Contribution):
        name: str
        target: dom.Ref

    class SpecContribution(Contribution):
        spec: dom.Struct[str, dom.Bound]

    class OverloadContribution(SpecContribution):
        params: dom.Struct[str, dom.Bound]

    class ImplContribution(OverloadContribution):
        returns: dom.Bound

    class Constraint(Inmutable):
        struct: dom.Struct[str, dom.Bound]

    class Overload(Inmutable):
        spec: "Entity.Constraint"
        params: dom.Struct[str, dom.Bound]

    ref: dom.Anchor
    spec_buckets: frozendict[dom.Struct.Shape, Constraint] = frozendict()
    overloads: frozendict[dom.Struct.Shape, Overload] = frozendict()
    implementations: frozendict[
        dom.Struct.Shape, tuple["Entity.ImplContribution", ...]
    ] = frozendict()

    class View(Inmutable):
        base: "Entity"
        ref: dom.Ref

        @property
        def spec_buckets(self):
            return self.base.spec_buckets

        @property
        def overloads(self):
            return self.base.overloads

        @property
        def implementations(self):
            return self.base.implementations

    @classmethod
    def empty(cls, ref: dom.Anchor) -> "Entity":
        return cls(
            ref=ref,
            spec_buckets=frozendict(),
            overloads=frozendict(),
            implementations=frozendict(),
        )

    @classmethod
    def from_contributions(
        cls, ref: dom.Anchor, contributions: Iterable["Entity.Contribution"]
    ) -> "Entity":
        spec_buckets = _build_spec_buckets(contributions)
        overloads = _build_overloads(contributions)
        implementations = _build_implementations(contributions)
        return cls(
            ref=ref,
            spec_buckets=frozendict(spec_buckets),
            overloads=frozendict(overloads),
            implementations=frozendict(implementations),
        )

    def view(self, ref: dom.Ref) -> "Entity.View":
        return Entity.View(base=self, ref=ref)

    def __rich__(self):
        from rich.text import Text

        return Text(
            f"Entity({self.ref}) specs={len(self.spec_buckets)} "
            f"overloads={len(self.overloads)} impls={len(self.implementations)}"
        )


def _is_full(struct: dom.Struct[str, dom.Bound]) -> bool:
    return struct.index.is_full


def _emit_invalid(contribution: Entity.Contribution, kind: str) -> None:
    diag = src.error(f"{kind} struct must be full")
    span = src.span_of(contribution.origin)
    if span is not None:
        diag = diag.with_label(
            src.Label(
                span=span,
                message="invalid shape",
                style=src.LabelStyle.PRIMARY,
            )
        )
    diag.emit()


def _emit_collision(contribution: Entity.Contribution, kind: str, shape: dom.Struct.Shape) -> None:
    diag = src.error(f"{kind} shape collision: {shape!r}")
    span = src.span_of(contribution.origin)
    if span is not None:
        diag = diag.with_label(
            src.Label(
                span=span,
                message="colliding contribution",
                style=src.LabelStyle.PRIMARY,
            )
        )
    diag.emit()


def _build_spec_buckets(
    contributions: Iterable[Entity.Contribution],
) -> dict[dom.Struct.Shape, Entity.Constraint]:
    specs: list[Entity.SpecContribution] = [
        c for c in contributions if type(c) is Entity.SpecContribution
    ]
    valid: list[Entity.SpecContribution] = []
    for contrib in specs:
        if not _is_full(contrib.spec):
            _emit_invalid(contrib, "spec")
            continue
        valid.append(contrib)

    buckets: dict[dom.Struct.Shape, list[Entity.SpecContribution]] = {}
    for contrib in valid:
        buckets.setdefault(contrib.spec.shape, []).append(contrib)

    result: dict[dom.Struct.Shape, Entity.Constraint] = {}
    for shape, items in buckets.items():
        if len(items) > 1:
            for contrib in items:
                _emit_collision(contrib, "spec", shape)
            continue
        result[shape] = Entity.Constraint(struct=items[0].spec)

    return result


def _build_overloads(
    contributions: Iterable[Entity.Contribution],
) -> dict[dom.Struct.Shape, Entity.Overload]:
    overloads: list[Entity.OverloadContribution] = [
        c for c in contributions if type(c) is Entity.OverloadContribution
    ]
    valid: list[Entity.OverloadContribution] = []
    for contrib in overloads:
        if not _is_full(contrib.spec):
            _emit_invalid(contrib, "spec")
            continue
        if not _is_full(contrib.params):
            _emit_invalid(contrib, "params")
            continue
        valid.append(contrib)

    buckets: dict[dom.Struct.Shape, list[Entity.OverloadContribution]] = {}
    for contrib in valid:
        buckets.setdefault(contrib.params.shape, []).append(contrib)

    result: dict[dom.Struct.Shape, Entity.Overload] = {}
    for shape, items in buckets.items():
        if len(items) > 1:
            for contrib in items:
                _emit_collision(contrib, "params", shape)
            continue
        constraint = Entity.Constraint(struct=items[0].spec)
        result[shape] = Entity.Overload(spec=constraint, params=items[0].params)

    return result


def _build_implementations(
    contributions: Iterable[Entity.Contribution],
) -> dict[dom.Struct.Shape, tuple[Entity.ImplContribution, ...]]:
    impls: list[Entity.ImplContribution] = [
        c for c in contributions if isinstance(c, Entity.ImplContribution)
    ]
    valid: list[Entity.ImplContribution] = []
    for contrib in impls:
        if not _is_full(contrib.spec):
            _emit_invalid(contrib, "spec")
            continue
        if not _is_full(contrib.params):
            _emit_invalid(contrib, "params")
            continue
        valid.append(contrib)

    buckets: dict[dom.Struct.Shape, list[Entity.ImplContribution]] = {}
    for contrib in valid:
        buckets.setdefault(contrib.params.shape, []).append(contrib)

    return {shape: tuple(items) for shape, items in buckets.items()}
