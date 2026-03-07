from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Self

from protobase import Consed, Object, flux

__all__ = ["SourceFile", "SourceDir", "FSWatcher"]

from .source import Source


class SourceFile(Consed, Source):
    path: Path
    source_dir: "SourceDir"

    @property
    def name(self) -> str:
        return self.path.name

    def __str__(self) -> str:
        return str(self.path)

    @flux.property  # type: ignore[override]
    def content(self) -> str:
        return (self.source_dir.path / self.path).read_text(encoding="utf-8")


class SourceDir(Consed):
    path: Path

    @classmethod
    def from_path(cls, path: Path | str) -> Self:
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        if not path.is_dir():
            raise NotADirectoryError(f"Path {path} is not a directory")
        return cls(path=path)

    @property
    def name(self) -> str:
        return self.path.name

    @flux.method
    def glob(self, pattern: str) -> frozenset[SourceFile]:
        matches: list[SourceFile] = []
        for path in self.path.glob(pattern):
            if not path.is_file():
                continue
            try:
                rel = path.relative_to(self.path)
            except ValueError:
                continue
            matches.append(SourceFile(path=rel, source_dir=self))
        return frozenset(matches)


class FSWatcher(Object):
    __slots__ = ("__weakref__", "root", "_observer", "_handler", "_callbacks")

    root: SourceDir

    def __init__(self, root: SourceDir) -> None:
        self.root = root
        self._observer = None
        self._handler = None
        self._callbacks: list[Callable[[], None]] = []

    def on_change(self, func: Callable[[], None]) -> Callable[[], None]:
        self._callbacks.append(func)
        return func

    def start(self) -> None:
        try:
            import watchdog.events as watchdog_events
            import watchdog.observers as watchdog_observers
        except Exception as exc:
            raise RuntimeError("watchdog is required for --watch") from exc

        FileSystemEventHandler = getattr(watchdog_events, "FileSystemEventHandler")
        Observer = getattr(watchdog_observers, "Observer")

        watch = self

        class Handler(FileSystemEventHandler):
            def on_created(self, event):
                watch._notify_event("created", event.src_path, None, event.is_directory)

            def on_modified(self, event):
                watch._notify_event(
                    "modified", event.src_path, None, event.is_directory
                )

            def on_deleted(self, event):
                watch._notify_event("deleted", event.src_path, None, event.is_directory)

            def on_moved(self, event):
                watch._notify_event(
                    "moved", event.src_path, event.dest_path, event.is_directory
                )

        handler = Handler()
        observer = Observer()
        observer.schedule(handler, str(self.root.path), recursive=True)
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

    def _notify_event(
        self,
        event: str,
        path: Path | str | bytes,
        dest: Path | str | bytes | None = None,
        is_dir: bool = False,
    ) -> None:
        if is_dir:
            SourceDir.glob.invalidate_for(self.root)
            for callback in tuple(self._callbacks):
                callback()
            return

        self._invalidate_file(path)
        if dest is not None:
            self._invalidate_file(dest)

        if event in {"created", "deleted", "moved"}:
            SourceDir.glob.invalidate_for(self.root)

        for callback in tuple(self._callbacks):
            callback()

    def _invalidate_file(self, path: Path | str | bytes) -> None:
        if isinstance(path, bytes):
            path = path.decode()
        target = Path(path).resolve()
        try:
            rel = target.relative_to(self.root.path)
        except ValueError:
            return
        file = SourceFile(path=rel, source_dir=self.root)
        SourceFile.content.invalidate(file)
