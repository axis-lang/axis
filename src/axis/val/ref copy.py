from __future__ import annotations
from functools import singledispatchmethod
from typing import ClassVar, Optional, Self
from protobase import Record, cached_property
from axis import syn
from .val import Val


class Ref(Val, Record, consed=True):

    class Evaluator(Val.Evaluator['Ref']):
        """
        Evaluador de referencias globales
        """

        base: Ref # TODO: sera un mapping

        @singledispatchmethod
        def eval(self, node: syn.Statement) -> Ref:
            return super().eval(node)


    class Step(Record, frozen=True): ...

    class Member(Step, frozen=True):
        name: str

        def __str__(self) -> str:
            return self.name

    root: ClassVar[Ref]
    steps: tuple[Step, ...]

    @classmethod
    def from_expr(cls, expr: syn.Expr | str, base_ref: Optional[Ref] = None) -> Self:
        if isinstance(expr, str):
            expr = syn.Expr.parse(expr)

        if base_ref is None:
            base_ref = cls.root

        return cls.Evaluator(base_ref).eval(expr)

    @cached_property
    def parent(self) -> Optional[Self]:
        if not self.steps:
            return None
        return self.__class__(self.steps[:-1])

    @cached_property
    def parents(self) -> tuple[Self, ...]:
        return tuple(self.__class__(self.steps[:i]) for i in range(len(self.steps)))

    @property
    def is_member(self) -> bool:
        if not self.steps:
            return False
        return isinstance(self.steps[-1], self.Member)

    @property
    def name(self):
        if not self.steps:
            return "@root"
        last_step = self.steps[-1]
        if not isinstance(last_step, self.Member):
            raise ValueError("last step is not a member")
        return last_step.name
    
    def __rich_repr__(self):
        return self.__str__(),

    def __str__(self):
        if not self.steps:
            return "@root"
        return "@root." + ".".join(str(p) for p in self.steps)

    # def __len__(self):
    #     return len(self.steps)

    # def __iter__(self):
    #     return iter(self.steps)

    def parent_at(self, level: int):
        return self.__class__(self.steps[: 1 + level])

    def member(self, name: str) -> Self:
        return self.__class__(self.steps + (self.Member(name),))


Ref.root = Ref(steps=())

