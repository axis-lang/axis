from __future__ import annotations
from typing import ClassVar, Literal, Optional

from protobase import flux

from axis import syn
from axis.sem import Entity

from .item import Item
from .ref import ref_from_expr, scope_ref_from_item



class Global(Item, syn.ClassMatcher, abstract=True): ## expr.Tuple.Nominal ValueMixin or ElementMixin
    """
    <kw> <name>: <type> = <value>
    where <kw> in ["val", "var", "let", 'dyn', 'mut']
    """
    outline_keyword: ClassVar[str]  # type: ignore[override]

    key: syn.Expr | None = None
    bound: Optional[syn.Expr] = None
    value: Optional[syn.Expr] = None

    @classmethod
    def build(
        cls,
        kw: Literal["val", "var", "let", "dyn", "mut"],
        key: syn.Expr,
        *args, 
        # op1: Optional[str] = None,
        # e1: Optional[syn.Expr] = None,
        # op2: Optional[str] = None,
        # e2: Optional[syn.Expr] = None,
        #*, 
        children: syn.OutlineNode.Children,
        **kwargs
    ):
        assert kw == cls.outline_keyword, f'Expected keyword {cls.outline_keyword}, got {kw}'        
        match args:
            case (":", bound, "=", value):
                return cls(key=key, bound=bound, value=value, **kwargs)
            case (":", bound, None, None):
                return cls(key=key, bound=bound, value=None, **kwargs)
            case ("=", value, None, None):
                return cls(key=key, bound=None, value=value, **kwargs)
            case (None, None, None, None):
                return cls(key=key, bound=None, value=None, **kwargs)
            case _:
                raise ValueError(
                    f"Invalid syntax for named element: {key} {args}"
                )

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        if self.key is None:
            return frozenset()
        scope_ref = scope_ref_from_item(self)
        anchor = ref_from_expr(self.key, scope_ref)
        contributions: list[Entity.Contribution] = []
        if self.value is not None:
            contributions.append(
                Entity.Fact(
                    anchor=anchor,
                    args=(self.value,),
                    origin=self.value,
                    ctx=self,
                )
            )
        if self.bound is not None:
            contributions.append(
                Entity.Constraint(
                    anchor=anchor,
                    predicate=self.bound,
                    origin=self.bound,
                    ctx=self,
                )
            )
        return frozenset(contributions)

class Val(Global):
    outline_keyword: ClassVar = "val"

class Var(Global):
    outline_keyword: ClassVar = "var"

class Let(Global):
    outline_keyword: ClassVar = "let"

class Dyn(Global):
    outline_keyword: ClassVar = "dyn"

class Mut(Global):
    outline_keyword: ClassVar = "mut"
