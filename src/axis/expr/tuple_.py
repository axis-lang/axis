from typing import ClassVar, Literal, Optional, Self

from protobase import slot_cached_property, frozendict

from axis import syn, expr, log


class Tuple(syn.Expr):

    class Element(syn.Node, abstract=True):
        grammar_context_infix: ClassVar[str] = "Element"

        @property
        def is_variadic(self) -> bool:
            return self.is_spread or self.is_ellipsis

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

    @slot_cached_property
    def variadic_offsets(self) -> tuple[int, ...]:
        return tuple(i for i, e in enumerate(self.elements) if e.is_variadic)

    @property
    def is_variadic(self) -> bool:
        return len(self.variadic_offsets) > 0

    @property
    def positional_count(self) -> tuple[int, int]:
        variadic_offsets = self.variadic_offsets
        if len(variadic_offsets) == 0:
            return len(self.elements), 0

        if len(variadic_offsets) > 1:
            report = log.error(
                f"Tuple has {len(variadic_offsets)} variadic positions, only one expected"
            )
            for pos in variadic_offsets:
                report = report.label(
                    self.elements[pos],
                    f"Variadic element at position {pos}",
                )
            report.throw()

        head_count = variadic_offsets[0]
        tail_count = len(self.elements) - variadic_offsets[-1]  # - 1
        return head_count, tail_count

    @property
    def split_positional_elements(
        self,
    ) -> tuple[tuple[Element, ...], tuple[Element, ...], tuple[Element, ...]]:
        head_count, tail_count = self.positional_count
        return (
            self.elements[:head_count],
            (
                self.elements[head_count : len(self.elements) - tail_count]
                if tail_count > 0
                else self.elements[head_count:]
            ),
            self.elements[-tail_count:] if tail_count > 0 else (),
        )

    @slot_cached_property
    def spread_positions(self) -> tuple[int, ...]:
        "Returns the positions of spread elements in the tuple."
        return tuple(i for i, e in enumerate(self.elements) if e.is_spread)

    @slot_cached_property
    def inline_prefix(self) -> tuple[tuple[Element, ...], bool]:
        elements = self.elements
        spread_index: int | None = None
        for index, element in enumerate(elements):
            if element.is_spread:
                if index != len(elements) - 1:
                    (
                        log.error("Variadic marker must be final element")
                        .label(element)
                        .throw()
                    )
                spread_index = index
                break
        if spread_index is None:
            return elements, False
        return elements[:spread_index], True

    @slot_cached_property  # TODO: cached property can retain the raised error and rethrow it on subsequent calls
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
            report = log.error(
                f"Tuple has {len(spread_positions)} spread positions, only one expected"
            )
            for pos in spread_positions:
                report = report.label(
                    self.elements[pos],
                    f"Spread element at position {pos}",
                )
            report.emit()
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


@syn.Matcher.impl_rule(Tuple)
def match_tuple(
    self: syn.Matcher, tuple: Tuple, value: syn.Expr
) -> syn.MatchResult | None:

    if not isinstance(value, Tuple):
        return None

    try:
        head_and_tail_count = tuple.head_and_tail_count

        value_head, value_rest, value_tail = value.head_rest_and_tail_elemets(
            *head_and_tail_count
        )
        target_head, target_rest, target_tail = tuple.head_rest_and_tail_elemets(
            *head_and_tail_count
        )

    except ValueError:
        return None

    result = syn.MatchResult.empty()

    for a, b in zip(target_head, value_head):
        head_result = self.match(a, b)
        if head_result is None:
            return None
        result = syn.MatchResult.unify(result, head_result)

    match target_rest:
        case (Tuple.Positional(value=expr.Etc(rhs=rhs_pattern)),):
            if isinstance(rhs_pattern, syn.MatchCapture):
                if not rhs_pattern.variadic:
                    rhs_pattern = syn.MatchCapture(
                        name_by_candidate=rhs_pattern.name_by_candidate,
                        subpattern=rhs_pattern.subpattern,
                        variadic=True,
                    )
            elif isinstance(rhs_pattern, syn.MatchGoal):
                subpattern = rhs_pattern.subpattern
                if isinstance(subpattern, syn.MatchCapture) and not subpattern.variadic:
                    subpattern = syn.MatchCapture(
                        name_by_candidate=subpattern.name_by_candidate,
                        subpattern=subpattern.subpattern,
                        variadic=True,
                    )
                rhs_pattern = syn.MatchGoal(
                    subpattern=subpattern,
                    candidates=rhs_pattern.candidates,
                )
            elif isinstance(rhs_pattern, expr.Sym) and rhs_pattern.is_wildcard:
                candidate = syn.MatchCandidate(result_type=None, schema=None)
                capture = syn.MatchCapture(
                    name_by_candidate=frozendict({candidate: rhs_pattern.name[1:]}),
                    subpattern=rhs_pattern,
                    variadic=True,
                )
                rhs_pattern = syn.MatchGoal(
                    subpattern=capture,
                    candidates=frozenset((candidate,)),
                )
            else:
                rhs_pattern = None

            if rhs_pattern is not None:
                rest_tuple = value.with_attr(elements=value_rest)
                rest_result = self.match(rhs_pattern, rest_tuple)
                if rest_result is None:
                    return None
                result = syn.MatchResult.unify(result, rest_result)

    for a, b in zip(target_tail, value_tail):
        tail_result = self.match(a, b)
        if tail_result is None:
            return None
        result = syn.MatchResult.unify(result, tail_result)

    return result


@syn.Reifier.impl(Tuple)
def reify_tuple(self: syn.Reifier, tup: Tuple) -> Tuple:
    """
    Reifies a Tuple expression, resolving any wildcards or named elements.
    """
    elements = []
    for elem in tup.elements:
        match elem:
            case Tuple.Positional(
                value=expr.Etc(rhs=expr.Sym(name=wildcard_name) as sym)
            ) if sym.is_wildcard:
                target = self.value(wildcard_name, Tuple)
                elements.extend(target.elements)

            case elem:
                elements.append(self.reify(elem))

    return tup.with_attr(elements=tuple(elements))
