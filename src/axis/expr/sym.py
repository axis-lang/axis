from __future__ import annotations
from typing import ClassVar, Literal, Optional
from axis import syn


class Sym(syn.Expr):
    """
    Representa un simbolo en el AST que debe ser resuelto semanticamente
    """

    ROOT: ClassVar[Sym]

    name: str
    at: Optional[str] = None

    def __str__(self) -> str:
        if self.at:
            return f"{self.name}@{self.at}"
        return self.name

    @property
    def is_wildcard(self) -> bool:
        return self.name[0] == "$"

    @property
    def is_placeholder(self) -> bool:
        return self.name == "_"

    @property
    def match_spec(self) -> syn.MatchSpec:
        if self.is_placeholder:
            return syn.MatchSpec(match_all=True)
        if self.is_wildcard:
            return syn.MatchSpec(
                capture_name=self.name[1:],
                match_all=True,
                filter_any=frozenset({"name"}),
            )
        return syn.MatchSpec()

    @classmethod
    def build(cls, name: str, at: Literal["@"] | None = None, scope: Optional[str] = None):
        return cls(name=name, at=scope)


Sym.ROOT = Sym("@root")

# @syn.AstBuilder.build.register(syn.AxisParser.SymContext)
# def build_sym_ast(
#     self,
#     ctx: syn.AxisParser.SymContext,
#     name: str,
#     _: Literal['@'] | None = None,
#     at: Optional[str] = None
# ):
#     return Sym(name=name, at=at)


@syn.Matcher.impl_rule(Sym)
def match_sym(self: syn.Matcher, sym: Sym, value: syn.Expr) -> syn.MatchResult | None:
    spec = sym.match_spec
    if spec.match_all:
        if sym.at and sym.at != value.__class__.__name__:
            return None
        return syn.MatchResult.empty()

    if not isinstance(value, Sym):
        return None
    if sym.name != value.name or sym.at != value.at:
        return None
    return syn.MatchResult.empty()


@Sym.as_impl(str)
def _sym_as_str(self: Sym) -> str:
    return self.name


@syn.Reifier.impl(Sym)
def reify_sym(self: syn.Reifier, sym: Sym):
    if not sym.is_wildcard:
        return self.reify_node(sym)

    return self.reify(self.value(sym.name))


# @val.Ref.Evaluator.eval.register(Sym)
# def ref_eval_sym(self: val.Ref.Evaluator, node: Sym) -> val.Ref:
#     return self.base.member(node.name)
