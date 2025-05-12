"""
Antes de arrojar un error de tipado
(intentar) aplicar una transformacion (al tipo)
de una lista transformaciones ordenada por precedencia
de forma recurrente
"""

from __future__ import annotations

from abc import abstractmethod
from itertools import chain
from pathlib import Path
from typing import Annotated, Any, Optional

from protobase import Context, Object, Record, cached_property
from rich import print

class Id(Record, consed=True):  # final = True
    parts: tuple[str]

    @classmethod
    def from_path(cls, path: Path):
        parts = chain.from_iterable(part.split(".") for part in path.parts)
        return cls(parts=tuple(parts)[:-1])

    def __rich__(self):
        return "::".join(self.parts)


class Qual(Record, frozen=True, abstract=True): ...

class Container(Qual, abtract=True): 
    'list'
    lenght: Optional[int] # can be optional

class List(Record, frozen=True): 
    'list'
    
class Index(Record, frozen=True): 
    'Index es un qualifier'

class Set(Record, frozen=True): 
    'un index con indexador identity'

class Class(Record, frozen=True):
    class Member(Record, frozen=True):
        offset: int # computed member does not have offset (cached yet?)
        name: str
        type: Type
        value: Val

    members: Annotated[Index[Member], "Index(name: {x -> x.name}) Member]"]

class LazyMap(Record, frozen=True):
    '''LazyMap(x -> beta) Person'''
    lamb: ...

class LazyReduce(Qual, frozen=True):
    ''



class Property(Record, frozen=True):
    '''Property('alpha') Person'''
    member: str

class Meta(Record, frozen=True, abstract=True):
    @property
    @abstractmethod
    def value_type(self): ...

class Type(Record, frozen=True):
    '''
    resulting types se computa en reversed, comenzando con Type((), class_)
    cada qualifier construye un resulting type que seria el parametro del 
    siguiente. el resulting type final es el tipo del valor accedido, en 
    contraste con el tipo del valor almacenado. 

    t: List[:] Real = (...)


    '''
    qualifiers: tuple[Qual, ...]
    class_: Class

    @property
    def attributes(self):
        """los atributos son dados por los cualificadores"""

    @property
    def properties(self):
        """las propiedades son dadas las la clase (miembros )"""

    def get_implementation(self, impl_definition, default = None):
        '''retorna la implementacion de un tipo'''

    @cached_property
    def value_type(self):
        """el tipo del valor accedido (vs almacenado)

        aplica transformaciones de tipo.

        resulting type consiste en aplicar una sustitucion a los tipos y cualificadores internos.
        "Index Property(name) Person" se sustituye por "Index String".

        una vista de un array:
        a: Array[100,100] Natural = (...)
        b: ViewRange[25..75, 25..75] Array[100, 100] Natural = a[25..75, 25..75]
        
        transformaciones a los tipos

        impl transformation_name for Q1() Q2() Q3() .. as Q4() ..

        las transformaciones deben ser "reversibles" para poder propagar la inferencia de tipos sobre ellas..

        """
        #


class Val[V=Any](Record, frozen=True):
    """
    statics & dynamics: tanto la parte meta como la parte data de un valor
    puede estar compuesta de otros valores que pueden ser estaticos o dinamicos.
    de forma que pueden separarse en dos grupos de valores.
    
    Categorizacion por staticidad y dinamismo:
     - pure-static: todos los valores (presentes en meta y en data) son estaticos.
     - meta-static: todos los valores (presentes en meta) son estaticos y 
     - pure-dynamic: todos los valores (presentes en meta y en data) son dinamicos.

    nested values: la anidacion de valores puede ser muy util a la hora de 
    jugar con representaciones de datos. un valor del tipo Person puede se representado
    como un valor del tipo Map[str, Any] o como bytes, y de esta forma ser serializado.
         
    """
    # un tipo de meta es una composicion de Qual class Composition que retorna un type
    meta: Meta # Meta que puede ser type, obtiene type llamando a resulting type.
    data: V

    @property
    def type(self):
        return self.meta.value_type




