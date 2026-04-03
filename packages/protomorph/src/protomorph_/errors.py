from __future__ import annotations

from protobase import _, Consed

import protomorph_ as pm

__all__ = ["ErrType", "Err"]


class ErrType(pm.Type):
    ANCHOR = "std.types.ErrType"

    def _wrap(self, data: pm.Data) -> pm.Val:
        return Err(self, data)


class Err(pm.Val, Consed):
    __type__: ErrType = ErrType()
    __data__: pm.Data | None = None
