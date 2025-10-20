from __future__ import annotations
from typing import ClassVar, Literal, Optional
from axis import syn

from typing import ClassVar, Literal
from axis import syn



class Global(syn.SegregatedItem, frozen=True, abstract=True): ## expr.Tuple.Nominal ValueMixin or ElementMixin
    """
    <kw> <name>: <type> = <value>
    where <kw> in ["val", "var", "let", 'dyn', 'mut']
    """
    outline_keyword: ClassVar[Literal["val", "var", "let", "dyn", "mut"]]

    key: syn.Expr
    bound: Optional[syn.Expr]
    value: Optional[syn.Expr]

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

class Val(Global, frozen=True):
    outline_keyword: ClassVar = "val"

class Var(Global, frozen=True):
    outline_keyword: ClassVar = "var"

class Let(Global, frozen=True):
    outline_keyword: ClassVar = "let"

class Dyn(Global, frozen=True):
    outline_keyword: ClassVar = "dyn"

class Mut(Global, frozen=True):
    outline_keyword: ClassVar = "mut"

