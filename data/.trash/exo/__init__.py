#%%
from __future__ import annotations
from typing import Any, Optional, get_type_hints, get_origin
from dataclasses import dataclass

from protobase import Object, traits, fields_of
from exo.tuple import Tuple

class Entity(Object):
    def __eq__(self, other: Any) -> bool:
        return self is other    
    
    def __hash__(self) -> int:
        return id(self)

class Class(Entity):
    class Member(Entity):
        position: int
        name: str
        type: Type

    members: Tuple[Member]


class Type(Object, traits.Consed):
    stereotypes: Tuple[str] # -> attributes
    cls: Class # -> properties

class Val(Object, traits.Consed):
    type: Type
    data: Any


def class_of(tp: type):
    tp = get_origin(tp) or tp
    
    print(tp)
    return Class(
        members=Tuple(
            Class.Member(
                position=i,
                name=nm,
                type=Type(
                    stereotypes=Tuple(),
                    cls=class_of(Any if tp is None else tp)
                )
            )
            for i, (nm, tp) in enumerate(get_type_hints(tp).items())
        )
    )

class_of(Class)


