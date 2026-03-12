from __future__ import annotations

from typing import ClassVar, TYPE_CHECKING
from weakref import WeakValueDictionary

from .derived import derived
from .inmutable import Inmutable
from .record import impl_consed_new_method
from .type import Type

__all__ = ["Consed"]


class Consed(Inmutable, abstract=True):
    __consign__: ClassVar[WeakValueDictionary]

    @staticmethod
    def __class_build__(bld: Type.Builder):
        @bld.postbuild
        def post(cls):
            if not cls.__isabstract__:
                cls.__consign__ = WeakValueDictionary()

    if not TYPE_CHECKING:

        @derived(impl_consed_new_method)
        def __new__(cls, *args, **kwargs): ...
