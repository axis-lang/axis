from functools import singledispatchmethod
from typing import Any, ClassVar, Self, Sequence
from protobase import Object, Record, attrs_of, frozendict
from .node import Node, Expr

class Matcher(Object):

    class NoMatch(Exception): ...

    values: dict[str, list[Node]] = {}

    def __call__(self, target: Node, value: Node) -> frozendict[str, Node] | None:
        try:
            self.match(target, value)
        except self.NoMatch:
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
        self.values.setdefault(name[1:], []).append(value)

    def stop_matching(self):
        raise self.NoMatch

    @singledispatchmethod
    def match(self, target: Any, value: Any) -> None: # TODO: returns bool?
        # if type(value) is not type(ctrl):
        #     raise StopUnification(f"Cannot unify {ctrl} with {value}")

        if target != value:
            raise self.NoMatch

    @classmethod
    def impl(cls, target_type: type[Node]):
        def decorator(func):
            cls.match.register(target_type, func)  # type: ignore
            return func
        return decorator

    @match.register
    def match_node(self, target: Node, value: Any):
        if not isinstance(value, type(target)):
            raise self.NoMatch

        for k, v in attrs_of(target).items():
            self.match(v, getattr(value, k))

    @match.register
    def match_tuple(self, target: tuple, value: Any):
        if not isinstance(value, tuple):
            raise self.NoMatch

        if len(target) != len(value):
            raise self.NoMatch

        for a, b in zip(target, value):
            self.match(a, b)


class Match(Object):
    """
    Match an expression against multiple target patterns
    and return the first successful match's captured values.
    """
    patterns: tuple[Expr, ...]

    def __call__(self, expr: Expr | str) -> frozendict[str, Any] | None:
        if isinstance(expr, str):
            expr = Expr.from_str(expr)
        matcher = Matcher()
        for target in self.patterns:
            result = matcher(target, expr)
            if result is not None:
                return result
        return None

    @classmethod
    def from_expr(cls, *patterns: Expr | str) -> Self:
        patterns = tuple(Expr.from_str(target) if isinstance(target, str) else target for target in patterns)
        return cls(patterns=patterns)

class MatchClass(Record, abstract=True, frozen=True):
    """
    Match an expression against multiple target patterns
    and return the first successful match's captured values.
    """
    match_patterns: ClassVar[tuple[Expr, ...]]

    @classmethod
    def match(cls, expr: Expr | str) -> Self | None:
        if isinstance(expr, str):
            expr = Expr.from_str(expr)

        def _match(cls: type[Self], expr: Expr):
            if not hasattr(cls, 'match_patterns'):
                return None
            for target in cls.match_patterns:
                result = Matcher()(target, expr)
                if result is not None:
                    return cls(**result)

        if res := _match(cls, expr):
            return res

        for subclass in cls.__subclasses__(): # non abstract
            result = _match(subclass, expr)
            if result is not None:
                return result

class MatchResult(Object, abstract=True):
    #match: ClassVar[Match] 
    #match_expressions: ClassVar[Sequence[str | Expr]] = []
    

    @classmethod
    def match(cls, expr: Expr | str) -> Self:
        #for subclass in cls.subclasses: # non abstract
            #subclass.match(expr)
        
        # construye un multimatch a partir de los subclasses
        ...




class MultiMatcher(Object):
    patterns: dict[Expr, type[MatchResult]] = {}

    def add_match_class(self, *expr: str | Expr):
        def decorator(cls: type[MatchResult]):
            for e in expr:
                if isinstance(e, str):
                    e = Expr.from_str(e)
                self.patterns[e] = cls
            return cls
        
    def __call__(self, expr: Expr | str) -> MatchResult | None:
        if isinstance(expr, str):
            expr = Expr.from_str(expr)
        for pattern, cls in self.patterns.items():
            matcher = Matcher()
            result = matcher(pattern, expr)
            if result is not None:
                return cls(**result)
        return None