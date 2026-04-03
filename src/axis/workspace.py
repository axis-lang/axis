from __future__ import annotations

from typing import Any, TYPE_CHECKING

from protobase import flux

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

    def schema_for(self, spec: Any) -> Any | None:
        _ = spec
        return None
