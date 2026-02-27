from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from weakref import WeakKeyDictionary, ref

from .inmutable import Inmutable
from .type import Type

__all__ = ["Consed"]


class Consed(Inmutable, abstract=True):
    __consign__: ClassVar[WeakKeyDictionary]

    @staticmethod
    def __class_build__(bld: Type.Builder):
        @bld.postbuild
        def post(cls):
            if not cls.__isabstract__:
                cls.__consign__ = WeakKeyDictionary()

    if not TYPE_CHECKING:
        def __new__(cls, *args, **kwargs):
            self = super().__new__(cls, *args, **kwargs)
            try:
                return cls.__consign__.setdefault(self, ref(self))()
            except TypeError as exc:
                raise ValueError(f"Cannot hash-consed object {self}") from exc
