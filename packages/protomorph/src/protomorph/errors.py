from __future__ import annotations

from protobase import _, Consed

import protomorph as morph

__all__ = ["ErrType", "Err"]


class ErrType(morph.Type):
    ANCHOR = "dom.Err.Type"

    def _wrap(self, data: morph.Data) -> morph.Val:
        return Err(self, data)


class Err(morph.Val, Consed):
    __type__: ErrType = ErrType()
    __data__: morph.Data | None = None
