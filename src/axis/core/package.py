from __future__ import annotations
from pathlib import Path
from typing import ClassVar
from protobase import Record
from axis.core import src, syn

# package definira sus propios s
# SRC_GLOB: str = "**/*.ax"


class Package(Record, frozen=True, abstract=True):  # src.Dir?
    path: Path
    file_types: ClassVar[dict[str, syn.Item]]  # {'**./*.ax': syn.Unit, ...}

    @property
    def abs_path(self) -> Path:
        return self.path.resolve()

    class FileEntry(Record, frozen=True):
        pkg: Package
        rel_path: Path
        item_cls: syn.Item

    @property
    def file_entries(self) -> frozenset[src.File]:
        return frozenset(
            self.FileEntry(
                pkg=self,
                rel_path=path.relative_to(self.abs_path),
                item_cls=item_cls,
            )
            for ext, item_cls in self.file_types.items()
            for path in self.abs_path.glob(f'**/*.{ext}')
        )

    

    # file = src.File.from_path("codebase/std-core.tests.src/test.ax")

    # # Parsing step
    # ol = std.Unit.build_ouline_spec()
    # unit = ol.parse_outline(file)

    @property
    def unit_outline_spec(self):
        ol = std.Unit.build_ouline_spec()

    def ast_of_unit(self, src_file: src.File) -> syn.Unit:
        return self.unit_outline_spec.parse_outline(src_file)
        # return outline.transform(syn.outline_transform_fn)
