from __future__ import annotations
from protobase import Record, frozendict
from axis.dom.tuple_ import Tuple, Shape, Index


class Node(Record, frozen=True, consed=True, abstract=True): ...


type Atom = int | float | str | bool | None
type Data = Atom | tuple | frozenset | frozendict


class Meta(Record, frozen=True, consed=True, abstract=True): ...


class TupleSpec(Meta, frozen=True, consed=True):
    """
    Meta de un valor estructural (tupla/record posicional, nominal o mixto).
    """

    fields: Tuple[str, Meta]


class TypeSymbol(Meta, frozen=True, consed=True):
    """
    Meta de un valor nominal:
    val a = MySymbol[K: Text](x: 1, y: 2)
    """

    symbol: tuple[str, ...]
    params: Val | Atom


class QualifiedType(Meta, frozen=True, consed=True, abstract=True):
    """
    Meta de un valor calificado:
        Array[3, 3] Natural
        Map[Id] (name: String, age: Natural)
    """

    qualifiers: tuple[Val, ...]
    base: Val


class Val[M: Meta = Meta, D: Data = Data](Node, frozen=True, consed=True):
    meta: M
    data: D
