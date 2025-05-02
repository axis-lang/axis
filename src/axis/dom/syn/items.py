from typing import Optional
from .abstract import Item, Expr
from .expr import Apply, Sym
from axis.dom import ref, log



class Mod(Item):
    expr: Optional[Expr]
    
class Unit(Mod):
    ...
   
class Use(Item):
    """
    Represents a 'use' entity:
    use x
    """
    
    expr: Expr
    bound: Optional[Expr]
    value: Optional[Expr]

class Val(Item):
    """
    Represents a 'val' entity:
    val x: N
    val y: N
    where:
        val N: Number
    """
    expr: Expr
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

    @property
    def sym(self) -> Optional[Sym]:
        expr = self.expr

        if isinstance(expr, Apply):
            expr = expr.function

        if isinstance(expr, Sym):
            return expr
        
