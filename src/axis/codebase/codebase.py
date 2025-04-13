# %%
from pathlib import Path

from rich import print

from axis.codebase.sem import SemanticLayer
from axis.codebase.syn import SyntacticLayer
from axis.codebase.fs import FileSystemLayer
from axis.std.core import Id
from protobase import Record, cached_property, Type


class CodeBase(SemanticLayer, SyntacticLayer, FileSystemLayer, Record):
    """
    Un codebase es consed esto es para resolver el arbol de
    dependencias de multiples codebases sin diplicar la informacion.
    """



if __name__ == "__main__":

    cb = CodeBase(fs_path=Path("src/std.base.tests.src"))

    for unit in cb.fs_units:
        print(cb.ast_of_unit(unit))


# %%
