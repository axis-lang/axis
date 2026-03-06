from __future__ import annotations
from typing import ClassVar, Literal, Optional

from protobase import flux, slot_cached_property

from axis import dom, expr, syn
from axis.sem import Entity, Scope

from .item import Item
from .scopes import parent_scope



class Global(Item, syn.ClassMatcher, abstract=True): ## expr.Tuple.Nominal ValueMixin or ElementMixin
    """
    <kw> <name>: <type> = <value>
    where <kw> in ["val", "var", "let", 'dyn', 'mut']
    """
    outline_keyword: ClassVar[str]  # type: ignore[override]

    key: syn.Expr | None = None
    bound: Optional[syn.Expr] = None
    value: Optional[syn.Expr] = None

    @slot_cached_property
    def anchor(self) -> dom.Anchor:
        parent = self.parent
        if parent is None:
            raise ValueError("Global requires a parent to build its anchor")
        return parent.anchor

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
        scope_ref = self.anchor
        target = expr.to_spec_ref(self.key, scope_ref)
        if target is None:
            return frozenset()
        contributions: list[Entity.Contribution] = []
        if scope_ref is not None:
            contributions.append(
                Entity.Member(
                    anchor=scope_ref,
                    name=expr.name_of(self.key),
                    target=target,
                    origin=self.key,
                    ctx=self,
                )
            )
        return frozenset(contributions)

    @flux.property
    def scope(self) -> Scope:
        scope_name = expr.name_of(self.key) if self.key is not None else None
        builder = Scope.Builder(name=scope_name, parent=parent_scope(self))
        return builder.build()

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
