from __future__ import annotations
from .abstract import Node, Block, Item
from .expr import Expr
from .items import Val

class Doc(Block):
    content: str

class Takes(Block):  ...

class Where(Block): ...

class Returns(Block):
    expr: Expr
