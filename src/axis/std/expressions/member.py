from os import name
from axis.core import syn

class Member(syn.Expr):
    of: syn.Expr
    name: str

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'


@syn.AstBuilder.build.register
def build_member_ast(
    self,
    ctx: syn.AxisParser.MemberAccessContext,
    of,
    *members: str,
):
    result = of
    for member in members:
        result = Member(of=result, name=member)
    return result


@syn.Matcher.match.register(Member)
def match_member(self: syn.Matcher, mem: Member, other: syn.Expr):    
    if not mem.is_wildcard:
        return self.match_node(mem, other)

    if not isinstance(other, Member):
        raise syn.StopUnification        

    self.match(mem.of, other.of)

    self.capture(mem.name, other)

        
