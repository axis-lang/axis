from __future__ import annotations
from .abstract import Node
from .expr import Expr

class Item(Node, abstract=True):
    #children: tuple[Item]
    doc: tuple[Doc] = ()

class Doc(Item): # ::Doc
    content: str

class Val(Item):
    id: str
    bound: Expr
    value: Expr

class Takes(Item): # ::Params
    class Val(Val):
        ...
    values: tuple[Val]

class Where(Item): # ::GenParams
    class Val(Val):
        ...
    bounds: tuple[Val]

class As(Item):
    expr: Expr

'''
# Un SIEMPRE tuple es definido por otro tuple 
# Tup[Tup] ...

el tuple externo define clave->valores y el interno clave -> tipo
ambos comparten el mismo keymap

el tuple interno es un TypedIndex o indice no uniforme
UniformIndex
NonUniformIndex

'''
