from __future__ import annotations

from .builtin import Builtin as _Builtin


class Spread[V](_Builtin):
    values: tuple[V, ...]
