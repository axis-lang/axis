from __future__ import annotations

from typing import Optional

from protobase import Inmutable

from axis import syn


class RefShape(Inmutable):
    segments: tuple[str, ...]
    params_exprs: tuple = ()
    scope: Optional["RefShape"] = None
