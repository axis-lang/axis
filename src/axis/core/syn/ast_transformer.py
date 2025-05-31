
from decimal import Decimal
from functools import singledispatchmethod
from types import NoneType
from typing import Any
from protobase import Object, Record, attrs_of
from .node import Node

class AstTransformer(Object, abstract=True):
    """
    A base class of a reification pass for the AST
    """

    def __call__(self, item: Node) -> Node:
        return self.transform(item)

    @singledispatchmethod
    def transform(self, value: Any) -> Any:
        """
        Transform a node into another node.
        """
        raise NotImplementedError(f"Cannot transform {value.__class__.__name__}")


    @transform.register
    def transform_node(self, node: Node) -> Node:
        attrs = {
            k: self.transform(v)# if isinstance(v, Node) else v
            for k, v in attrs_of(node).items()
        }
        return node.__class__(**attrs).with_span_of(node)

    @transform.register    
    def transform_none(self, none: None) -> None:
        pass

    @transform.register
    def transform_str(self, string: str) -> str:
        return string

    @transform.register
    def transform_bool(self, boolean: bool) -> int:
        return boolean

    @transform.register
    def transform_int(self, integer: int) -> int:
        return integer


    @transform.register
    def transform_decimal(self, decimal: Decimal) -> Decimal:
        return decimal

    @transform.register
    def transform_tuple(self, tup: tuple) -> tuple:
        return tuple(self.transform(n) for n in tup)

