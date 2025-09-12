
from functools import singledispatchmethod
from typing import Any
from protobase import Object, Record, attrs_of, frozendict
from .node import Node


class AstVisitor(Object, abstract=True):
    def __call__(self, node: Node):
        self.visit(node)

    @singledispatchmethod
    def visit(self, node: Any):
        raise NotImplementedError(
            f"{type(self).__qualname__}.visit not implemented for {type(node).__qualname__}"
        )

    @visit.register    
    def visit_node(self, node: Node):
        for v in attrs_of(node).values():
            self(v)

    @visit.register    
    def visit_tuple(self, node: tuple):
        for v in node:
            self(v)

