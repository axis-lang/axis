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

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'

    @property
    def wildcard(self) -> Optional[str]:
        if self.name[0] == '$':
            return self.name

    @property
    def is_placeholder(self) -> bool:
        return self.name == '_'

Sym.ROOT = Sym('@root', at='root')

@syn.AstBuilder.build.register(syn.AxisParser.SymContext)
def build_sym_ast(
    self, 
    ctx: syn.AxisParser.SymContext, 
    name: str,
    at: Optional[str] = None
):
    return Sym(name=name, at=at)


@syn.Matcher.match.register(Sym)
def unify_sym(self: syn.Matcher, sym: Sym, value: syn.Expr):
    if not sym.is_wildcard:
        return self.match_node(sym, value)
    
    self.capture(sym.name, value)
    
    
