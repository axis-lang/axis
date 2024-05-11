# %%
"""
dfg evaluation toolkit
"""

import operator as op
from types import FunctionType
from typing import TypeAlias

from rich import print

from axis.components import dfg
from axis.components.dfg.evaluation import EvaluationContext
from axis.components.tuple import Tuple
from axis.components.entity import know

Constant: TypeAlias = str | int | float | bool | FunctionType

GLOBALS = {  # GLOBAL_SCOPE
    know.GET_ATTR: op.getitem,
    know.ADD: op.add,
    know.MUL: op.mul,
    know.GT: op.gt,
    know.LT: op.lt,
    know.EQ: op.eq,
    know.NE: op.ne,
    know.LE: op.le,
    know.GE: op.ge,
    know.SUB: op.sub,
    know.TRUEDIV: op.truediv,
    know.FLOORDIV: op.floordiv,
    know.MOD: op.mod,
    know.POW: op.pow,
    know.LSHIFT: op.lshift,
    know.RSHIFT: op.rshift,
    know.AND: op.and_,
    know.OR: op.or_,
    know.XOR: op.xor,
    know.PRINT: print,
}


@dfg.compile
def test_add(a, b):
    return a + b


@dfg.compile
def test_apply(x, y, z):
    return test_add(a=x, b=y) * z


@dfg.compile
def test_max(a, b):
    return dfg.Switch.build(
        a > b,
        {
            True: a,
            False: b,
        },
    )


with EvaluationContext(Tuple(x=1, y=2, z=3), scope=GLOBALS):
    print(dfg.eval(test_apply))

with EvaluationContext(Tuple(a=10, b=5), scope=GLOBALS):
    print(dfg.eval(test_max))


with dfg.VisualizationContext(Tuple(x=1, y=2, z=3), scope=GLOBALS):
    dfg.eval(test_apply)

# vis.graph.render("max", format="png", view=True)
