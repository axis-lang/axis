from functools import singledispatchmethod
from typing import Any, Self
from protobase import Object, Record, attrs_of, frozendict
from .node import Node
from .expr import Expr

class Matcher(Object):
    """
    A base class of a reification pass for the AST
    """

    class StopMatching(Exception): ...

    values: dict[str, list[Node]] = {}

    def __call__(self, ctrl: Node, value: Node) -> frozendict[str, Node] | None:
        try:
            self.match(ctrl, value)
        except self.StopMatching:
            return

        # las variables capturadas solo pueden tener un valor.
        result = {}
        for k, v in self.values.items():
            if len(v) == 1:
                result[k] = v[0]
                continue
            if len(v) > 1:
                items = set(v)
                if len(items) == 1:
                    result[k] = items.pop()
                else:
                    # raise ValueError(f"Variable {k} captured multiple values: {v}")
                    return None  # or raise an error if you prefer

        return frozendict(result)

    def capture_value(self, name: str, value: Any):
        self.values.setdefault(name, []).append(value)

    def stop_matching(self):
        raise self.StopMatching

    @singledispatchmethod
    def match(self, ctrl: Any, value: Any):
        # if type(value) is not type(ctrl):
        #     raise StopUnification(f"Cannot unify {ctrl} with {value}")

        if ctrl != value:
            raise self.StopMatching

    @match.register
    def match_node(self, ctrl: Node, value: Any) -> Node:
        if not isinstance(value, type(ctrl)):
            raise self.StopMatching

        for k, v in attrs_of(ctrl).items():
            self.match(v, getattr(value, k))

    @match.register
    def match_tuple(self, ctrl: tuple, value: Any) -> Node:
        if not isinstance(value, tuple):
            raise self.StopMatching

        if len(ctrl) != len(value):
            raise self.StopMatching

        for a, b in zip(ctrl, value):
            self.match(a, b)


class Match(Object):
    pattern: Expr
    # vars: frozendict[Any, str]

    def __call__(self, expr: Expr | str) -> frozendict[str, Any] | None:
        if isinstance(expr, str):
            expr = Expr.parse(expr)
        matcher = Matcher()
        return matcher(self.pattern, expr)

    @classmethod
    def expr(cls, pattern: Expr | str) -> Self:
        if isinstance(pattern, str):
            pattern = Expr.parse(pattern)
        return cls(pattern=pattern)
