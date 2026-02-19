from __future__ import annotations

from typing import Optional

from protobase import Record

from axis import syn


class RefShape(Record, frozen=True):
    segments: tuple[str, ...]
    params_exprs: tuple = ()
    scope: Optional["RefShape"] = None
