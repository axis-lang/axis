"""

Una referencia es un objeto que identifica univocamente un elemento
en el sistema de entidades. El sistema de entidades es un sistema arboreo
donde cada nodo es una entidad y cada entidad puede tener un padre
o un conjunto de hijos. Las entidades pueden ser modulos, funciones,
clases, variables, etc.

Existen dos tipos de referencias:
 - Referencia fisica: tiene como raiz un codebase y se refiere a
    partes de ese codebase. la referencia fisica se maneja en axis.core.src.
    Las referencias fisicas son objetos que representan elementos
    fisicos (textuales y estructurales) en el codebase.


 - Referencia logica: implementadas en este modulo, hacen referencia al
    istema de entidades


"""

from __future__ import annotations
from typing import ClassVar, Optional, Self
from protobase import Record, cached_property
from axis.core import val, syn

KNOW_GLOBAL_ANCHORS = {"std", "lib", "com", "org", "man"}


class Ref(val.Value, Record, abstract=True):
    ROOT: ClassVar[Global]

#@classvar('ROOT', of=Ref)
class Global(Ref, consed=True):
    """
    Referencia a un elemento global en el sistema de entidades,
    se representa prefijada como "@root.std" o "@std"

    el primer elemento de la referencia siempre debe ser un
    namespace y su nombre esta delimitado a elementos conocidos (std, lib).

    """
    path: tuple[str, ...]

    def __str__(self) -> str:
        return "@" + ".".join(str(e) for e in self.elements)

    def member(self, name: str) -> Self:
        return self.__class__(self.elements + (self.Child(name),))

    @property
    def parent(self) -> Optional[Self]:
        if not self.elements:
            return None
        return self.__class__(self.elements[:-1])

ROOT = Ref.ROOT = Global(path=())



class GlobalEvaluator(val.Evaluator[Global]):
    """
    Evaluador de referencias globales
    """
    base = Ref.ROOT
    def eval(self, node: syn.Statement) -> Global:
        if isinstance(node, syn.Sym):
            return self.base.member(node.name)
        return super().eval(node)
