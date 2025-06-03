from multiprocessing import Value
from os import name
from axis.core import syn

class Member(syn.Expr):
    of: syn.Expr
    name: str

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'


@syn.AstBuilder.build.register
def build_member(
    self,
    ctx: syn.AxisParser.MemberAccessContext,
    of: syn.Node,
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
        raise self.StopMatching

    self.match(mem.of, other.of)

    self.capture_value(mem.name, other.name)
    #self.capture_value(mem.name, mem)

@syn.Reifier.reify.register(Member)
def reify_member(self: syn.Reifier, mem: Member):    
    if not mem.is_wildcard:
        return self.reify_node(mem)
    
    return mem.with_attrs(
        of=self.reify(mem.of),
        name=self.value(mem.name)
    )

    return self.reify(self.value(mem.name))

        
