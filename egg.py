# %%
from __future__ import annotations
from egglog import *


class Num(Expr):
    def __init__(self, value: i64Like) -> None: ...

    @classmethod
    def var(cls, name: StringLike) -> Num: ...

    def __add__(self, other: Num) -> Num: ...

    def __mul__(self, other: Num) -> Num: ...


egraph = EGraph()

expr1 = egraph.let("expr1", Num(2) * (Num.var("x") + Num(3)))
expr2 = egraph.let("expr2", Num(6) + Num(2) * Num.var("x"))


# @egraph.register
# def _num_rule(a: Num, b: Num, c: Num, i: i64, j: i64):
#     yield rewrite(a + b).to(b + a)
#     yield rewrite(a * (b + c)).to((a * b) + (a * c))
#     yield rewrite(Num(i) + Num(j)).to(Num(i + j))
#     yield rewrite(Num(i) * Num(j)).to(Num(i * j))


egraph.saturate()
