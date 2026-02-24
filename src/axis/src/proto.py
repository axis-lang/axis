from __future__ import annotations

from pathlib import Path
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .fs import FSStat

from protobase import register_inmutable


class FileSystem(Protocol):
    def read_text(self, path: Path | str) -> str: ...
    def stat(self, path: Path | str): ...

    def exists(self, path: Path | str) -> bool: ...

    def listdir(self, path: Path | str) -> tuple[Path, ...]: ...

    def glob(self, root: Path | str, pattern: str) -> tuple[Path, ...]: ...

    def apply_text(self, path: Path | str, text: str, *, version: int | None = None) -> None: ...

    def apply_deltas(self, path: Path | str, deltas, *, version: int | None = None) -> None: ...

    def clear_overlay(self, path: Path | str) -> None: ...


class FileLike(Protocol):
    path: Path
    fs: FileSystem

    @property
    def content(self) -> str: ...

    def position_at_offset(self, offset: int): ...


class DirLike(Protocol):
    path: Path
    fs: FileSystem


class SpanLike(Protocol):
    file: FileLike
    start: int
    end: int


register_inmutable(FileSystem, FileLike, DirLike, SpanLike)
