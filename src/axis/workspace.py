from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

import protomorph as pm

from protobase import flux, frozendict

from axis import items, log, sem

from .codebase import Codebase

if TYPE_CHECKING:
    import axis


class Workspace(sem.Realm):
    codebase: Codebase
    roots: tuple[str | items.Package, ...] = ()

    @flux.property
    def root_packages(self) -> tuple[items.Package, ...]:
        packages: list[items.Package] = []
        for root in self.roots:
            package = root if isinstance(root, items.Package) else self.codebase.package(root)
            packages.append(package)
        return tuple(packages)

    @flux.property
    def packages(self) -> tuple[items.Package, ...]:
        resolved: dict[str, items.Package] = {}
        pending = list(self.root_packages)
        while pending:
            package = pending.pop()
            key = str(package.dir.path)
            if key in resolved:
                continue
            resolved[key] = package
            for dependency in package.dependencies:
                pending.append(self.codebase.package(dependency))
        return tuple(resolved[key] for key in sorted(resolved))

    @property
    def all_contexts(self) -> tuple[sem.Context, ...]:
        return tuple(
            context
            for package in self.packages
            for context in package.all_contexts
        )

    @property
    def all_reports(self) -> frozenset[log.Report]:
        return frozenset()

    @flux.property
    def root_entities(self) -> tuple[sem.Entity, ...]:
        grouped: dict[object, list[sem.Context.EntityContribution]] = {}
        for package in self.root_packages:
            for context in package.all_contexts:
                for contribution in context.contributions:
                    if isinstance(contribution, sem.Context.EntityContribution):
                        grouped.setdefault(contribution.anchor, []).append(contribution)
        return tuple(
            sem.Entity(anchor=cast(pm.Anchor, anchor), contributions=frozenset(contributions))
            for anchor, contributions in grouped.items()
        )

    @flux.property
    def status(self) -> sem.Status:
        return sem.Status(children=tuple(entity.status for entity in self.root_entities))

    def schema_for(self, spec: Any) -> Any | None:
        return super().schema_for(spec)
