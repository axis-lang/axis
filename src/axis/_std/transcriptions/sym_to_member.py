from axis import syn
from axis._std.expr import Sym, Member

class SymToMemberOf(syn.AstTransformer):
    member_of: syn.Expr
    #scope_mapping: dict[str|None, syn.Expr] = {}
    def transform(self, node: syn.Expr) -> syn.Expr:
        if isinstance(node, Sym):
            # solo transcribe si sym.at is None?
            # utilizar el at clave para mapear un diccionario de miembros, None para default

            return Member(
                of=self.member_of, 
                name=node.name,
            ).with_span_of(node)
        return super().transform(node)

def sym_to_member_of(ast: syn.Expr, of: syn.Expr):
    return SymToMemberOf(of).transform(ast)

