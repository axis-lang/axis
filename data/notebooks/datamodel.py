from __future__ import annotations
from typing import Any
from protobase import Record, frozendict, cached_property


class Tuplet[T, K = str](Record, frozen=True):
    """
    """

    class Index[K = str](Record, frozen=True):
        '''
        Un indice es un mapeo de llaves a offsets en una tupla
        las claves puramente nominales se almacenan como numeros
        negativos mientras que las claves con nominacion opcional
        se almacenan como numeros positivos.

        una tupla es descrita por varios segmentos y existen varias convenciones:
         - la convencion estructural: solo contiene elementos nominales

         - la convencion de argumento (siguiendo el estilo de python):
            1. el tuple se compone de un segmento posicional por la izquierda
              que contiene en su final elementos mixtos (posicionales y nominales)
            2. seguido de un segmento nominal por la derecha

            (1, 2, alpha=3, beta=4) es asignable a (a:int, b:int, alpha:int, ..more)

         - la convencion de arreglo (ndarrays con dimensiones nombradas)
            1. el tuple se compone de un segmento posicional por la izquierda
              que contiene elementos mixtos a la derecha (al final)
            2. seguido de un segmento de argumentos nominales
            3. seguido de un segmento posicional por la izquierda que 
              contiene elementos mixtos a la izquierda

        
        '''
        offsets: frozendict[K, int]

        @cached_property
        def nominal_keys(self) -> frozenset[K]:
            return frozenset(k for k, v in self.offsets.items() if v < 0)

    index: Index[K]
    values: tuple[T, ...]

    # def __len__(self):
    #     return len(self.values)

    # def __iter__(self):
    #     return iter(self.values)

    # def __getitem__(self, item: int) -> T:
    #     return self.values[item]

    def get(self, key: K, default: Any = None) -> T | Any:
        if key in self.index.offsets:
            return self.values[self.index.offsets[key]]
        return default

    def at(self, key: K) -> T:
        return self.values[self.index.offsets[key]]


class Class(Record, frozen=True):
    class Property:
        name: str
        type: Val
    properties: Tuplet[Property]


class Val(Record, frozen=True):
    meta: ...
    data: Any


person = Class(
    name="Person",
    properties=Tuplet(
        index=Class.Property.Index(positions=frozendict()),
        values=(Class.Property(type=Val(meta=..., data=...)),),
    ),
)
