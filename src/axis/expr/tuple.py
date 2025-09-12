from multiprocessing import Value
from optparse import Option
from token import OP
from typing import ClassVar, Literal, Optional, Self
from protobase import cached_property
from axis import syn, log

# from .etc import Etc
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
        grammar_context_infix: ClassVar[Literal['Element']] = 'Element'


    class Value(Element):
        "value"

        value: Optional[syn.Expr]

        def __str__(self) -> str:
            return str(self.value)
        
        @classmethod
        def build(cls, value: syn.Expr):
            return cls(value=value)

    class Spread(Element):
        "..spread"

        etc: Optional[syn.Expr]

        @classmethod
        def build(cls, ellipsis: Literal['..'], etc: Optional[syn.Expr]=None):
            return cls(etc=etc)

        def __str__(self) -> str:
            if self.etc:
                return f'..{self.etc}'
            return '..'

    class Nominal(Element):
        "name: bound = value"

        key: syn.Expr = None
        bound: Optional[syn.Expr] = None
        value: Optional[syn.Expr] = None

        @classmethod
        def build(cls, key: syn.Expr, op1: Optional[str] = None, e1: Optional[syn.Expr] = None, op2: Optional[str] = None, e2: Optional[syn.Expr] = None):
            match (op1, e1, op2, e2):
                case (":", bound, "=", value):
                    return cls(key=key, bound=bound, value=value)
                case (":", bound, None, None):
                    return cls(key=key, bound=bound, value=None)
                case ("=", value, None, None):
                    return cls(key=key, bound=None, value=value)
                case (None, None, None, None):
                    return cls(key=key, bound=None, value=None)
                case _:
                    raise ValueError(f"Invalid syntax for named element: {key} {op1} {e1} {op2} {e2}")


        # @property
        # def is_wildcard(self) -> bool:
        #     return self.key[0] == "$"

        def __str__(self) -> str:
            if self.bound and self.value:
                return f'{self.key}: {self.bound} = {self.value}'
            if self.bound:
                return f'{self.key}: {self.bound}'
            if self.value:
                return f'{self.key} = {self.value}'
            return str(self.key)

    elements: tuple[Element, ...]

    @classmethod
    def build(cls, *elements: Element) -> Self:
        return cls(elements=elements)

    def __str__(self) -> str:
        return '(' + ', '.join(str(e) for e in self.elements) + ')'

    def __len__(self) -> int:
        return len(self.elements)

    def __getitem__(self, index: int | slice) -> Element:
        return self.elements[index]

    def __iter__(self):
        return iter(self.elements)

    @cached_property
    def spread_positions(self) -> tuple[int, ...]:
        return tuple(
            i for i, e in enumerate(self.elements) if isinstance(e, self.Spread)
        )

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
                        self.elements[pos], f"Spread element at position {pos}"
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


class Shape(Tuple):
    ...

# @syn.AstBuilder.build.register(syn.AxisParser.TupleContext | syn.AxisParser.ShapeContext)
# def build_tuple_ast(
#     self,
#     _,
#     *elements: tuple[Tuple.Element, ...],
# ) -> Tuple:
#     return Tuple(elements=elements)

# syn.AstBuilder.decl_pass_context(syn.AxisParser.ElementContext)

# @syn.AstBuilder.build.register(syn.AxisParser.ValueElementContext)
# def build_value_element_ast(
#     self,
#     _,
#     value: syn.Expr,
# ):
#     return Tuple.Value(value=value)



# @syn.AstBuilder.build.register(syn.AxisParser.ValueElementContext)
# def build_value_element_ast(
#     self,
#     _,
#     value: syn.Expr,
# ):
#     return Tuple.Value(value=value)


# @syn.AstBuilder.build.register(syn.AxisParser.SpreadElementContext)
# def build_spread_element_ast(
#     self,
#     _,
#     ellipsis: str,
#     etc: Optional[syn.Expr] = None,
# ):
#     assert ellipsis == "..", "Expected '..' for spread element"
#     return Tuple.Spread(etc=etc)


# @syn.AstBuilder.build.register(syn.AxisParser.NominalElementContext)
# def build_nominal_element_ast(
#     self,
#     _,
#     name: str,
#     op1: Optional[str] = None,
#     e1: Optional[syn.Expr] = None,
#     op2: Optional[str] = None,
#     e2: Optional[syn.Expr] = None,
# ):
#     if op1 == ":":
#         if op2 is None:
#             return Tuple.Nominal(key=name, bound=e1, value=None)
#         assert op2 == "=", "Expected '=' after ':' in named element"
#         return Tuple.Nominal(key=name, bound=e1, value=e2)

#     assert op1 == "=", "Expected '=' before named element"
#     assert op2 is None, "Expected no operator after '=' in named element"
#     return Tuple.Nominal(key=name, bound=None, value=e1)


@syn.Matcher.match.register(Tuple)
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

    if len(target_rest) == 1:
        target_spread = target_rest[0]
        assert isinstance(
            target_spread, Tuple.Spread
        ), "Expected a spread element in the rest of the tuple"

        if isinstance(target_spread.etc, Sym) and target_spread.etc.is_wildcard:
            self.capture_value(target_spread.etc.name, value.with_attr(elements=value_rest))

    for a, b in zip(target_tail, value_tail):
        self.match_node(a, b)


@syn.Reifier.reify.register(Tuple)
def reify_tuple(self: syn.Reifier, tup: Tuple) -> Tuple:
    """
    Reifies a Tuple expression, resolving any wildcards or named elements.
    """
    elements = []
    for elem in tup.elements:
        if (
            isinstance(elem, Tuple.Spread)
            and isinstance(elem.etc, Sym)
            and elem.etc.is_wildcard
        ):
            target = self.value(elem.etc.name, Tuple)

            # if elem.etc.name[1:] not in self.values:
            #     raise ValueError(f"Unresolved wildcard: {elem.etc.name}")

            # target = self.values[elem.etc.name]

            # if not isinstance(target, Tuple):
            #     raise ValueError(
            #         f"Expected a Tuple for wildcard {elem.etc.name}, got {type(target)}"
            #     )

            elements.extend(target.elements)
            continue

        elements.append(self.reify(elem))

    return tup.with_attr(elements=tuple(elements))
