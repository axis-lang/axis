"""
layouts: 
    - python object: instance of protobase.Object or other python objects (str, float, int, bool, None, Decimal, datetime, timedelta, etc..)
    - frozenjson: frozendict, frozenset, tuple
    - binary: bytes
"""
from __future__ import annotations
from typing import Any
from protobase import Record

class Val(Record, consed=True):
    class Meta(Record, consed=True, abstract=True):
        ...

    meta: Meta
    data: Any

    def get(self, name: str) -> Val:
        "get property"


