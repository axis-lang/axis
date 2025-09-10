from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar, Optional
from protobase import Record, frozendict
from axis.core import syn, val, sem
from contextvars import ContextVar

current_context: ContextVar[Optional[Context]] = ContextVar("current_context", default=None)


class Context(Record, frozen=True):
    class Settings(Record, frozen=True):
        pass

    settings: Settings = Settings()

    # codebase_paths: frozenset[Path] | tuple[Path]





