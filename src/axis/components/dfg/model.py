# %%
from __future__ import annotations

import inspect
from types import FunctionType
from typing import Dict, Optional, TypeAlias

from frozendict import frozendict
from protobase import Object, traits

from axis.components.entity import know
from axis.components.tuple.model import Tuple

__all__ = [
    "Node",
    "Leaf",
    "Use",
    "Constant",
    "Trunk",
    "Composition",
    "Apply",
    "Loop",
    "Switch",
    "BuildContext",
    "compile",
]


type Entity = str | FunctionType

type Constant = str | int | float | bool

_build_context = None


class BuildContext:
    _parent_context: BuildContext | None = None
    _nodes: list[Node]

    def __init__(self):
        self._nodes = []

    def __enter__(self):
        global _build_context
        self.prev = _build_context
        _build_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global _build_context
        _build_context = self.prev

    def new_node(self, node: Node):
        self._nodes.append(node)
        return node


class Node(traits.Repr, traits.Consed):
    EphimeralId: TypeAlias = str

    @property
    def ephimeral_id(self) -> EphimeralId:
        return f"{id(self)}"

    ## Build toolkit

    def attr(self, name: str):
        return Apply.build(
            function=Use.build(know.GET_ATTR),
            argument=Composition.build(self, Constant.build(name)),
        )

    def __call__(self, *args: Tuple[Node], **kwargs: Dict[str, Node]):
        if isinstance(self, (Trunk | FunctionType)):
            function = Constant.build(self)
        else:
            function = self

        return Apply.build(
            function=function,
            argument=Composition.build(*args, **kwargs),
        )

    def _infix_operator(operator):
        def infix_operator(self: Node, other: Node):
            return Apply.build(
                function=Use.build(operator),
                argument=Composition.build(self, other),
            )

        return infix_operator

    __lt__ = _infix_operator(know.LT)
    __gt__ = _infix_operator(know.GT)
    __le__ = _infix_operator(know.LE)
    __ge__ = _infix_operator(know.GE)
    eq = _infix_operator(know.EQ)
    __ne__ = _infix_operator(know.NE)
    __hash__ = traits.Consed.__hash__
    __add__ = _infix_operator(know.ADD)
    __sub__ = _infix_operator(know.SUB)
    __mul__ = _infix_operator(know.MUL)
    __truediv__ = _infix_operator(know.TRUEDIV)
    __floordiv__ = _infix_operator(know.FLOORDIV)
    __mod__ = _infix_operator(know.MOD)
    __pow__ = _infix_operator(know.POW)
    __lshift__ = _infix_operator(know.LSHIFT)
    __rshift__ = _infix_operator(know.RSHIFT)
    __and__ = _infix_operator(know.AND)
    __or__ = _infix_operator(know.OR)
    __xor__ = _infix_operator(know.XOR)

    del _infix_operator

    def switch(self, branches: Switch.Branches):
        return Switch.build(self, branches)


class Leaf(Object, Node):
    name: str

    @classmethod
    def build(cls, name: str):
        return _build_context.new_node(cls(name=name))


class Use(Object, Node):
    """
    Este nodo representa el uso de una entidad externa, esta entidad será resuelta
    por el contexto de ejecución.

    Algunos uses pueden convertirse en consts si son resueltos en tiempo de compilación.

    Los uses no resueltos en tiempo de compilacion representan dependencias externas.
    """

    entity: Entity

    @classmethod
    def build(cls, entity: Entity):
        return _build_context.new_node(cls(entity=entity))


class Constant(Object, Node):
    """
    Un const es un valor constante, no puede ser modificado.
    """

    value: Constant

    @classmethod
    def build(cls, value: Constant):
        return _build_context.new_node(cls(value=value))


class Trunk(Object, Node):
    """
    the first children is the HeadNode of the region dominated by this Node
    """

    children: tuple[Node]
    result: Node  # generalmente el del ultimo children?

    @property
    def leaf(self):
        return self.children[0]

    @classmethod
    def build(cls, result: Node):
        return cls(children=tuple(_build_context._nodes), result=result)


class Composition(Object, Node):
    """
    Tuple puede utilizarse para construir argumentos de llamada o contextos de cierre
    DfgCompose
    """

    inputs: Tuple[Node]  # no es una lista de nodos, es un Tuple

    @classmethod
    def build(cls, *args: tuple[Node, ...], **kwargs: Dict[str, Node]):
        return _build_context.new_node(cls(inputs=Tuple.from_args(*args, **kwargs)))


class Apply(Object, Node):
    function: Node
    argument: Node

    @classmethod
    def build(cls, function: Node, argument: Node):
        return _build_context.new_node(cls(function=function, argument=argument))


class Loop(Object, Node):
    input: Optional[Node]
    iteration: Trunk

    @classmethod
    def build(cls, input: Optional[Node], iteration: Trunk):
        return _build_context.new_node(cls(iteration=iteration, input=input))


class Switch(Object, Node):
    class MatchPatter: ...

    DEFAULT = MatchPatter()

    # Constant
    Match: TypeAlias = bool | int | float | str | MatchPatter

    input: Optional[Node]
    selector: Node
    branches: frozendict[Match, Node]

    @classmethod
    def build(cls, selector: Node, branches: dict[Match, Node], /, input: Node = None):
        return _build_context.new_node(
            cls(input=input, selector=selector, branches=frozendict(branches))
        )


def compile(fn):
    fn_signature = inspect.signature(fn)
    fn_parameters = fn_signature.parameters

    with BuildContext():
        leaf = Leaf.build(fn.__name__)
        params = [leaf.attr(p.name) for p in fn_parameters.values()]
        result = fn(*params)
        trunk = Trunk.build(result)

    return trunk
