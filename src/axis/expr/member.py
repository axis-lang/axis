from typing import Self
from axis import syn, val
from .sym import Sym

class Member(syn.Expr, frozen=True):
    of: syn.Expr
    name: str

    def __str__(self):
        return f'{self.of}.{self.name}'

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'
    
    def as_sym(self):
        return Sym(name=self.name).with_span_of(self)

    @classmethod
    def build(cls, of: syn.Expr, *members):
        result = of
        for member in members:
            result = cls(of=result, name=member)
        return result


# @syn.Builder.build.register
# def build_member(
#     self,
#     ctx: syn.AxisParser.MemberAccessContext,
#     of: syn.Node,
#     *members: str,
# ):
#     result = of
#     for member in members:
#         result = Member(of=result, name=member)
#     return result


@syn.Matcher.impl(Member)
def match_member(self: syn.Matcher, pattern: Member, value: syn.Expr):    
    if not pattern.is_wildcard:
        return self.match_node(pattern, value)

    if not isinstance(value, Member):
        raise self.NoMatch

    self.match(pattern.of, value.of)

    self.capture_value(pattern.name, value.as_sym())
    #self.capture_value(mem.name, mem)

@syn.Reifier.impl(Member)
def reify_member(self: syn.Reifier, mem: Member):    
    if not mem.is_wildcard:
        return self.reify_node(mem)
    
    # tail = self.value(mem.name)
    # si tail es member, path_prefix tail con self.reify(mem.of)
    # sino:

    return mem.with_attr(
        of=self.reify(mem.of),
        name=self.value(mem.name, expected_type=Sym).name
    )

    return self.reify(self.value(mem.name))

        

# @val.Ref.Evaluator.eval.register(Member)
# def eval_member(self: val.Ref.Evaluator, mem: Member):
#     return self.eval(mem.of).member(mem.name)
