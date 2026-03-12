from __future__ import annotations

from typing import ClassVar, cast

from protobase import Consed, Inmutable, _

import protomorph as morph

__all__ = ["ContextProto", "VarType", "Var", "var"]


class ContextProto(Inmutable):
    def lookup_bound(self, name: str) -> morph.Type | None: ...


class VarType[C: ContextProto](morph.Type, abstract=True):
    ctx: C

    ANCHOR: ClassVar[str] = "dom.Var.Type"

    def wrap(self, data: morph.Data) -> morph.Val:
        if not isinstance(data, str):
            raise ValueError(
                f"{type(self).__name__}.wrap expected variable name str, got {type(data).__name__}"
            )
        return Var(self, data)


class Var(morph.Val, morph.Type, Consed):
    __type__: VarType = _
    __data__: str = _

    def _metatype(self) -> VarType:
        return cast(VarType, self.type)


def var[C: ContextProto](var_type_cls: type[VarType[C]], ctx: C, name: str) -> Var:
    return Var(var_type_cls(ctx=ctx), name)
