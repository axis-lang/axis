
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from inspect import getattr_static
from pathlib import Path
from re import Pattern
from types import GenericAlias, UnionType, GetSetDescriptorType, MemberDescriptorType
from typing import Any, ForwardRef, Self, cast, get_args, get_origin, Union, TypeAliasType, TypeVar, TYPE_CHECKING

from .derived import derived
from .object import attr_info_of
from .record import Record, impl_hash_method
from .type import Type

__all__ = [
    "Inmutable",
    "check_inmutable",
    "inmutable",
    "is_inmutable",
    "register_inmutable",
]


_INMUTABLE_TYPES: set[type] = {
    type,
    type(None),
    type(...),
    #type(lambda: None), # function es inmutable, 
    bool,
    int,
    float,
    bytes,
    str,
    tuple,
    frozenset,
    Decimal,
    Pattern,
    Path,
    datetime,
    date,
    timedelta,
    Enum,
}

def register_inmutable(*types: type):
    _INMUTABLE_TYPES.update(types)

def inmutable(cls: type):
    _INMUTABLE_TYPES.add(cls)
    return cls



def is_inmutable(cls: type) -> bool:
    """
    Check if a class is immutable.

    Args:
        cls (type): The class to check.

    Returns:
        bool: True if the class is immutable, False otherwise.

    Example:
        >>> is_inmutable(int)
        True
        >>> is_inmutable(str)
        True
        >>> is_inmutable(list)
        False
        >>> is_inmutable(dict)
        False
    """
    if cls is None:
        return False

    for base in reversed(cls.__mro__):
        if base in _INMUTABLE_TYPES:
            return True
    return False


def check_inmutable(tp: object, _seen_aliases: set[TypeAliasType] | None = None):
    if _seen_aliases is None:
        _seen_aliases = set()

    if isinstance(tp, TypeAliasType):
        if tp in _seen_aliases:
            return
        _seen_aliases.add(tp)
        tp = tp.__value__

    if isinstance(tp, ForwardRef):
        return

    if isinstance(tp, str):
        return

    if tp in (Self, Ellipsis):
        return # a priori lo damos por bueno

    if tp is type:
        return True


    if isinstance(tp, TypeVar):
        if tp.__bound__ is not None:
            check_inmutable(tp.__bound__, _seen_aliases)
        if tp.__constraints__:
            for constraint in tp.__constraints__:
                check_inmutable(constraint, _seen_aliases)
        return

    # if isinstance(tp, GenericAlias):
    #     check_inmutable(get_origin(tp))
    #     for arg in get_args(tp):
    #         check_inmutable(arg)
    #     return
    
    if isinstance(tp, UnionType) or get_origin(tp) is Union:
        for arg in get_args(tp):
            check_inmutable(arg, _seen_aliases)
        return
    
    
    if isinstance(tp, type):
        if not is_inmutable(tp):
            raise TypeError(f"Type '{tp}' is not a know inmutable.")
        return

    tp_any = cast(Any, tp)
    origin = get_origin(tp)
    if origin is None:
        origin = getattr(tp_any, "__origin__", None)
    if origin is None:
        raise TypeError(f"Type '{tp}' is not a know inmutable.")

    if isinstance(origin, TypeAliasType):
        check_inmutable(origin, _seen_aliases)
        return

    if not isinstance(origin, type):
        raise TypeError(f"Type '{tp}' is not a know inmutable.")

    origin_type = cast(type, origin)
    if not is_inmutable(origin_type):
        raise TypeError(f"Type '{tp}' is not a know inmutable.")
    
    #check_inmutable(origin)

    args = get_args(tp)
    if not args:
        args = getattr(tp_any, "__args__", None) or ()

    for arg in args:
        check_inmutable(arg, _seen_aliases)

    #raise TypeError(f"Can not determine inmutability for '{tp}' of type '{type(tp)}'")


_FROZEN_SET_BLOCKLIST = (MemberDescriptorType, GetSetDescriptorType)


def _frozen_setattr(self, name, value):
    descriptor = getattr_static(self.__class__, name, None)
    if descriptor is not None and not isinstance(descriptor, _FROZEN_SET_BLOCKLIST):
        set_method = getattr(descriptor, "__set__", None)
        if set_method is not None:
            set_method(self, value)
            return
    raise AttributeError(
        f"Can't set attribute {name!r} on {self.__class__.__name__!r} object is frozen"
    )


class Inmutable(Record, abstract=True):
    @staticmethod
    def __class_build__(bld: Type.Builder):
        bld.add_slots("__hash_cache__")

        @bld.postbuild
        def post(cls):
            cls.__setattr__ = _frozen_setattr
            register_inmutable(cls)

    @classmethod
    def __class_check__(cls):
        inmutability_errors = []

        for nm, attr in attr_info_of(cls).items():
            try:
                check_inmutable(attr.type)
            except TypeError as exc:
                exc.add_note(
                    f"Attribute {nm!r} of {cls.__name__!r} is not inmutable"
                )
                inmutability_errors.append(exc)

        if inmutability_errors:
            raise ExceptionGroup(
                f"Errors in inmutability of {cls.__name__!r}",
                inmutability_errors,
            )

    if not TYPE_CHECKING:
        @derived(impl_hash_method)
        def __structural_hash__(self): ...

        def __hash__(self):
            cache = getattr(self, "__hash_cache__", None)
            if cache is not None:
                return cache
            hash_value = self.__structural_hash__()
            object.__setattr__(self, "__hash_cache__", hash_value)
            return hash_value

        def __copy__(self):
            return self

        def __deepcopy__(self, memo):
            return self
    
