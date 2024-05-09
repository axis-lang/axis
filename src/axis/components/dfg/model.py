# %%
"""program Data Flow Graph (DFG) module

A program DFG Data Flow Graph (DFG) is a tree structure that represents the
data flow of a program. The nodes of the tree are the computation nodes
and the edges are the dependencies between the nodes. The PDT is used to
determine the order in which the nodes should be executed.


Regla de ORO: todas las dependencias deben ser consumidas o retornadas.
TODOS los nodos tienen la dependencia state, state representa el estado
(global) del programa y eel contexto de ejecucion. (closures, caller, catchers, etc)

tipos de cierre:
- destructiva FnOnce (consume su propio contexto)
- reiterativa FnMut (muta su propio contexto)
- paralelizable Fn  (no muta su propio contexto)

Estados:

- never: un pseudo valor que indica a los nodos
  dependientes que no seran ejecutados, pero si se
  deberan de consumir sus dependencias.
- Raise X: valor que representa never hasta que sea capturado por {match v: Raised X -> ...}


El parametro State y las funciones puras
----------------------------------------

El parametro State es un valor que representa el estado del programa,
y el contexto de ejecucion del nodo. cuando una operacion modifica una
variable (variable implica valores mutables) la aplicacion de esa
operacion necesita el parametro de estado. Algo parecido ocurre con las
operaciones de lectura. las funciones que NO tienen efectos colaterales
en el stado del programa se llaman funciones puras y NO reciben el
parametro de estado.

una funcion pura por lo tanto no puede leer ni escribir una variable,
y solo puede operar con valoes inmutables o constantes.

una operacion de lectura retorna el valor de una variable.

una operacion de escritura modifica el valor de una variable retornando un nuevo estado ( y el valor anterior)

"""

from __future__ import annotations

from types import FunctionType
from typing import Dict, Any

from protobase import Object, Trait, traits
from axis.components.tuple.model import Tuple


type Entity = str | FunctionType

type Constant = str | int | float | bool


class DfgNode(traits.Repr, traits.Consed):
    """
    Un nodo representa una entidad computacional, que puede ser un valor constante, una operacion, una entidad externa, etc.
    """


class DfgLeaf(Object, DfgNode):
    """ """


class DfgUse(Object, DfgNode):
    """
    Este nodo representa el uso de una entidad externa, esta entidad será resuelta
    por el contexto de ejecución.

    Algunos uses pueden convertirse en consts si son resueltos en tiempo de compilación.

    Los uses no resueltos en tiempo de compilacion representan dependencias externas.
    """

    entity: Entity


class DfgConstant(Object, DfgNode):
    """
    Un const es un valor constante, no puede ser modificado.
    """

    value: Constant


class DfgTuple(Object, DfgNode):
    """
    Tuple puede utilizarse para construir argumentos de llamada o contextos de cierre
    """

    inputs: Tuple[DfgNode]  # no es una lista de nodos, es un Tuple


class DfgTrunk(Object, DfgNode):
    """

    the first children is the HeadNode of the region dominated by this Node
    """

    leaf: DfgLeaf
    # children: tuple[DfgNode]

    value: DfgNode

    @property
    def leaf(self) -> DfgLeaf:
        return self.children[0]


class DfgApply(Object, DfgNode):
    function: DfgNode
    argument: DfgNode


class DfgSwitch(Object, DfgNode):
    class MatchPatter: ...

    # Constant
    type Match = bool | int | float | str | MatchPatter

    selector: Value
    branches: dict[Match, DfgTrunk]


class DfgLoop(Object, DfgNode):
    input: DfgNode
    iterator: DfgTrunk


type Value = Constant | DfgNode


"""
dfg build toolkit
"""

import inspect


import operator as op

current_build_context = None


class BuildContext:
    current_state: None = None

    def __enter__(self):
        global current_build_context
        self.prev = current_build_context
        current_build_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global current_build_context
        current_build_context = self.prev


def dfg_use(entity: Any) -> DfgUse:
    return DfgUse(entity=entity)


class DfgCarrier[T: DfgNode](Object, traits.Basic):
    _node: Value | None

    @classmethod
    def mk_constant(cls, value: Constant) -> DfgCarrier[DfgConstant]:
        return cls(_node=DfgConstant(value=value))

    @classmethod
    def mk_use(cls, entity: Any) -> DfgCarrier[DfgUse]:
        return cls(_node=DfgUse(entity=entity))

    @classmethod
    def mk_leaf(cls) -> DfgCarrier[DfgLeaf]:
        return cls(_node=DfgLeaf())

    @classmethod
    def mk_trunk(
        cls, leaf: DfgCarrier[DfgLeaf], value: DfgCarrier
    ) -> DfgCarrier[DfgTrunk]:
        return cls(_node=DfgTrunk(leaf=leaf._node, value=value._node))

    @classmethod
    def mk_apply(cls, function: DfgNode, argument: DfgCarrier) -> DfgCarrier[DfgApply]:
        return cls(_node=DfgApply(function=function, argument=argument._node))

    @classmethod
    def tuple(
        cls,
        *elements: tuple[DfgCarrier, ...],
        **named_elements: Dict[str, DfgCarrier],
    ):
        return cls(
            _node=DfgTuple(
                inputs=Tuple.from_args(
                    *(element._node for element in elements),
                    **{k: v._node for k, v in named_elements.items()},
                )
            ),
        )

    def _carrier_infix_operator(operator):
        used_operator = dfg_use(operator)

        def infix_operator(self: DfgCarrier, other: DfgCarrier):
            return self.mk_apply(
                function=used_operator,
                argument=self.tuple(self, other),
            )

        return infix_operator

    __lt__ = _carrier_infix_operator(op.lt)
    __gt__ = _carrier_infix_operator(op.gt)
    __le__ = _carrier_infix_operator(op.le)
    __ge__ = _carrier_infix_operator(op.ge)
    __eq__ = _carrier_infix_operator(op.eq)
    __ne__ = _carrier_infix_operator(op.ne)

    __add__ = _carrier_infix_operator(op.add)
    __sub__ = _carrier_infix_operator(op.sub)
    __mul__ = _carrier_infix_operator(op.mul)
    __truediv__ = _carrier_infix_operator(op.truediv)
    __floordiv__ = _carrier_infix_operator(op.floordiv)
    __mod__ = _carrier_infix_operator(op.mod)
    __pow__ = _carrier_infix_operator(op.pow)

    __lshift__ = _carrier_infix_operator(op.lshift)
    __rshift__ = _carrier_infix_operator(op.rshift)
    __and__ = _carrier_infix_operator(op.and_)
    __or__ = _carrier_infix_operator(op.or_)
    __xor__ = _carrier_infix_operator(op.xor)

    del _carrier_infix_operator

    GET_ITEM = dfg_use(op.getitem)
    GET_ATTR = dfg_use(getattr)

    def attr(self, name: str):
        return self.mk_apply(
            function=self.GET_ATTR,
            argument=self.tuple(self, self.mk_constant(name)),
        )

    def __call__(self, *args: Tuple[DfgCarrier], **kwargs: Dict[str, DfgCarrier]):
        return self.mk_apply(
            function=self._node,
            argument=self.tuple(*args, **kwargs),
        )

    def eval(self, evaluator: DfgEvaluator):
        return self._node

    # def switch(self, branches: dict[DfgSwitch.Match, DfgTrunk]):
    #     return self.new(value=DfgSwitch(self._node, branches))


def compile_fn(fn):
    fn_signature = inspect.signature(fn)
    fn_parameters = fn_signature.parameters

    with BuildContext() as ctx:
        leaf = DfgCarrier.mk_leaf()

        params = [leaf.attr(p.name) for p in fn_parameters.values()]

        value = fn(*params)

        # children=ctx.make_trunk

        return DfgCarrier.mk_trunk(leaf=leaf, value=value)


class DfgEvaluator[T]:
    class Context:
        def __init__(self, evaluator: DfgEvaluator, dfg_trunk: DfgTrunk):
            self.evaluator = evaluator
            self.dfg_trunk = dfg_trunk

        def __enter__(self): ...

        def __exit__(self, exc_type, exc_value, traceback): ...

    # def run(self, dfg_trunk: DfgTrunk, *args, **kwargs):
    #     return self.eval_trunk(dfg_trunk)

    def eval(self, node: DfgNode):
        match node:
            case DfgLeaf() as dfg_leaf:
                return self.eval_leaf(dfg_leaf)
            case DfgUse() as dfg_use:
                return self.eval_use(dfg_use)
            case DfgConstant() as dfg_constant:
                return self.eval_constant(dfg_constant)
            case DfgTuple() as dfg_tuple:
                return self.eval_tuple(dfg_tuple)
            case DfgApply() as dfg_apply:
                return self.eval_apply(dfg_apply)
            case DfgTrunk() as dfg_trunk:
                return self.eval_trunk(dfg_trunk)
            case DfgSwitch() as dfg_switch:
                return self.eval_switch(dfg_switch)
            case DfgLoop() as dfg_loop:
                return self.eval_loop(dfg_loop)

    def eval_leaf(self, dfg_leaf: DfgLeaf):
        raise NotImplementedError("Leaf nodes cannot be evaluated")

    def eval_use(self, dfg_use: DfgUse):
        raise NotImplementedError("Use nodes cannot be evaluated")

    def eval_constant(self, dfg_constant: DfgConstant):
        return dfg_constant.value

    def eval_trunk(self, dfg_trunk: DfgTrunk):
        with self.Context(self, dfg_trunk):
            return self.eval(dfg_trunk.value)

    def eval_apply(self, dfg_apply: DfgApply):
        function = self.eval(dfg_apply.function)
        argument = self.eval(dfg_apply.argument)

        return function, argument

    def eval_tuple(self, dfg_tuple: DfgTuple):
        return dfg_tuple.inputs.map(self.eval)

    def eval_switch(self, switch: DfgSwitch):
        return

    def eval_loop(self, loop: DfgLoop):
        return


"""
dfg evaluation toolkit
"""


def max(x, y, z):
    return x + y * z


compile_fn(max)


def ce_getattr(t: Tuple, attr: str | int):
    return t[attr]


class ConstantEvaluator(DfgEvaluator):
    """
    El evaluador conostante realiza:
    - Resolucion de entidades
    - chequeo de tipos
    - aplicacion de funciones puras
    - embedding de funciones nativas (inlining)
    - propagacion de constantes hacia funciones inlined

    Una vez ejecutado, el evaluador retorna un Dfg que representa
    el programa optimizado.

    los nodos del dfg resultante contendran metadatos que permitiran
    la desestructuracion de codigo.

    """

    global_context = {
        getattr: ce_getattr,
        op.add: lambda x, y: x + y,
        op.mul: lambda x, y: x * y,
    }

    def eval_leaf(self, dfg_leaf: DfgLeaf):
        return Tuple(x=1, y=2, z=3)

    def eval_use(self, dfg_use: DfgUse):
        """
        Resuelve entidades sustituyendolas por constantes
        """
        print("USE", dfg_use.entity)
        return self.global_context[dfg_use.entity]

    def eval_apply(self, dfg_apply: DfgApply):
        function, argument = super().eval_apply(dfg_apply)

        if isinstance(function, FunctionType):
            if isinstance(argument, Tuple):
                args, kwargs = argument.to_args()
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    # add exception context
                    raise e

        raise TypeError(f"Cannot apply {function} to {argument}")


from rich import print

print(compile_fn(max)._node)
ConstantEvaluator().eval(compile_fn(max)._node)
