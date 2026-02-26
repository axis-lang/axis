# %%

from types import GenericAlias
from typing import Any, Callable, Generic, Literal, Self, TypeVar, overload
from weakref import WeakKeyDictionary

from .object import slots_of
from .type import Type


def _has_weakref_slot(owner: type) -> bool:
    slots = slots_of(owner)
    return "__weakref__" in slots


T = TypeVar("T")


class slot_cached_property(Generic[T], Type.SlotMember):

    def slotname(self, owner_name: str, name: str) -> str:
        return f"_{owner_name}__{name}"

    def __init__(self, func: Callable[..., T]):
        self.func = func
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    _slotname: str

    def __set_name__(self, owner, name):
        slotname = self.slotname(owner.__name__, name)

        if hasattr(self, "_slotname") and self._slotname != slotname:
            raise TypeError(
                f"Cannot assign the same {type(self)} to two different names "
                f"({self._slotname!r} and {slotname!r})."
            )
        self._slotname = slotname

    @overload
    def __get__(self, instance: None, owner: Any) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: Any) -> T: ...

    def __get__(self, instance, owner=None) -> Self | T:
        if instance is None:
            return self

        if not hasattr(self, "_slotname"):
            raise TypeError(
                "Cannot use slot_cached_property instance without calling __set_name__ on it."
            )

        if not hasattr(instance, self._slotname):
            val = self.func(instance)
            try:
                slotdescriptor = getattr(owner, self._slotname)
                slotdescriptor.__set__(instance, val)
            except TypeError:
                msg = f"Cannot cache the result of {self.func.__name__!r}"
                raise TypeError(msg) from None

        return getattr(instance, self._slotname)

    __class_getitem__ = classmethod(GenericAlias)


class cached_property(Generic[T]):
    def __init__(self, func: Callable[..., T]):
        self.func = func
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__
        self._cache: WeakKeyDictionary[object, T] = WeakKeyDictionary()

    def __set_name__(self, owner, name):
        if not _has_weakref_slot(owner):
            raise TypeError(
                f"cached_property requires {owner.__qualname__} to define '__weakref__' in __slots__"
            )

    @overload
    def __get__(self, instance: None, owner: Any) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: Any) -> T: ...

    def __get__(self, instance, owner=None) -> Self | T:
        if instance is None:
            return self
        try:
            return self._cache[instance]
        except KeyError:
            value = self.func(instance)
            self._cache[instance] = value
            return value

    __class_getitem__ = classmethod(GenericAlias)
