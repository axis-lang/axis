from __future__ import annotations
from .abstract import Statement, Block
from .expr import Expr

class Doc(Block):
    content: str

class Takes(Block):  ...

class Where(Block): ...

class Returns(Block):
    expr: Expr

class Suite(Block):
    statements: tuple[Statement]
