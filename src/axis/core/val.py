from functools import singledispatchmethod
from typing import Self
from protobase import Object
from axis.core import syn

class Value(Object, abstract=True):
    """
    un valor es un objeto que puede ser resultado de una evaluacion
    """

    def member(self, name: str) -> Self:
        raise NotImplementedError(f"Cannot get member {name} of {self}")

    def apply(self, value: Self) -> Self:
        raise NotImplementedError(f"Cannot apply {self} to {value}")

    def index(self, value: Self) -> Self:
        raise NotImplementedError(f"Cannot index {self} with {value}")
    


class Evaluator[V: Value](Object):
    """
    A base class for a ast statement (and expression) evaluator.
    """

    def __call__(self, item: syn.Statement) -> V:
        return self.eval(item)
    
    @singledispatchmethod
    def eval(self, node: syn.Statement) -> V:
        raise NotImplementedError(f"Cannot evaluate {node.__class__.__name__}")
