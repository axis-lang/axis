
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from re import Pattern
from types import GenericAlias, UnionType
from typing import Self, get_args, get_origin, Union, TypeVar


_INMUTABLE_TYPES: set[type] = {
    type,
    type(None),
    type(...),
    #type(attrs_of),  # function type is accepted as inmutable
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
    for base in cls.__mro__:
        if base in _INMUTABLE_TYPES:
            return True
    return False


def check_inmutable(tp: GenericAlias | type):
    if tp in (Self, Ellipsis):
        return # a priori lo damos por bueno

    if(tp is type):
        return True

    if isinstance(tp, type):

        if not is_inmutable(tp):
            raise TypeError(f"Type '{tp}' is not a know inmutable.")
        return

    if isinstance(tp, TypeVar):
        if tp.__bound__ is not None:
            check_inmutable(tp.__bound__)
        if tp.__constraints__:
            for constraint in tp.__constraints__:
                check_inmutable(constraint)
        return

    # if isinstance(tp, GenericAlias):
    #     check_inmutable(get_origin(tp))
    #     for arg in get_args(tp):
    #         check_inmutable(arg)
    #     return
    
    if isinstance(tp, UnionType) or get_origin(tp) is Union:
        for arg in get_args(tp):
            check_inmutable(arg)
        return
    
    
    origin = get_origin(tp)
    if origin is type:
        return
    
    check_inmutable(origin)

    for arg in get_args(tp):
        check_inmutable(arg)

    #raise TypeError(f"Can not determine inmutability for '{tp}' of type '{type(tp)}'")
    