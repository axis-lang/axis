from __future__ import annotations
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Optional
from .model import *
from ..tuple import Tuple
from axis.components.entity import know


"""
EVALUATTION
"""
_eval_context: EvaluationContext | None = None


class EvaluationContext[T]:
    _parent_context: EvaluationContext[T] | None = None
    _visited: dict[Node, T]
    _scope: dict[Entity, T]

    def __init__(self, argument: T, /, scope: Optional[dict[Entity, T]] = None):
        # self._parent_context = parent

        self._argument = argument
        self._visited = {}
        self._scope = scope if scope is not None else {}

    ## existen dos formas de entrar en un contexto,
    # una es una evaluacion anidada y la otra una evaluacion
    # via apply

    def __enter__(self):
        global _eval_context
        self._parent_context = _eval_context
        _eval_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global _eval_context
        _eval_context = self._parent_context
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

    def eval_leaf(self, leaf: Leaf) -> T:
        return self._argument

    def eval_use(self, use: Use) -> T:
        for ctx in self.context_hierarchy_in_resolution_order():
            if use.entity in ctx._scope:
                return ctx._scope[use.entity]

        return self.missing_use(use)

    def missing_use(self, use: Use):
        raise NotImplementedError(f"Use {use.entity} not found in {self}")

    def eval_constant(self, constant: Constant) -> T:
        return constant.value

    def eval_composition(self, composition: Composition, inputs: Tuple[T]) -> T:
        return inputs

    def eval_apply(self, apply: Apply, function: T, argument: T) -> T:
        if isinstance(function, Trunk):
            return self.apply_trunk(apply, function, argument)
        elif callable(function):
            return self.apply_builtin(apply, function, argument)

        raise NotImplementedError(
            f"eval_apply for {function.__class__} is not implemented in {self.__class__}"
        )

    @property
    def apply_trunk_context_type(self):
        return type(self)

    def apply_trunk(self, apply: Apply, trunk: Trunk, argument: T):
        with self.apply_trunk_context_type(argument):
            return eval(trunk)

    def apply_builtin(self, apply: Apply, function: Trunk, argument: T):
        if isinstance(argument, Tuple):
            args, kwargs = argument.to_args()
            return function(*args, **kwargs)

        raise NotImplementedError(
            f"eval_builtin_apply for {argument.__class__} is not implemented in {self.__class__}"
        )

    def eval_switch(self, switch: Switch, selector: T):
        # branch matching
        branch = switch.branches.get(selector, None)
        if branch is None:
            branch = switch.branches.get(Switch.DEFAULT, None)
        if branch is None:
            raise ValueError(
                f"No branch matched in switch {switch} with selector {selector}"
            )

        return eval(branch)

    def eval_loop(self, loop: Loop):
        return

    def eval_trunk(self, trunk: Trunk, result: T):
        return result


# _eval_context = EvaluationContext(
#     None,
#     scope={  # GLOBAL_SCOPE
#         know.GET_ATTR: lambda x, y: x[y],
#         know.ADD: lambda x, y: x + y,
#         know.MUL: lambda x, y: x * y,
#         know.GT: lambda x, y: x > y,
#         know.LT: lambda x, y: x < y,
#         know.EQ: lambda x, y: x == y,
#         know.NE: lambda x, y: x != y,
#         know.LE: lambda x, y: x <= y,
#         know.GE: lambda x, y: x >= y,
#         know.SUB: lambda x, y: x - y,
#         know.TRUEDIV: lambda x, y: x / y,
#         know.FLOORDIV: lambda x, y: x // y,
#         know.MOD: lambda x, y: x % y,
#         know.POW: lambda x, y: x**y,
#         know.LSHIFT: lambda x, y: x << y,
#         know.RSHIFT: lambda x, y: x >> y,
#         know.AND: lambda x, y: x & y,
#         know.OR: lambda x, y: x | y,
#         know.XOR: lambda x, y: x ^ y,
#         know.PRINT: lambda x: print(x),
#     },
# )


def eval(node: Node):
    """
    Eval puede ser parametrizado via evaluation_context
    """
    if (ctx := _eval_context) is None:
        raise ValueError("DFG Evaluation context is not present.")

    prev_result = _eval_context.check_visited(node)

    if prev_result is not None:
        return prev_result

    try:
        match node:
            case Leaf() as leaf:
                result = ctx.eval_leaf(leaf)
            case Use() as use:
                result = ctx.eval_use(use)
            case Constant() as constant:
                result = ctx.eval_constant(constant)
            case Composition() as composition:
                inputs = composition.inputs.map(eval)
                result = ctx.eval_composition(composition, inputs)
            case Apply() as apply:
                function = eval(apply.function)
                argument = eval(apply.argument)
                result = ctx.eval_apply(apply, function, argument)
            case Switch() as switch:
                selector = eval(switch.selector)
                result = ctx.eval_switch(switch, selector)
            case Loop() as loop:
                # inputs = eval(loop.inputs)
                result = ctx.eval_loop(loop)
            case Trunk() as trunk:
                for node in trunk.children:
                    eval(node)
                result = eval(trunk.result)
                result = ctx.eval_trunk(trunk, result)
    except Exception:
        print("Error evaluating", node)
        raise

    ctx.visited(node, result)

    return result
