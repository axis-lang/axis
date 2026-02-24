from pathlib import Path
from typing import Self

from protobase import Record

from .fs import FileSystem, default_fs

class Dir(Record, consed=True):
    """
    Encapsula la logica de watcher de un directorio de codigo fuente.
    observando cuando se agregan nuevos archivos, etc.
    """
    path: Path
    fs: FileSystem = default_fs()

    @classmethod
    def from_path(cls, path: Path|str, *, fs: FileSystem | None = None) -> Self:
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")
        return cls(path=path, fs=fs or default_fs())

    def glob(self, pattern: str) -> frozenset[Path]:
        return frozenset(
            path.relative_to(self.path)
            for path in self.fs.glob(self.path, pattern)
        )
    
    

    
