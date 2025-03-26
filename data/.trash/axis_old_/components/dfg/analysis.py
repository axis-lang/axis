"""
El chequeo de tipos no debe ser efectuaro por eval sino por analize.

mientras que el proceso de evaluacion es apropiado para validar el
comportamiento de un dfg el proceso de analisis se adapta mejor para
visualizar el grafo.

"""

from __future__ import annotations

from ast import Constant
from contextlib import contextmanager
from typing import Optional

import frozendict

from ..tuple import Tuple
from .model import Apply, Composition, Entity, Leaf, Loop, Node, Switch, Trunk, Use

_analysis_context: AnalysisContext | None = None

#

class AnalysisContext[T]:
    _parent_context: AnalysisContext[T] | None = None
    _visited: dict[Node, T]
    _scope: dict[Entity, T]

    @property
    def subcontext_type(self) -> type[AnalysisContext[T]]:
        return type(self)

    def __init__(self, argument: T, /, scope: Optional[dict[Entity, T]] = None):
        # self._parent_context = parent

        self._argument = argument
        self._visited = {}
        self._scope = scope if scope is not None else {}

    ## existen dos formas de entrar en un contexto,
    # una es una evaluacion anidada y la otra una evaluacion
    # via apply

    def __enter__(self):
        global _analysis_context
        self._parent_context = _analysis_context
        _analysis_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global _analysis_context
        _analysis_context = self._parent_context
        self._parent_context = None

    @property
    def parent_context(self):
        return self._parent_context

    def context_hierarchy_in_resolution_order(self):
        yield self
        ctx = self
        while (ctx := ctx.parent_context) is not None:
            yield ctx

    def check_visited(self, node: Node) -> T | None:
        for ctx in self.context_hierarchy_in_resolution_order():
            if (last_result := ctx._visited.get(node, None)) is not None:
                return last_result

    def visited(self, node: Node, result: T):
        # un nodo Leaf nunca se marca como visitado
        # ???
        if not isinstance(node, Leaf):
            self._visited[node] = result

    def process_leaf(self, leaf: Leaf) -> T:
        return self._argument

    def process_use(self, use: Use) -> T:
        for ctx in self.context_hierarchy_in_resolution_order():
            if use.entity in ctx._scope:
                return ctx._scope[use.entity]

        return self.on_missing_use(use)

    def on_missing_use(self, use: Use):
        raise NotImplementedError(f"Use {use.entity} not found in {self}")

    def process_constant(self, constant: Constant) -> T:
        return constant.value

    def process_composition(self, composition: Composition, inputs: Tuple[T]) -> T:
        return inputs

    def process_apply(self, apply: Apply, function: T, argument: T) -> T:
        if isinstance(function, Trunk):
            return self.apply_trunk(apply, function, argument)
        if callable(function):
            return self.apply_builtin(apply, function, argument)

        raise NotImplementedError(
            f"eval_apply for {function.__class__} is not implemented in {self.__class__}"
        )

    def apply_trunk(self, apply: Apply, trunk: Trunk, argument: T):
        with self.subcontext_type(argument):
            return analyze(trunk)

    def apply_builtin(self, apply: Apply, function: Trunk, argument: T):
        if isinstance(argument, Tuple):
            args, kwargs = argument.to_args()
            return function(*args, **kwargs)

        raise NotImplementedError(
            f"eval_builtin_apply for {argument.__class__} is not implemented in {self.__class__}"
        )

    @contextmanager
    def switch_context(self, switch: Switch):
        def do_switch(selector: T, branches: frozendict[Switch.Match, T]):
            branch = switch.branches.get(selector, None)
            if branch is None:
                branch = switch.branches.get(Switch.DEFAULT, None)
            if branch is None:
                raise ValueError(
                    f"No branch matched in switch {switch} with selector {selector}"
                )

            return eval(branch)

            return branches[selec]
        yield do_switch

    def process_switch(self, switch: Switch, selector: T):
        # branch matching
        branch = switch.branches.get(selector, None)
        if branch is None:
            branch = switch.branches.get(Switch.DEFAULT, None)
        if branch is None:
            raise ValueError(
                f"No branch matched in switch {switch} with selector {selector}"
            )

        return eval(branch)

    def process_loop(self, loop: Loop):
        return

    def process_trunk(self, trunk: Trunk, result: T):
        return result


def analyze(node: Node):
    """
    Eval puede ser parametrizado via evaluation_context
    """
    if (ctx := _analysis_context) is None:
        raise ValueError("DFG Evaluation context is not present.")

    prev_result = _analysis_context.check_visited(node)

    if prev_result is not None:
        return prev_result

    try:
        match node:
            case Leaf() as leaf:
                result = ctx.process_leaf(leaf)
            case Use() as use:
                result = ctx.process_use(use)
            case Constant() as constant:
                result = ctx.process_constant(constant)
            case Composition() as composition:
                inputs = composition.inputs.map(eval)
                result = ctx.process_composition(composition, inputs)
            case Apply() as apply:
                function = eval(apply.function)
                argument = eval(apply.argument)
                result = ctx.process_apply(apply, function, argument)
            case Switch() as switch:
                with ctx.switch_context(switch) as do_switch:
                    selector = eval(switch.selector)
                    branches = switch.branches.map(analyze)
                    result = do_switch(selector, branches)
            case Loop() as loop:
                # inputs = eval(loop.inputs)
                result = ctx.process_loop(loop)
            case Trunk() as trunk:
                for node in trunk.children:
                    eval(node)
                result = eval(trunk.result)
                result = ctx.process_trunk(trunk, result)
    except Exception:
        print("Error evaluating", node)
        raise

    ctx.visited(node, result)

    return result
