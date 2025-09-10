from pathlib import Path
from typing import Self
from protobase import Record

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

    # @property
    # def file_entries(self) -> frozenset[src.File]:
    #     return frozenset(
    #         self.FileEntry(
    #             rel_path=path.relative_to(self.abs_path),
    #             item_cls=item_cls,
    #         )
    #         for ext, item_cls in self.file_types.items()
    #         for path in self.abs_path.glob(f'**/*.{ext}')
    #     )
