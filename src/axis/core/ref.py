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
from functools import singledispatchmethod
from typing import ClassVar, Optional, Self
from protobase import Record, cached_property
from axis.core import val, syn

#KNOW_GLOBAL_ANCHORS = {"std", "lib", "com", "org", "man"}


class Ref(val.Value, Record, consed=True):


    class Part(Record, frozen=True): ...

    # class Root(Part):
    #     name: str = "root"
    #     def __str__(self) -> str:
    #         return "@"

    class Member(Part):
        name: str
        def __str__(self) -> str:
            return self.name
        
    # class Index(Part):
    #     indices: ...

    root: ClassVar[Ref]    
    parts: tuple[Part, ...]

    def __str__(self):
        if not self.parts:
            return "@root"
        return "@" + ".".join(str(p) for p in self.parts)

    def member(self, name: str) -> Self:
        return self.__class__(self.parts + (self.Member(name),))
    
    @property
    def parent(self) -> Optional[Self]:
        if not self.parts:
            return None
        return self.__class__(self.parts[:-1])

    # @cached_property
    # def is_primary_global(self) -> bool:
    #     ...

Ref.root = Ref(parts=())


# #@classvar('ROOT', of=Ref)
# class Global(Ref, consed=True):
#     """
#     Referencia a un elemento global en el sistema de entidades,
#     se representa prefijada como "@root.std" o "@std"

#     el primer elemento de la referencia siempre debe ser un
#     namespace y su nombre esta delimitado a elementos conocidos (std, lib).

#     """
#     path: tuple[str, ...]

#     def __str__(self) -> str:
#         return "@" + ".".join(str(e) for e in self.elements)

#     def member(self, name: str) -> Self:
#         return self.__class__(self.elements + (self.Child(name),))

#     @property
#     def parent(self) -> Optional[Self]:
#         if not self.elements:
#             return None
#         return self.__class__(self.elements[:-1])





class Evaluator(val.Evaluator[Ref]):
    """
    Evaluador de referencias globales
    """
    base: Ref = Ref.root

    @singledispatchmethod
    def eval(self, node: syn.Statement) -> Ref:
        return super().eval(node)

def eval(expr: syn.Expr, *, base = Ref.root):
    return Evaluator(base).eval(expr)