from __future__ import annotations
from pathlib import Path
from typing import ClassVar, Self
from axis.core import src
from .building import AstBuilder
from .statement import Statement

class Expr(Statement, abstract=True): 
    grammar_context_infix: ClassVar[str] = 'Expr'

