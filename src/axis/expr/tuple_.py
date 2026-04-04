from __future__ import annotations

from typing import Any, ClassVar, Optional, Self

import protomorph as pm

from axis import syn, expr, log

from .lowering import build_tuple_bound


class Tuple(syn.Expr):

    class Element(syn.Node, abstract=True):
        grammar_context_infix: ClassVar[str] = "Element"

        @property
        def is_spread(self) -> bool:
            raise NotImplementedError

        @property
        def is_ellipsis(self) -> bool:
            raise NotImplementedError

        @property
        def name(self) -> str:
            log.error("Unsupported tuple element").label(self).throw()

    class Positional(Element):  # PositionalElement
        value: syn.Expr

        def __str__(self) -> str:
            return str(self.value)

        @classmethod
        def build(cls, value: syn.Expr):
            return cls(value=value)

        @property
        def is_spread(self) -> bool:
            return isinstance(self.value, expr.Etc)

        @property
        def is_ellipsis(self) -> bool:
            return isinstance(self.value, expr.Lit) and self.value.is_ellipsis

        @property
        def name(self) -> str:
            value = self.value
            if value is None:
                log.error("Positional element requires a value").label(self).throw()
            from axis import expr as expr_module

            return expr_module.name_of(value)

    class Nominal(Element):  # es un elemento que implementa value mixin
        "name: bound = value"

        key: syn.Expr
        bound: Optional[syn.Expr]
        value: Optional[syn.Expr]

        @classmethod
        def build(
            cls,
            key: syn.Expr,
            op1: Optional[str] = None,
            e1: Optional[syn.Expr] = None,
            op2: Optional[str] = None,
            e2: Optional[syn.Expr] = None,
            **kwargs,
        ):
            match (op1, e1, op2, e2):
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
                        f"Invalid syntax for named element: {key} {op1} {e1} {op2} {e2}"
                    )

        @property
        def is_spread(self) -> bool:
            return isinstance(self.key, expr.Etc)

        @property
        def is_ellipsis(self) -> bool:
            return isinstance(self.key, expr.Lit) and self.key.is_ellipsis

        @property
        def name(self) -> str:
            from axis import expr as expr_module

            return expr_module.to_slot_name(self.key)

        # @property
        # def is_wildcard(self) -> bool:
        #     return self.key[0] == "$"

        def __str__(self) -> str:
            if self.bound and self.value:
                return f"{self.key}: {self.bound} = {self.value}"
            if self.bound:
                return f"{self.key}: {self.bound}"
            if self.value:
                return f"{self.key} = {self.value}"
            return str(self.key)

    ##

    elements: tuple[Element, ...]

    @classmethod
    def build(cls, *elements: Element, **kwargs) -> Self:
        return cls(elements=elements, **kwargs)

    def __str__(self) -> str:
        return "(" + ", ".join(str(e) for e in self.elements) + ")"

    def __len__(self) -> int:
        return len(self.elements)

    def __getitem__(self, index: int | slice) -> Element | tuple[Element, ...]:
        return self.elements[index]

    def __iter__(self):
        return iter(self.elements)

    def to_bound(self, scope: syn.ScopeLike) -> pm.Result[log.Report, Any]:
        return build_tuple_bound(self.elements, scope)


class Shape(Tuple): ...
