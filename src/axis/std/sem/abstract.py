from __future__ import annotations
from typing import Any, Optional, Protocol, Self
from weakref import ref
from protobase import Object

from axis.std.core import Id

class Context(Protocol):
    def get(self, name: str) -> Entry | None:
        """
        Get a semantic entity by name.
        """
"""
def Copy
# copy trait
    fn Self.copy() { -> Self }
where:
    val Self: Type

"""


class Entry(Object, abstract=True):
    '''
    A entry of a semantic context (Node)
        sem.VarEntry
        sem.Gen
        sem.Local
        sem.Global
        sem.-
    '''
    name: str
    value: Any


class Node(Object, abstract=True):
    '''
    A semantic node  (unit, def, etc..)
    sem.UnitNode
    sem.DefNode
    sem.ValNode
    sem.FnNode
    '''
    __slots__ = ('__weakref__', )

    id: Id
    parent: Optional[Self]

    entries: dict[str, Entry]

    def get(self, name: str) -> Entry | None:
        entry = self.entries.get(name, None)
        
        if entry is not None:
            return entry

        if self.parent is not None:
            return self.parent.get(name)

        return None


class Graph(Object):
    '''
    A semantic graph (a instance for codebase, dynamically created from the ast)
    '''
    __slots__ = ('__weakref__', )

    nodes: dict[Id, Node]


