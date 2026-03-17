from __future__ import annotations

from typing import ClassVar, cast

from protobase import Consed, Inmutable, _

import protomorph as pm

__all__ = ["ContextProto", "VarType", "Var", "var"]


class ContextProto(Inmutable):
    def lookup_bound(self, name: str) -> pm.Type | None: ...


class VarType[C: ContextProto](pm.Type, abstract=True):
    ctx: C

    ANCHOR: ClassVar[str] = "std.types.VarType"

    def _wrap(self, data: pm.Data) -> pm.Val:
        if not isinstance(data, str):
            raise ValueError(
                f"{type(self).__name__}.wrap expected variable name str, got {type(data).__name__}"
            )
        return Var(self, data)


class Var(pm.Val, pm.Type, Consed):
    __type__: VarType = _
    __data__: str = _

    def _metatype(self) -> VarType:
        return cast(VarType, self.__type__)

    def _wrap(self, data: pm.Data) -> pm.Val:
        if not isinstance(data, str):
            raise ValueError(
                f"{type(self).__name__}.wrap expected variable name str, got {type(data).__name__}"
            )
        if data != self.__data__:
            raise ValueError(
                f"{type(self).__name__}.wrap expected variable name {self.__data__!r}, got {data!r}"
            )
        return self



def var[C: ContextProto](var_type_cls: type[VarType[C]], ctx: C, name: str) -> Var:
    return Var(var_type_cls(ctx=ctx), name)
