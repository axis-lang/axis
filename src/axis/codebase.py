from __future__ import annotations

from pathlib import Path
from typing import Self

from protobase import Consed, flux

from axis import items, src


class Codebase(Consed):
    dir: src.SourceDir
    parent: Codebase | None = None

    @classmethod
    def from_path(
        cls,
        path: str | src.Path,
        *,
        parent: Codebase | None = None,
    ) -> Self:
        return cls(dir=src.SourceDir.from_path(path), parent=parent)

    @property
    def name(self) -> str:
        return self.dir.name

    @flux.property
    def package_dirs(self) -> frozenset[src.SourceDir]:
        matches: set[src.SourceDir] = set()
        for path in sorted(self.dir.path.iterdir()):
            if not path.is_dir() or path.name.startswith("."):
                continue
            if not any(child.suffix == ".ax" for child in path.iterdir() if child.is_file()):
                continue
            matches.add(src.SourceDir.from_path(path))
        return frozenset(matches)

    @flux.property
    def packages(self) -> frozenset[items.Package]:
        return frozenset(
            items.Package(dir=package_dir, codebase=self)
            for package_dir in self.package_dirs
        )

    @flux.method
    def package(self, name: str) -> items.Package:
        normalized = Path(name).name
        for package in self.packages:
            if package.name == normalized:
                return package
        if self.parent is not None:
            return self.parent.package(normalized)
        raise KeyError(f"Package {name!r} not found in codebase hierarchy")
