from __future__ import annotations
from typing import Optional
from .abstract import Node, Item
from .expr import Expr


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


