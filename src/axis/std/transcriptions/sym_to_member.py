from axis.core import syn
from axis.std.expressions import Sym, Member

class SymToMemberTranscriptor(syn.AstTransformer):
    member_of: syn.Expr

    def transform(self, node: syn.Expr) -> syn.Expr:
        if isinstance(node, Sym):
            # solo transcribe si sym.at is None?
            return Member(
                of=self.member_of, 
                name=node.name
            ).with_span_of(node)
        return super().transform(node)

def transcript_sym_to_member_expressions(ast: syn.Expr, of: syn.Expr):
    return SymToMemberTranscriptor(of).transform(ast)

