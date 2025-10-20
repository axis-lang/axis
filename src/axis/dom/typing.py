from __future__ import annotations
from protobase import Record, frozendict
from axis.dom.tuple_ import Tuple, Shape, Index


class Node(Record, frozen=True, consed=True, abstract=True): ...


type Atom = int | float | str | bool | None
type Data = Atom | tuple | frozenset | frozendict


class Meta(Record, frozen=True, consed=True, abstract=True): ...

class Const(Meta, frozen=True, consed=True, abstract=True):
    '''
    Un valor constante es un valor completamente determinado 
    y conocido en tiempo de compilacion.
    '''

class ConstStruct(Const, frozen=True, consed=True):
    '''
    Meta de un valor constante estructural:
    val a = (x: 1, y: 2)
    '''
    fields: Tuple[str, Const]

class ConstSymbol(Const, frozen=True, consed=True):
    '''
    Meta de un valor constante symbolico:
    val a = MySymbol[K: Text](x: 1, y: 2)
    '''
    symbol: tuple[str, ...]
    params: Tuple[str, Const] | Atom

class ConstQualification(Const, frozen=True, consed=True, abstract=True):
    '''
    '''
    qualifiers: tuple[Const, ...]
    base: ConstStruct | ConstSymbol


class Val(Node, frozen=True, consed=True):
    meta: Meta
    data: Data

    @property
    def is_const(self) -> bool:
        return isinstance(self.meta, Const)

