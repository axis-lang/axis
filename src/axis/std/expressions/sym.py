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

print('reg expression')
@syn.AstBuilder.build.register(syn.AxisParser.IdentifierContext)
def build_sym_ast(
    self, 
    ctx: syn.AxisParser.IdentifierContext, 
    val: str
):
    return Sym(val)

