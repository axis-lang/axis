"""

Qualifier

a: Natural 1
a: Natural 0..<10
a: (a:Natural 1) = (a: 1)

a: Array[1,1] = Natural

(..., class_bound, val_bound)


"""
from __future__ import annotations
from protobase import Record
from axis import builtins

class Value(Record, frozen=True, abstract=True):
    ...

class Const(Value, frozen=True, consed=True, abstract=True):
    ...


class Ref(Value, frozen=True, consed=True):
    ...



class Bound(Record, frozen=True, consed=True, abstract=True):
    ...

class Type(Bound, frozen=True, consed=True):
    qualifiers: builtins.Tuple[Const] # conjunto de valores constantes construidos
    target: ... # tipo de destino estructural o nominal


class Struct(Bound, frozen=True, consed=True):
    fields: builtins.Tuple[Bound]
