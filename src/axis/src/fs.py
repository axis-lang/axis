from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import importlib
import os
from pathlib import Path
import time
from typing import Iterable, Mapping, Sequence, cast

from protobase import Inmutable, Object, flux, register_inmutable


__all__ = [
    "FileSystem",
    "PhysicalFileSystem",
    "VirtualFileSystem",
    "FSOverlay",
    "FSStat",
    "TextBuffer",
    "TextDelta",
    "WatchFS",
    "default_fs",
]


class FSStat(Inmutable):
    path: Path
    exists: bool
    is_file: bool
    is_dir: bool
    size: int
    mtime: timedelta


@dataclass
class TextDelta:
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    text: str


class TextBuffer(Object):
    __slots__ = ("text", "mtime", "version", "line_starts")

    text: str
    mtime: timedelta
    version: int | None
    line_starts: list[int]

    def __init__(self, text: str, mtime: timedelta, version: int | None = None) -> None:
        self.text = text
        self.mtime = mtime
        self.version = version
        self.line_starts = _line_starts(text)

    def apply_deltas(self, deltas: Sequence[TextDelta]) -> None:
        if not deltas:
            return
        edits = []
        for delta in deltas:
            start = _offset_at(self.line_starts, delta.start_line, delta.start_col)
            end = _offset_at(self.line_starts, delta.end_line, delta.end_col)
            edits.append((start, end, delta.text))
        edits.sort(key=lambda item: item[0], reverse=True)
        text = self.text
        for start, end, replacement in edits:
            text = text[:start] + replacement + text[end:]
        self.text = text
        self.line_starts = _line_starts(text)


class FileSystem(Object, abstract=True):
    __slots__ = ("__weakref__",)

    __weakref__: object

    def _normalize(self, path: Path | str) -> Path:
        path = Path(path)
        mount_point = getattr(self, "mount_point", None)
        if mount_point is not None and not path.is_absolute():
            path = Path(mount_point) / path
        return path.resolve()

    def _now(self) -> timedelta:
        return timedelta(microseconds=time.time_ns() // 1000)

    @flux.method
    def read_text(self, path: Path | str) -> str:
        raise NotImplementedError

    @flux.method
    def stat(self, path: Path | str) -> FSStat:
        raise NotImplementedError

    @flux.method
    def exists(self, path: Path | str) -> bool:
        raise NotImplementedError

    @flux.method
    def listdir(self, path: Path | str) -> tuple[Path, ...]:
        raise NotImplementedError

    @flux.method
    def glob(self, root: Path | str, pattern: str) -> tuple[Path, ...]:
        root_path = self._normalize(root)
        root_rel = Path(pattern)
        matches: list[Path] = []
        for entry in _walk_tree(cast(FileSystem, self), root_path):
            try:
                rel = entry.relative_to(root_path)
            except ValueError:
                continue
            if rel.match(pattern) or entry.match(str(root_rel)):  # type: ignore[arg-type]
                matches.append(entry)
        return tuple(sorted(matches))

    def _invalidate(self, method_name: str, *args: object) -> None:
        method = getattr(type(self), method_name, None)
        invalidate = getattr(method, "invalidate", None)
        if invalidate is None:
            return
        invalidate(self, *args)

    def invalidate_path(self, path: Path | str) -> None:
        target = self._normalize(path)
        self._invalidate("read_text", target)
        self._invalidate("stat", target)
        self._invalidate("exists", target)
        self._invalidate("listdir", target.parent)

    def invalidate_dir(self, path: Path | str) -> None:
        target = self._normalize(path)
        self._invalidate("listdir", target)


register_inmutable(FileSystem)


class PhysicalFileSystem(FileSystem):
    __slots__ = ("__weakref__", "mount_point", "watcher")

    mount_point: Path
    watcher: "WatchFS | None"

    def __init__(self, mount_point: Path | str = "/") -> None:
        self.mount_point = Path(mount_point)
        self.watcher = None

    def enable_watching(self, root: Path | str, *, backend: str = "watchdog") -> "WatchFS":
        if self.watcher is None:
            self.watcher = WatchFS(self, root, backend=backend)
            self.watcher.start()
        return self.watcher

    def disable_watching(self) -> None:
        if self.watcher is None:
            return
        self.watcher.stop()
        self.watcher = None

    def apply_text(self, path: Path | str, text: str, *, version: int | None = None) -> None:
        target = self._normalize(path)
        target.write_text(text, encoding="utf-8")
        self.invalidate_path(target)

    def apply_deltas(self, path: Path | str, deltas: Sequence[TextDelta], *, version: int | None = None) -> None:
        target = self._normalize(path)
        text = target.read_text(encoding="utf-8")
        buffer = TextBuffer(text, self._now(), version)
        buffer.apply_deltas(deltas)
        target.write_text(buffer.text, encoding="utf-8")
        self.invalidate_path(target)

    def clear_overlay(self, path: Path | str) -> None:
        target = self._normalize(path)
        self.invalidate_path(target)

    @flux.method
    def read_text(self, path: Path | str) -> str:
        target = self._normalize(path)
        return target.read_text(encoding="utf-8")

    @flux.method
    def stat(self, path: Path | str) -> FSStat:
        target = self._normalize(path)
        if not target.exists():
            return _missing_stat(target)
        stat = target.stat()
        return FSStat(
            path=target,
            exists=True,
            is_file=target.is_file(),
            is_dir=target.is_dir(),
            size=stat.st_size,
            mtime=_mtime_from_ns(stat.st_mtime_ns),
        )

    @flux.method
    def exists(self, path: Path | str) -> bool:
        target = self._normalize(path)
        return target.exists()

    @flux.method
    def listdir(self, path: Path | str) -> tuple[Path, ...]:
        target = self._normalize(path)
        if not target.is_dir():
            return ()
        return tuple(sorted(entry for entry in target.iterdir()))


class VirtualFileSystem(FileSystem):
    __slots__ = ("__weakref__", "mount_point", "files")

    def __init__(self, files: dict[Path, TextBuffer] | None = None, *, mount_point: Path | str = "/") -> None:
        self.mount_point = Path(mount_point)
        self.files = files or {}

    @classmethod
    def from_files(cls, files: Mapping[Path | str, str], *, mount_point: Path | str = "/") -> "VirtualFileSystem":
        fs = cls(mount_point=mount_point)
        for path, content in files.items():
            target = fs._normalize(path)
            fs.files[target] = TextBuffer(content, fs._now())
        return fs

    def apply_text(self, path: Path | str, text: str, *, version: int | None = None) -> None:
        target = self._normalize(path)
        buffer = self.files.get(target)
        if buffer is None:
            self.files[target] = TextBuffer(text, self._now(), version)
        else:
            buffer.text = text
            buffer.mtime = self._now()
            buffer.version = version
            buffer.line_starts = _line_starts(text)
        self.invalidate_path(target)
        self.invalidate_dir(target.parent)

    def apply_deltas(self, path: Path | str, deltas: Sequence[TextDelta], *, version: int | None = None) -> None:
        target = self._normalize(path)
        buffer = self.files.get(target)
        if buffer is None:
            raise FileNotFoundError(f"File not found: {target}")
        buffer.apply_deltas(deltas)
        buffer.mtime = self._now()
        buffer.version = version
        self.invalidate_path(target)
        self.invalidate_dir(target.parent)

    def clear_overlay(self, path: Path | str) -> None:
        target = self._normalize(path)
        if target in self.files:
            del self.files[target]
            self.invalidate_path(target)
            self.invalidate_dir(target.parent)

    @flux.method
    def read_text(self, path: Path | str) -> str:
        target = self._normalize(path)
        buffer = self.files.get(target)
        if buffer is None:
            raise FileNotFoundError(f"File not found: {target}")
        return buffer.text

    @flux.method
    def stat(self, path: Path | str) -> FSStat:
        target = self._normalize(path)
        buffer = self.files.get(target)
        if buffer is not None:
            return FSStat(
                path=target,
                exists=True,
                is_file=True,
                is_dir=False,
                size=len(buffer.text),
                mtime=buffer.mtime,
            )
        if _has_descendant(self.files.keys(), target):
            return FSStat(
                path=target,
                exists=True,
                is_file=False,
                is_dir=True,
                size=0,
                mtime=_missing_mtime(),
            )
        return _missing_stat(target)

    @flux.method
    def exists(self, path: Path | str) -> bool:
        target = self._normalize(path)
        return target in self.files or _has_descendant(self.files.keys(), target)

    @flux.method
    def listdir(self, path: Path | str) -> tuple[Path, ...]:
        target = self._normalize(path)
        return tuple(sorted(_children_from_files(self.files.keys(), target)))


class FSOverlay(FileSystem):
    __slots__ = ("__weakref__", "base", "overlay", "prefer_overlay")

    def __init__(self, base: FileSystem, overlay: dict[Path, TextBuffer] | None = None, *, prefer_overlay: bool = False) -> None:
        self.base = base
        self.overlay = overlay or {}
        self.prefer_overlay = prefer_overlay

    def apply_text(self, path: Path | str, text: str, *, version: int | None = None) -> None:
        self._apply_text(path, text, version)

    def apply_deltas(self, path: Path | str, deltas: Sequence[TextDelta], *, version: int | None = None) -> None:
        self._apply_deltas(path, deltas, version)

    def clear_overlay(self, path: Path | str) -> None:
        self._clear_overlay(path)

    def _apply_text(self, path: Path | str, text: str, version: int | None) -> None:
        target = self._normalize(path)
        buffer = self.overlay.get(target)
        if buffer is None:
            buffer = TextBuffer(text, self._now(), version)
            self.overlay[target] = buffer
        else:
            buffer.text = text
            buffer.mtime = self._now()
            buffer.version = version
            buffer.line_starts = _line_starts(text)
        self.invalidate_path(target)
        if target.parent not in self.overlay:
            self.invalidate_dir(target.parent)

    def _apply_deltas(self, path: Path | str, deltas: Sequence[TextDelta], version: int | None) -> None:
        target = self._normalize(path)
        buffer = self.overlay.get(target)
        if buffer is None:
            base_text = self.base.read_text(target)
            buffer = TextBuffer(base_text, self._now(), version)
            self.overlay[target] = buffer
        buffer.apply_deltas(deltas)
        buffer.mtime = self._now()
        buffer.version = version
        self.invalidate_path(target)
        self.invalidate_dir(target.parent)

    def _clear_overlay(self, path: Path | str) -> None:
        target = self._normalize(path)
        if target in self.overlay:
            del self.overlay[target]
            self.invalidate_path(target)
            self.invalidate_dir(target.parent)

    @flux.method
    def read_text(self, path: Path | str) -> str:
        target = self._normalize(path)
        buffer = self.overlay.get(target)
        if buffer is None:
            return self.base.read_text(target)
        if self.prefer_overlay:
            return buffer.text
        base_stat = cast(FSStat, self.base.stat(target))
        if (not base_stat.exists) or buffer.mtime >= base_stat.mtime:
            return buffer.text
        return self.base.read_text(target)

    @flux.method
    def stat(self, path: Path | str) -> FSStat:
        target = self._normalize(path)
        buffer = self.overlay.get(target)
        base_stat = cast(FSStat, self.base.stat(target))
        overlay_stat: FSStat | None = None
        if buffer is not None:
            overlay_stat = FSStat(
                path=target,
                exists=True,
                is_file=True,
                is_dir=False,
                size=len(buffer.text),
                mtime=buffer.mtime,
            )
        if self.prefer_overlay and overlay_stat is not None:
            return overlay_stat
        if overlay_stat is None:
            if not base_stat.exists and _has_descendant(self.overlay.keys(), target):
                return FSStat(
                    path=target,
                    exists=True,
                    is_file=False,
                    is_dir=True,
                    size=0,
                    mtime=_missing_mtime(),
                )
            return base_stat
        if (not base_stat.exists) or overlay_stat.mtime >= base_stat.mtime:
            return overlay_stat
        return base_stat

    @flux.method
    def exists(self, path: Path | str) -> bool:
        target = self._normalize(path)
        if target in self.overlay:
            return True
        if _has_descendant(self.overlay.keys(), target):
            return True
        return bool(self.base.exists(target))

    @flux.method
    def listdir(self, path: Path | str) -> tuple[Path, ...]:
        target = self._normalize(path)
        base_entries = tuple(self.base.listdir(target))
        overlay_entries = _children_from_files(self.overlay.keys(), target)
        entries = set(base_entries)
        entries.update(overlay_entries)
        return tuple(sorted(entries))


class WatchFS(Object):
    __slots__ = ("__weakref__", "fs", "root", "backend", "_observer", "_handler")

    fs: FileSystem
    root: Path
    backend: str

    def __init__(self, fs: FileSystem, root: Path | str, *, backend: str = "watchdog") -> None:
        self.fs = fs
        self.root = Path(root).resolve()
        self.backend = backend
        self._observer = None
        self._handler = None

    def start(self) -> None:
        if self.backend != "watchdog":
            return
        try:
            watchdog_events = importlib.import_module("watchdog.events")
            watchdog_observers = importlib.import_module("watchdog.observers")
            FileSystemEventHandler = getattr(watchdog_events, "FileSystemEventHandler")
            Observer = getattr(watchdog_observers, "Observer")
        except Exception:
            self.backend = "manual"
            return

        class Handler(FileSystemEventHandler):
            def on_created(self, event):
                self._notify(event, "created")

            def on_modified(self, event):
                self._notify(event, "modified")

            def on_deleted(self, event):
                self._notify(event, "deleted")

            def on_moved(self, event):
                self._notify(event, "moved", dest=event.dest_path)

            def _notify(self, event, kind, dest=None):
                if event.is_directory:
                    return
                self.fs_event(kind, event.src_path, dest)

        handler = Handler()
        handler.fs_event = self._notify_event
        observer = Observer()
        observer.schedule(handler, str(self.root), recursive=True)
        observer.start()
        self._observer = observer
        self._handler = handler

    def stop(self) -> None:
        if self._observer is None:
            return
        self._observer.stop()
        self._observer.join()
        self._observer = None
        self._handler = None

    def notify(self, path: Path | str, event: str, dest: Path | str | None = None) -> None:
        self._notify_event(event, path, dest)

    def _notify_event(self, event: str, path: Path | str, dest: Path | str | None = None) -> None:
        source = Path(path)
        if event == "modified":
            self.fs.invalidate_path(source)
        elif event == "created":
            self.fs.invalidate_path(source)
            self.fs.invalidate_dir(source.parent)
        elif event == "deleted":
            self.fs.invalidate_path(source)
            self.fs.invalidate_dir(source.parent)
        elif event == "moved":
            self.fs.invalidate_path(source)
            self.fs.invalidate_dir(source.parent)
            if dest is not None:
                dest_path = Path(dest)
                self.fs.invalidate_path(dest_path)
                self.fs.invalidate_dir(dest_path.parent)


_DEFAULT_FS: FSOverlay | None = None


def default_fs() -> FSOverlay:
    global _DEFAULT_FS
    if _DEFAULT_FS is None:
        _DEFAULT_FS = FSOverlay(PhysicalFileSystem())
    return _DEFAULT_FS


def _missing_mtime() -> timedelta:
    return timedelta(0)


def _missing_stat(path: Path) -> FSStat:
    return FSStat(
        path=path,
        exists=False,
        is_file=False,
        is_dir=False,
        size=0,
        mtime=_missing_mtime(),
    )


def _mtime_from_ns(ns: int) -> timedelta:
    return timedelta(microseconds=ns // 1000)


def _line_starts(text: str) -> list[int]:
    return [0] + [i for i, ch in enumerate(text, 1) if ch == "\n"]


def _offset_at(line_starts: list[int], line_no: int, col_no: int) -> int:
    if line_no < 0 or line_no >= len(line_starts):
        raise IndexError(f"Line {line_no} out of range")
    start = line_starts[line_no]
    return start + col_no


def _walk_tree(fs: FileSystem, root: Path) -> Iterable[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        entries = fs.listdir(current)
        for entry in entries:
            yield entry
            try:
                stat = fs.stat(entry)
                if stat is not None and stat.is_dir:
                    stack.append(entry)
            except Exception:
                continue


def _has_descendant(paths: Iterable[Path], root: Path) -> bool:
    for path in paths:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        if path != root:
            return True
    return False


def _children_from_files(paths: Iterable[Path], root: Path) -> set[Path]:
    children: set[Path] = set()
    for path in paths:
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel.parts:
            children.add(root / rel.parts[0])
    return children
