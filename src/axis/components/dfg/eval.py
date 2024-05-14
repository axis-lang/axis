from __future__ import annotations

from ast import Constant
from typing import Optional, Self

from ..tuple import Tuple
from .model import Apply, Composition, Entity, Leaf, Loop, Node, Switch, Trunk, Use
from .processor import BasicProcessor

'''
tras un nodo loop siempre podriamos contar con un switch que cortocircuita el resto 
del programa si el loop finalizo con return, o si se alcanzo una orden raise dentro del mismo

este mecanismo de short-circuiting deberia ser algo generalizado en el modelo

short-circuit desde un return de una funcion, retornando un continuator

'''

NOT_VISITED = object()


class Evaluator[T](BasicProcessor[T]):
    def __init__(
        self,
        argument: T,
        parent: Optional[Self] = None,
        scope: Optional[dict[Entity, T]] = None,
    ):
        super().__init__(parent)
        self._argument = argument
        self._scope = scope if scope is not None else {}

    def subevaluator(self, argument: T) -> Evaluator[T]:
        return self.__class__(argument, self)

    def process_leaf(self, leaf: Leaf) -> T:
        return self._argument

    def process_use(self, use: Use) -> T:
        for ctx in self.ancestors():
            if use.entity in ctx._scope:
                return ctx._scope[use.entity]

        raise NotImplementedError(f"Use {use.entity} not found in {self}")

    def process_constant(self, constant: Constant) -> T:
        return constant.value

    def process_composition(self, composition: Composition) -> T:
        return composition.inputs.map(self)

    def process_apply(self, apply: Apply) -> T:
        function = self(apply.function)
        argument = self(apply.argument)

        if isinstance(function, Trunk):
            return self.subevaluator(argument)(function)

        if callable(function):
            if isinstance(argument, Tuple):
                args, kwargs = argument.to_args()
                return function(*args, **kwargs)

            raise TypeError(
                f"Invalid argument type {argument.__class__} for function {function}"
            )
        raise TypeError(f"Invalid function type {function.__class__}")

    def process_switch(self, switch: Switch):
        selector = self(switch.selector)

        ## TODO complex branch matching
        if (branch := switch.branches.get(selector, None)) is None:
            if (branch := switch.branches.get(Switch.DEFAULT, None)) is None:
                raise ValueError(
                    f"No branch matched in switch {switch} with selector {selector}"
                )

        if isinstance(branch, Trunk):
            input = self(switch.input)
            return self.subevaluator(input)(branch)

        assert switch.input is None

        return self(branch)

    def process_loop(self, loop: Loop) -> T:
        input = self(loop.input)

        while True:
            result = self.subevaluator(input)(loop.iteration)
            ctrl, result = result.pop("$ctrl")
            # extrae $ctrl de result
            if result == input:
                break
            input = result

    def process_trunk(self, trunk: Trunk) -> T:
        for node in trunk.children:
            self(node)
        return self(trunk.result)


def eval[T](
    node: Node,
    argument: T,
    /,
    scope: dict[Entity, T],
) -> T:
    return Evaluator(argument=argument, parent=None, scope=scope)(node)
