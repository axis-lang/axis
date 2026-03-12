from __future__ import annotations

from protobase import _
from protobase import Consed

from axis import dom


class ErrType(dom.Type):
    ANCHOR = "dom.Err.Type"

    def wrap(self, data: dom.Data) -> dom.Val:
        return Err(type=self, data=data)


class Err(dom.Val, Consed):
    type: ErrType = ErrType()
    data: dom.Data | None = None
