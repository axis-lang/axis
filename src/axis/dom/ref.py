"""

Una referencia es un objeto que identifica univocamente un elemento
en el sistema de entidades. El sistema de entidades es un sistema arboreo
donde cada nodo es una entidad y cada entidad puede tener un padre
o un conjunto de hijos. Las entidades pueden ser modulos, funciones,
clases, variables, etc.

Existen dos tipos de referencias:
 - Referencia fisica: tiene como raiz un codebase y se refiere a
    partes de ese codebase. la referencia fisica se maneja en axis.dom.src.
    Las referencias fisicas son objetos que representan elementos
    fisicos (textuales y estructurales) en el codebase.


 - Referencia logica: implementadas en este modulo, hacen referencia al
    istema de entidades


"""

from __future__ import annotations
from pathlib import Path
from typing import ClassVar, Optional, Self
from protobase import Record, cached_property


KNOW_GLOBAL_ANCHORS = {"std", "lib", "com", "org", "man"}


class Ref(Record, abstract=True):
    ROOT: ClassVar[Global]


class Global(Ref, consed=True):
    """
    Referencia a un elemento global en el sistema de entidades,
    se representa prefijada como "@root.std" o "@std"

    el primer elemento de la referencia siempre debe ser un
    namespace y su nombre esta delimitado a elementos conocidos (std, lib).

    """

    class Element(Record, frozen=True, abstract=True): ...

    class Child(Element):
        name: str

    elements: tuple[Element, ...]

    @property
    def parent(self) -> Optional[Self]:
        if not self.elements:
            return None
        return self.__class__(self.elements[:-1])

    def __str__(self) -> str:
        return "@" + ".".join(str(e) for e in self.elements)

    def child(self, name: str) -> Self:
        return self.__class__(self.elements + (self.Child(name),))


ROOT = Ref.ROOT = Global(elements=())
