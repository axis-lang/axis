from functools import singledispatchmethod
from typing import Any, Self
from protobase import Object, attrs_of, frozendict
from .node import Node
from .statement import Statement


class Reifier(Object):
    values: dict[str, Any] = {}

    def __call__(self, item: Node) -> Node:
        return self.reify(item)

    def value(self, name: str, expected_type: type = Node) -> Node:
        if name not in self.values:
            raise ValueError(f"Unresolved value: {name}")

        value = self.values[name]

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Expected value of type {expected_type.__name__}, "
                f"but got {type(value).__name__} for '{name}'"
            )
        
        return value

    @singledispatchmethod
    def reify(self, value: Any) -> Any:
        return value

    @reify.register
    def reify_node[N:Node](self, node: N) -> N:
        attrs = {k: self.reify(v) for k, v in attrs_of(node).items()}
        return node.__class__(**attrs).with_span_of(node)

    @reify.register
    def reify_tuple(self, tup: tuple) -> tuple:
        return tuple(self.reify(elem) for elem in tup)


class Reify(Object):
    pattern: Statement

    def __call__(self, values: dict[str, Node]) -> Node:
        reifier = Reifier(values=values)
        return reifier(self.pattern)

    @classmethod
    def expr(cls, pattern: Statement | str) -> Self:
        if isinstance(pattern, str):
            pattern = Statement.parse(pattern)
        return cls(pattern=pattern)
