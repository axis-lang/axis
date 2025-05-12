from __future__ import annotations
from typing import ClassVar, Optional
from axis.core import syn

from .member import Member

class Sym(syn.Expr):
    '''
    Representa un simbolo en el AST que debe ser resuelto semanticamente
    '''
    ROOT: ClassVar[Sym]

    name: str
    at: Optional[str] = None

Sym.ROOT = Sym('@root', at='root')    

@syn.AstBuilder.build.register
def build_sym_ast(
    self: syn.AstBuilder, 
    ctx: syn.AxisParser.IdentifierContext, 
    val: str
):
    return Sym(val)

