from __future__ import annotations

from protobase import frozendict

from axis import expr, log, syn

from .member import Member
from .sym import Sym
from .tuple_ import Tuple


def _spread_positions(tuple_: Tuple) -> tuple[int, ...]:
    return tuple(i for i, element in enumerate(tuple_.elements) if element.is_spread)


def _spread_head_and_tail_count(tuple_: Tuple) -> tuple[int, int]:
    spread_positions = _spread_positions(tuple_)
    if len(spread_positions) == 0:
        return len(tuple_.elements), 0

    if len(spread_positions) > 1:
        report = log.error(
            f"Tuple has {len(spread_positions)} spread positions, only one expected"
        )
        for pos in spread_positions:
            report = report.label(
                tuple_.elements[pos],
                f"Spread element at position {pos}",
            )
        report.emit()
        raise ValueError("Tuple has multiple spread positions")

    head_count = spread_positions[0]
    tail_count = len(tuple_.elements) - head_count - 1
    return head_count, tail_count


def _split_tuple_elements(
    tuple_: Tuple,
    head_count: int,
    tail_count: int = 0,
) -> tuple[tuple[Tuple.Element, ...], tuple[Tuple.Element, ...], tuple[Tuple.Element, ...]]:
    if head_count < 0 or tail_count < 0:
        raise ValueError("Head and tail counts must be non-negative")

    if head_count + tail_count > len(tuple_.elements):
        raise ValueError("Head and tail counts exceed total number of elements")

    head_elements = tuple_.elements[:head_count]
    tail_elements = tuple_.elements[-tail_count:] if tail_count > 0 else ()
    rest_elements = (
        tuple_.elements[head_count : len(tuple_.elements) - tail_count]
        if tail_count > 0
        else tuple_.elements[head_count:]
    )

    return head_elements, rest_elements, tail_elements


@syn.Matcher.impl_rule(Sym)
def match_sym(self: syn.Matcher, sym: Sym, value: syn.Expr) -> syn.MatchResult | None:
    spec = sym.match_spec
    if spec.match_all:
        if sym.at and sym.at != value.__class__.__name__:
            return None
        return syn.MatchResult.empty()

    if not isinstance(value, Sym):
        return None
    if sym.name != value.name or sym.at != value.at:
        return None
    return syn.MatchResult.empty()


@syn.Matcher.impl_rule(Member)
def match_member(self: syn.Matcher, pattern: Member, value: syn.Expr) -> syn.MatchResult | None:
    if not isinstance(value, Member):
        return None

    if not pattern.is_wildcard and pattern.name != value.name:
        return None

    return self.match(pattern.of, value.of)


@syn.Matcher.impl_rule(Tuple)
def match_tuple(
    self: syn.Matcher, tuple: Tuple, value: syn.Expr
) -> syn.MatchResult | None:
    if not isinstance(value, Tuple):
        return None

    try:
        head_and_tail_count = _spread_head_and_tail_count(tuple)
        value_head, value_rest, value_tail = _split_tuple_elements(value, *head_and_tail_count)
        target_head, target_rest, target_tail = _split_tuple_elements(tuple, *head_and_tail_count)
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
