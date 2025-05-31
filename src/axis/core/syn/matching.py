from functools import singledispatchmethod
from typing import Any, Self
from protobase import Object, Record, attrs_of, frozendict
from .node import Node
from .expr import Expr
from .ast_transformer import AstTransformer


class StopUnification(Exception): ...

# Matching Matcher
# Match
# a <$op> b
class Matcher(Object):
    """
    A base class of a reification pass for the AST
    """
    class StopMatching(Exception):
        ...

    values: dict[str, set[Any]] = {}

    def __call__(self, ctrl: Any, value: Any)-> frozendict[str, Any] | None:
        try: 
            self.match(ctrl, value)
        except StopUnification:
            return
        
        # las variables capturadas solo pueden tener un valor.        

        return frozendict(self.values)

    def capture(self, name: str, value: Any):
        self.values.setdefault(name, set()).add(value)

    @singledispatchmethod
    def match(self, ctrl: Any, value: Any):
        # if type(value) is not type(ctrl):
        #     raise StopUnification(f"Cannot unify {ctrl} with {value}")

        if ctrl != value:
            raise StopUnification

    @match.register
    def match_node(self, ctrl: Node, value: Any) -> Node:
        if not isinstance(value, type(ctrl)):
            raise StopUnification

        for k, v in attrs_of(ctrl).items():
            self.match(v, getattr(value, k))

    @match.register
    def match_tuple(self, ctrl: tuple, value: Any) -> Node:
        if not isinstance(value, tuple):
            raise StopUnification
        
        if len(ctrl) != len(value):
            raise StopUnification

        for a, b in zip(ctrl, value):
            self.match(a, b)


class Match(Object):
    pattern: Expr
    #vars: frozendict[Any, str]

    def __call__(self, expr: Expr|str) -> frozendict[str, Any] | None:
        if isinstance(expr, str):
            expr = Expr.parse(expr)
        unifier = Matcher()
        return unifier(self.pattern, expr)

    @classmethod
    def expr(cls, pattern: Expr|str) -> Self:
        if isinstance(pattern, str):
            pattern = Expr.parse(pattern)
        return cls(pattern=pattern)

