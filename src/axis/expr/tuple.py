from typing import ClassVar, Literal, Optional, Self

from protobase import cached_property

from axis import log, syn

from .prefix import Etc
from .sym import Sym


class Tuple(syn.Expr):
    """
    Represents a tuple expression in the AST.
    It can contain elements that are:
    - Values (e.g. `1`, `2`, `3`)
    - Named elements (e.g. `a: b`, `c = d`, `e: f = g`)
    - Spread elements (e.g. `..alpha..`, `..`)

    """

    class Element(syn.Node, abstract=True):
        grammar_context_infix: ClassVar[str] = "Element"

        @property
        def is_spread(self) -> bool:
            raise NotImplementedError

    class Positional(Element):  # PositionalElement
        "value"

        value: Optional[syn.Expr]

        def __str__(self) -> str:
            return str(self.value)

        @classmethod
        def build(cls, value: syn.Expr):
            return cls(value=value)

        @property
        def is_spread(self) -> bool:
            return isinstance(self.value, Etc)

    class Nominal(Element): # es un elemento que implementa value mixin
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
            **kwargs
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
            return isinstance(self.key, Etc)

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

    @cached_property
    def spread_positions(self) -> tuple[int, ...]:
        return tuple(i for i, e in enumerate(self.elements) if e.is_spread)

    @cached_property  # TODO: cached property can retain the raised error and rethrow it on subsequent calls
    def head_and_tail_count(self) -> tuple[int, int]:
        """
        Returns a tuple of (head_count, spread_count, tail_count).
        - head_count: Number of elements before the first spread element.
        - spread_count: Number of spread elements.
        - tail_count: Number of elements after the last spread element.
        """
        spread_positions = self.spread_positions
        if len(spread_positions) == 0:
            return len(self.elements), 0

        if len(spread_positions) > 1:
            with log.error(
                f"Tuple has {len(spread_positions)} spread positions, only one expected"
            ) as err:
                for pos in spread_positions:
                    err.with_label(
                        self.elements[pos].as_label(f"Spread element at position {pos}")
                    )
            raise ValueError("Tuple has multiple spread positions")

        head_count = spread_positions[0]
        tail_count = len(self.elements) - head_count - 1
        return head_count, tail_count

    def head_rest_and_tail_elemets(
        self, head_count: int, tail_count: int = 0
    ) -> tuple[tuple[Element, ...], tuple[Element, ...], tuple[Element, ...]]:
        """
        Returns a tuple of (head_elements, rest_elements, tail_elements).
        - head_elements: Elements before the first spread element.
        - tail_elements: Elements after the last spread element.
        - rest_elements: Elements in between, including the spread element if present.
        """
        if head_count < 0 or tail_count < 0:
            raise ValueError("Head and tail counts must be non-negative")

        if head_count + tail_count > len(self.elements):
            raise ValueError("Head and tail counts exceed total number of elements")

        head_elements = self.elements[:head_count]
        tail_elements = self.elements[-tail_count:] if tail_count > 0 else ()
        rest_elements = (
            self.elements[head_count : len(self.elements) - tail_count]
            if tail_count > 0
            else self.elements[head_count:]
        )

        return head_elements, rest_elements, tail_elements


class Shape(Tuple): ...


@syn.Matcher.impl(Tuple)
def match_tuple(self: syn.Matcher, tuple: Tuple, value: syn.Expr):

    if not isinstance(value, Tuple):
        raise self.NoMatch

    try:
        head_and_tail_count = tuple.head_and_tail_count

        value_head, value_rest, value_tail = value.head_rest_and_tail_elemets(
            *head_and_tail_count
        )
        target_head, target_rest, target_tail = tuple.head_rest_and_tail_elemets(
            *head_and_tail_count
        )

    except:
        raise self.NoMatch

    for a, b in zip(target_head, value_head):
        self.match_node(a, b)

    match target_rest:
        case (
            Tuple.Positional(value=Etc(rhs=Sym(name=wildcard_name) as target_sym)),
        ) if target_sym.is_wildcard:

            # target_etc = target_rest[0]
            # assert target_etc.is_spread, "Expected a spread element in the rest of the tuple"
            # TODO: logica de captura de valores, ampliar con bounds etc
            self.capture_value(wildcard_name, value.with_attr(elements=value_rest))

    # if len(target_rest) == 1:
    #     target_etc = target_rest[0]
    #     assert target_etc.is_spread, "Expected a spread element in the rest of the tuple"
    #     # TODO: logica de captura de valores, ampliar con bounds etc
    #     if isinstance(target_etc.expr, Sym) and target_etc.expr.is_wildcard:
    #         self.capture_value(target_etc.expr.name, value.with_attr(elements=value_rest))

    for a, b in zip(target_tail, value_tail):
        self.match_node(a, b)


@syn.Reifier.impl(Tuple)
def reify_tuple(self: syn.Reifier, tup: Tuple) -> Tuple:
    """
    Reifies a Tuple expression, resolving any wildcards or named elements.
    """
    elements = []
    for elem in tup.elements:
        match elem:
            case Tuple.Positional(
                value=Etc(rhs=Sym(name=wildcard_name) as sym)
            ) if sym.is_wildcard:
                target = self.value(wildcard_name, Tuple)
                elements.extend(target.elements)

            case elem:
                elements.append(self.reify(elem))

    return tup.with_attr(elements=tuple(elements))
