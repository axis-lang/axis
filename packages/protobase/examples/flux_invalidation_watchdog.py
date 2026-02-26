import os
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from protobase import Inmutable, flux


class File(Inmutable):
    path: Path

    @flux.property
    def stat(self) -> os.stat_result | None:
        try:
            return self.path.stat()
        except FileNotFoundError:
            return None

    @flux.property
    def content(self) -> str:
        stat = self.stat
        if stat is None:
            return ""
        return self.path.read_text(encoding="utf-8")


class _FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_obj: File) -> None:
        self.file_obj = file_obj
        self._target = file_obj.path.resolve(strict=False)

    def _matches(self, path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> bool:
        return Path(os.fsdecode(path)).resolve(strict=False) == self._target

    def _invalidate(self) -> None:
        File.stat.invalidate(self.file_obj)

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        if self._matches(event.src_path):
            self._invalidate()

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        if self._matches(event.src_path):
            self._invalidate()

    def on_deleted(self, event) -> None:
        if event.is_directory:
            return
        if self._matches(event.src_path):
            self._invalidate()

    def on_moved(self, event) -> None:
        if event.is_directory:
            return
        if self._matches(event.src_path) or self._matches(event.dest_path):
            self._invalidate()


def watch_file(file_obj: File) -> BaseObserver:
    handler = _FileChangeHandler(file_obj)
    observer = Observer()
    parent_dir = file_obj.path.parent.resolve(strict=False)
    observer.schedule(handler, str(parent_dir), recursive=False)
    observer.start()
    return observer


def main() -> None:
    file_obj = File(path=Path("data.txt"))

    observer = watch_file(file_obj)

    try:
        while True:
            time.sleep(1.0)
            stat = file_obj.stat
            mtime = None if stat is None else stat.st_mtime
            print("mtime:", mtime, "content:", file_obj.content)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
