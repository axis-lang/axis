from __future__ import annotations

from enum import Enum
from typing import Optional

from .abstract import Item, Node
from .expr import Expr, Call


class Unit(Item):
    """
    """
    

class Val(Item):
    as_: Expr
    bound: Optional[Expr] 
    value: Optional[Expr]

class Def(Item):
    """
    Represents a 'def' entity:
    
    def Vector(..)
    takes:
        val x: N
        val y: N
    where:
        val N: Number
    """
    expr: Expr

    class Kind(str, Enum):
        CLASS = 'class'
      

