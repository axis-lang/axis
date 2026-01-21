# %%

from types import GenericAlias, MemberDescriptorType
from typing import Any, Callable, Literal, Self, overload
from .type import Type

class cached_property[T](Type.SlotMember):

    def slotname(self, owner_name: str, name: str) -> str:
        return f"_{owner_name}__{name}"

    def __init__(self, func: Callable[..., T]):
        self.func = func
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    _slotname: str
    _slotdescriptor: MemberDescriptorType

    def __set_name__(self, owner, name):
        slotname = self.slotname(owner.__name__, name)

        if hasattr(self, "_slotname") and self._slotname != slotname:
            raise TypeError(
                f"Cannot assign the same {type(self)} to two different names "
                f"({self._slotname!r} and {slotname!r})."
            )
        self._slotname = slotname
        #self._slotdescriptor = getattr(owner, slotname)

    @overload
    def __get__(self, instance, owner: Literal[None]) -> Self: ...

    @overload
    def __get__(self, instance, owner: Any) -> T: ...

    def __get__(self, instance, owner=None) -> Self | T:
        if instance is None:
            return self

        if not hasattr(self, "_slotname"):
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )

        if not hasattr(instance, self._slotname):
            val = self.func(instance)
            try:
                #self._slotdescriptor.__set__(instance, val)
                slotdescriptor = getattr(owner, self._slotname)
                slotdescriptor.__set__(instance, val)
            except TypeError:
                msg = f"Cannot cache the result of {self.func.__name__!r}"
                raise TypeError(msg) from None

        return getattr(instance, self._slotname)

    __class_getitem__ = classmethod(GenericAlias)
