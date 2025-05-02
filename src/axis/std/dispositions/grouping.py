"""
la disposicion de grupo


group(key={it.name}, value={it.value}) ->



"""
from __future__ import annotations
from typing import Callable, Union
from protobase import Record, frozendict

class disposition(Record, frozen=True):
    ordering: bool = True

class group[K,V,T](disposition):
    by: Callable[[T], K]
    map: Callable[[T], V]

class Group[K, V](Record, abstract=True):
    """ """
    _inner: Union[
        dict[K, set[V]],
        frozendict[K, frozenset[V]],
    ]

    @classmethod
    def mut(cls) -> MutGroup[K, V]:
        """ """
        return MutGroup()

class MutGroup[K, V](Group[K, V], frozen=False):
    _inner: dict[K, set[V]]

class FrozenGroup[K, V](Group[K, V], frozen=True):
    _inner: frozendict[K, frozenset[V]]

class ConsedGroup[K, V](FrozenGroup[K, V], consed=True):
    _inner: frozendict[K, frozenset[V]]

