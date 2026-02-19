from __future__ import annotations

from typing import Optional

from protobase import Record

from axis import syn


class SlotShape(Record, frozen=True):
    name: Optional[str]
    pos: int
    bound: Optional[syn.Expr] = None


class TupleShape(Record, frozen=True):
    slots: tuple[SlotShape, ...]
