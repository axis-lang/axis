from __future__ import annotations

from typing import NewType

from protobase import Consed

Id = NewType("Id", str)
Anchor = NewType("Anchor", str)

_RECONSTRUCT = object()


class Builtin(Consed, abstract=True): ...
