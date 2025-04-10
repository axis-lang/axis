# %%
from pathlib import Path

from rich import print

from axis.codebase.ast import ASTLayer
from axis.codebase.filesystem import FileSystemLayer
from axis.std.core import Id
from protobase import Record, cached_property


class CodeBase(ASTLayer, FileSystemLayer, Record, consed=True):
    """
    Un codebase es consed esto es para resolver el arbol de
    dependencias de multiples codebases sin diplicar la informacion.
    """

    @cached_property
    def id(self):
        return Id(tuple(self.fs_path.name.split(".")[:-1]))


if __name__ == "__main__":

    cb = CodeBase(fs_path=Path("src/std.base.tests.src"))

    for unit in cb.fs_unit_paths:
        print(cb.ast_unit(unit)[1])


# %%
