from typing import Iterable, Self

from axis import src, log
from protobase import flux
from typing import cast

from axis.sem import Realm
from .item import Item

class Package(Realm):
    dir: src.SourceDir

    @classmethod
    def from_path(cls, path: str | src.Path) -> Self:
        return cls(dir=src.SourceDir.from_path(path))

    @property
    def source_files(self) -> frozenset[src.SourceFile]:
        return frozenset(self.dir.glob("**/*.ax"))

    @flux.method
    def file_items(self, file: src.SourceFile) -> frozenset[Item]:
        from axis import items
        return frozenset(
            item for item in items.Unit.from_file(file, realm=self)
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
        self.check()
        return flux.collect(Package.check, obj=self, cls=log.Report)
