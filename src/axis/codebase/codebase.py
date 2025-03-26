# %%
from itertools import chain
from pathlib import Path
from protobase import Context, Object, Record
from axis.codebase.srcblock import Parser as SrcBlockParser
from rich import print

SRC_BLOCK_SPEC_FILE = Path("src/axis/codebase/grammar/srcblock-spec.yaml")
TESTS_CODEBASE = Path("src/std.base.tests.src")


class Id(Record, consed=True):  # final = True
    parts: tuple[str]

    @classmethod
    def from_path(cls, path: Path):
        parts = chain.from_iterable(part.split(".") for part in path.parts)
        return cls(parts=tuple(parts)[:-1])

    def __rich__(self):
        return "::".join(self.parts)


class FileSystemLayer(Object, abstract=True):
    fs_path: Path
    fs_glob: str = "**/*.ax"  # Annotated[]

    @property
    def fs_unit_paths(self):
        return {
            Id.from_path(rel_path): path
            for path in self.fs_path.glob(self.fs_glob)
            if (rel_path := path.relative_to(self.fs_path))
        }


class ASTLayer(FileSystemLayer, abstract=True):

    @property
    def ast_srcblock_parser(self) -> SrcBlockParser:
        return SrcBlockParser.from_yaml(SRC_BLOCK_SPEC_FILE)

    def ast_unit(self, unit_id: Id):
        unit_path = self.fs_unit_paths.get(unit_id, None)
        if not unit_path:
            raise ValueError(f"Unit {unit_id} not found")
        unit_content = unit_path.read_text()
        return self.ast_srcblock_parser.parse("unit", unit_content)


class CodeBase(ASTLayer, FileSystemLayer):
    @property
    def cb_id(self):
        return Id(tuple(self.fs_path.name.split(".")[:-1]))


class CodeUnit: ...


if __name__ == "__main__":
    cb = CodeBase(fs_path=TESTS_CODEBASE)

    for unit in cb.fs_unit_paths:
        print(cb.ast_unit(unit))

    # TODO: parsear un unit con un def!
# %%
