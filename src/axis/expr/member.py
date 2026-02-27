from typing import Self
from axis import syn, val
from .sym import Sym

__all__ = ["Member"]

class Member(syn.Expr):
    of: syn.Expr
    name: str

    def __str__(self):
        return f'{self.of}.{self.name}'

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == '$'

    @property
    def match_spec(self) -> syn.MatchSpec:
        if self.is_wildcard:
            return syn.MatchSpec(
                capture_name=self.name[1:],
                filter_any=frozenset({"name"}),
            )
        return syn.MatchSpec()
    
    def as_sym(self):
        return Sym(name=self.name).with_span_of(self)

    @classmethod
    def build(cls, of: syn.Expr, *members):
        result = of
        for member in members:
            result = cls(of=result, name=member)
        return result


@syn.Matcher.impl_rule(Member)
def match_member(self: syn.Matcher, pattern: Member, value: syn.Expr) -> syn.MatchResult | None:
    if not isinstance(value, Member):
        return None

    if not pattern.is_wildcard and pattern.name != value.name:
        return None

    result = self.match(pattern.of, value.of)
    if result is None:
        return None

    return result


@Member.as_impl(str)
def _as_str(self: Member) -> str:
    return self.name


@Member.as_impl(Sym)
def _as_sym(self: Member) -> Sym:
    return self.as_sym()

@syn.Reifier.impl(Member)
def _reify(self: syn.Reifier, mem: Member):    
    if not mem.is_wildcard:
        return self.reify_node(mem)
    
    # tail = self.value(mem.name)
    # si tail es member, path_prefix tail con self.reify(mem.of)
    # sino:

    return mem.with_attr(
        of=self.reify(mem.of),
        name=self.value(mem.name, expected_type=Sym).name
    )


        
