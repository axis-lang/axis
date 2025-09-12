from pathlib import Path
from typing import Self
from protobase import Record
from .file import File

class Dir(Record, consed=True):
    """
    Encapsula la logica de watcher de un directorio de codigo fuente.
    observando cuando se agregan nuevos archivos, etc.
    """
    path: Path

    @classmethod
    def from_path(cls, path: Path|str) -> Self:
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")
        return cls(path=path)

    def glob(self, pattern: str) -> frozenset[Path]:
        return frozenset(
            path.relative_to(self.path)
            for path in self.path.glob(pattern)
        )
    
    

    
