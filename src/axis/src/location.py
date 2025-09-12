from typing import Self
from protobase import Record
from pathlib import Path

class Loc(Record, consed=True, abstract=True):
    ...

class Codebase(Loc):
    '''
    Un codebase puede ser un directorio el un archivo zip. cuando se trata de un archivo zip
    el nombre del archivo contiene la version del codebase. dentro del codebase se 
    encuentra un archivo codebase.toml que contiene la version del codebase y el nombre
    del codebase asi como las dependencias.
    cuando el codebase se almacena en formato zip, a su lado tambien se encontrará el 
    archivo con el mismo nombre con la extension .axis-vXX.YY.ZZ.cache
    '''
    path: Path

    @classmethod
    def from_path(cls, path: Path) -> Self:
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a directory")
        return cls(path=path)


class Unit(Loc):
    parent: Codebase
    path: Path

    @property
    def rel_path(self):
        return self.path.relative_to(self.parent.path)

    def __repr__(self):
        return f"ref.Mod({self.rel_path})"
