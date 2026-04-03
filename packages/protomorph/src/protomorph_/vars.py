from __future__ import annotations

from typing import ClassVar, cast

from protobase import Consed, Inmutable, _

import protomorph_ as pm

__all__ = [
    "ContextProto",
    "Placeholder",
    "VarType",
    "Var",
    "SystemVarType",
    "AnyType",
    "Any",
    "ANY",
    "THIS",
    "var",
]


class ContextProto(Inmutable):
    def lookup_bound(self, name: str) -> pm.Type | None: ...


class Placeholder(pm.Val, pm.Type, abstract=True):
    def _metatype(self) -> pm.Type:
        return cast(pm.Type, self.__type__)

    def _wrap(self, data: pm.Data) -> pm.Val:
        if data == self.__data__:
            return self
        return type(self)(self.__type__, data)


class VarType[C: ContextProto](pm.Type, abstract=True):
    ctx: ContextProto | None = None

    ANCHOR: ClassVar[str] = "std.types.VarType"

    def _wrap(self, data: pm.Data) -> pm.Val:
        return Var(self, data)


class Var(Placeholder, Consed):
    __type__: VarType = _
    __data__: pm.Data = _

    def _wrap(self, data: pm.Data) -> pm.Val:
        if data != self.__data__:
            raise ValueError(
                f"{type(self).__name__}.wrap expected placeholder data {self.__data__!r}, got {data!r}"
            )
        return self


class SystemVarType(VarType[ContextProto]):
    ANCHOR = "std.types.SystemVarType"


class AnyType(pm.Type):
    ANCHOR: ClassVar[str] = "std.types.AnyPlaceholder"

    def _wrap(self, data: pm.Data) -> pm.Val:
        return Any(self, data)


class Any(Placeholder, Consed):
    __type__: AnyType = _
    __data__: pm.Data = _


ANY = Any(AnyType(), ())
THIS = Var(SystemVarType(), "THIS")


def var[C: ContextProto](
    var_type_cls: type[VarType[C]],
    ctx: C,
    name: str,
) -> Var:
    return Var(cast(VarType, var_type_cls(ctx=ctx)), name)
