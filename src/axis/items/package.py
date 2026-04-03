from __future__ import annotations

from typing import Self

from protobase import Consed, flux

from axis import src, log

from .item import Item


class Package(Consed):
    dir: src.SourceDir
    codebase: Consed | None = None

    @classmethod
    def from_path(cls, path: str | src.Path) -> Self:
        from axis.codebase import Codebase

        package_dir = src.SourceDir.from_path(path)
        codebase = Codebase.from_path(package_dir.path.parent)
        return cls(dir=package_dir, codebase=codebase)

    @property
    def name(self) -> str:
        return self.dir.name

    @flux.property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    @property
    def source_files(self) -> frozenset[src.SourceFile]:
        return frozenset(self.dir.glob("**/*.ax"))

    @flux.method
    def file_items(self, file: src.SourceFile) -> frozenset[Item]:
        from axis import items
        return frozenset(
            #item for item in items.Unit.from_src(file, realm=self)
            item for item in items.Unit.from_src(file, package=self)
            if isinstance(item, Item)
        )

    @flux.property
    def items(self) -> frozenset[Item]:
        return frozenset(
            item
            for file in self.source_files
            for item in self.file_items(file)
        )

    @property
    def all_contexts(self):
        return tuple(self.items)

    @property
    def all_reports(self) -> frozenset[log.Report]:
        # TODO: Ya no podemos hacer el check desde la parte sintactica, debemos ejecutar check en las contribuciones semanticas (sem)
        #self.check()
        #return flux.collect(Package.check, obj=self, cls=log.Report)
        return frozenset()
