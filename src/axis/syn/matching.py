"""
Matching

This module documents the matching contract used across the project.
Matching is functional: it produces a result object and never mutates state.

Core concepts
- MatchExpr: AST nodes used only for matching.
- MatchCapture: wraps a subpattern and records captured values per candidate.
- MatchGoal: leaf node that carries one or more candidates.
- MatchCandidate: typed or untyped goal for resolution.
- MatchSwitch: lookup node with priority order (literal -> any -> match_all).
- MatchResult: immutable bundle of candidates and captures.

Matcher contract
- Matcher.match(pattern, value) returns MatchResult or None.
- MatchResult.unify(a, b) merges candidates and captures.
- MatchCandidate is applied at the end to validate and build the output.

Captures
- Captures are only produced by MatchCapture nodes.
- Each capture records a value and resolves a name per candidate.
- Variadic captures use MatchCapture(variadic=True).

Goals and schemas
- MatchCandidate can be typed (result_type) or untyped (for the evaluator).
- If typed, the candidate uses the class annotations as a schema.
- If untyped, the candidate returns a frozendict of captures.

Projections
- Projections are defined per AST node through Node.as_(type).
- If a goal expects a non-Expr type, resolution calls as_ on the captured node.
- Missing projections raise ValueError.
- If the goal expects an Expr subclass, the value must already be that type.

Switch priority
MatchSwitch tries rules in order:
1) literal filters
2) filters with Any
3) match_all

Ambiguous filters at the same priority level raise ValueError.
"""

from __future__ import annotations

from functools import singledispatchmethod
from types import UnionType
from typing import Any, ClassVar, Iterable, Self, Union, cast, get_args, get_origin

from protobase import Inmutable, Record, attrs_of, frozendict, is_abstract

from .node import Expr, Node


class MatchAny:
    def __repr__(self) -> str:
        return "Any"


ANY = MatchAny()


class MatchExpr(Expr, abstract=True):
    pass


class MatchCandidate(Inmutable):
    result_type: type["ClassMatcher"] | None = None
    schema: frozendict[str, type] | None = None

    def __hash__(self) -> int:
        return hash((self.result_type, self.schema))

    def apply(self, result: "MatchResult") -> object | None:
        values = result.values_for(self)
        if values is None:
            return None
        if self.result_type is None:
            return frozendict(values)
        return self.result_type(**values)


class MatchGoal(MatchExpr):
    subpattern: Expr | None = None
    candidates: frozenset[MatchCandidate] = frozenset()

    def __str__(self):
        return f"{{ {self.subpattern} }}"


class MatchCapture(MatchExpr):
    name_by_candidate: frozendict[MatchCandidate, str]
    subpattern: Expr
    variadic: bool = False


MatchFilter = tuple


class MatchSwitch(MatchExpr):
    literals: frozendict[MatchFilter, Expr]
    anys: frozendict[MatchFilter, Expr]
    match_all: Expr | None = None


class CaptureEvent(Inmutable):
    capture: MatchCapture
    value: Node | tuple[Node, ...]


class MatchResult(Inmutable):
    candidates: frozenset[MatchCandidate] = frozenset()
    captures: tuple[CaptureEvent, ...] = ()

    @classmethod
    def empty(cls) -> "MatchResult":
        return cls()

    @classmethod
    def from_goal(cls, goal: MatchGoal) -> "MatchResult":
        return cls(candidates=frozenset(goal.candidates))

    @classmethod
    def from_capture(cls, capture: MatchCapture, value: Node | tuple[Node, ...]) -> "MatchResult":
        return cls(captures=(CaptureEvent(capture=capture, value=value),))

    @classmethod
    def unify(cls, left: "MatchResult", right: "MatchResult") -> "MatchResult":
        merged = cls(
            candidates=left.candidates | right.candidates,
            captures=left.captures + right.captures,
        )
        if not merged.candidates:
            return merged
        filtered = frozenset(
            candidate
            for candidate in merged.candidates
            if merged.values_for(candidate) is not None
        )
        if filtered == merged.candidates:
            return merged
        return cls(candidates=filtered, captures=merged.captures)

    def values_for(self, candidate: MatchCandidate) -> dict[str, Any] | None:
        values: dict[str, Any] = {}
        for event in self.captures:
            name = event.capture.name_by_candidate.get(candidate)
            if name is None:
                continue
            value = event.value
            if candidate.schema is not None:
                if name not in candidate.schema:
                    return None
                expected = candidate.schema[name]
                value = _project_value(value, expected)
            if name in values and values[name] != value:
                return None
            values[name] = value
        return values


def _is_expr_value(value: Any) -> bool:
    return isinstance(value, Node)


def _is_expr_sequence(value: Any) -> bool:
    if not isinstance(value, (tuple, list, frozenset)):
        return False
    return any(isinstance(item, Node) for item in value)


def _hashable(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, set):
        return frozenset(_hashable(v) for v in value)
    if isinstance(value, dict):
        return frozendict((k, _hashable(v)) for k, v in value.items())
    return value


def _match_filter(expr: Expr) -> MatchFilter:
    spec = expr.match_spec
    tokens = []
    for attr, value in attrs_of(expr).items():
        if _is_expr_value(value) or _is_expr_sequence(value):
            continue
        if attr in spec.filter_any:
            tokens.append(ANY)
        else:
            tokens.append(_hashable(value))
    return (type(expr), *tokens)


def _filter_has_any(match_filter: MatchFilter) -> bool:
    return ANY in match_filter[1:]


def _filters_overlap(a: MatchFilter, b: MatchFilter) -> bool:
    if a[0] is not b[0]:
        return False
    if len(a) != len(b):
        return False
    for left, right in zip(a[1:], b[1:]):
        if left is ANY or right is ANY:
            continue
        if left != right:
            return False
    return True


def _patterns_from_pairs(
    pairs: Iterable[tuple[Expr, frozenset[MatchCandidate] | MatchCandidate]]
):
    result: dict[Expr, frozenset[MatchCandidate]] = {}
    for expr, candidates in pairs:
        candidate_set = (
            candidates if isinstance(candidates, frozenset) else frozenset((candidates,))
        )
        if expr in result:
            result[expr] = result[expr] | candidate_set
        else:
            result[expr] = candidate_set
    return result


def merge(patterns: dict[Expr, frozenset[MatchCandidate]]) -> Expr:
    if not patterns:
        raise ValueError("merge() requires at least one pattern")

    match_all_items = [
        (expr, candidates)
        for expr, candidates in patterns.items()
        if expr.match_spec.match_all
    ]

    match_all_expr: Expr | None = None
    if match_all_items:
        match_all_expr = _reify_group(_patterns_from_pairs(match_all_items))
        if len(patterns) == 1:
            return match_all_expr
        patterns = {
            expr: candidates
            for expr, candidates in patterns.items()
            if expr is not match_all_items[0][0]
        }

    groups: dict[MatchFilter, dict[Expr, frozenset[MatchCandidate]]] = {}
    for expr, candidates in patterns.items():
        match_filter = _match_filter(expr)
        groups.setdefault(match_filter, {})[expr] = candidates

    literals: dict[MatchFilter, Expr] = {}
    anys: dict[MatchFilter, Expr] = {}

    for match_filter, group in groups.items():
        reified = _reify_group(group)
        if _filter_has_any(match_filter):
            for existing in anys:
                if _filters_overlap(existing, match_filter):
                    raise ValueError(
                        "Ambiguous match filters with Any: "
                        f"{existing} vs {match_filter}"
                    )
            anys[match_filter] = reified
        else:
            literals[match_filter] = reified

    if not literals and not anys:
        if match_all_expr is None:
            raise ValueError("MatchSwitch has no viable branches")
        return match_all_expr

    if len(literals) + len(anys) == 1 and match_all_expr is None:
        return next(iter(literals.values() or anys.values()))

    return MatchSwitch(
        literals=frozendict(literals),
        anys=frozendict(anys),
        match_all=match_all_expr,
    )


def _reify_group(group: dict[Expr, frozenset[MatchCandidate]]) -> Expr:
    patterns = list(group.keys())
    first = patterns[0]
    target_type = type(first)

    attrs: dict[str, Any] = {}
    has_expr_attrs = False
    pairs = list(group.items())

    for attr, value in attrs_of(first).items():
        values = [getattr(pattern, attr) for pattern, _ in pairs]
        if _is_expr_value(value):
            has_expr_attrs = True
            sub_pairs = [(v, goals) for (pattern, goals), v in zip(pairs, values)]
            subpatterns = _patterns_from_pairs(sub_pairs)
            attrs[attr] = merge(subpatterns)
            continue

        if _is_expr_sequence(value):
            has_expr_attrs = True
            lengths = {len(v) for v in values}
            if len(lengths) != 1:
                raise ValueError(
                    f"Ambiguous sequence length for {target_type.__name__}.{attr}"
                )
            seq_len = lengths.pop()
            merged_items = []
            for index in range(seq_len):
                sub_pairs = [
                    (values[item_index][index], pairs[item_index][1])
                    for item_index in range(len(pairs))
                ]
                subpatterns = _patterns_from_pairs(sub_pairs)
                merged_items.append(merge(subpatterns))
            attrs[attr] = tuple(merged_items)
            continue

        if attr in first.match_spec.filter_any:
            attrs[attr] = values[0]
            continue
        if not all(v == values[0] for v in values):
            raise ValueError(
                f"Ambiguous literal value for {target_type.__name__}.{attr}"
            )
        attrs[attr] = values[0]

    candidates: set[MatchCandidate] = set()
    for candidate_set in group.values():
        candidates.update(candidate_set)

    merged_expr: Expr = target_type(**attrs)

    name_by_candidate: dict[MatchCandidate, str] = {}
    for pattern, candidate_set in pairs:
        capture_name = pattern.match_spec.capture_name
        if capture_name is None:
            continue
        for candidate in candidate_set:
            existing = name_by_candidate.get(candidate)
            if existing is None:
                name_by_candidate[candidate] = capture_name
            elif existing != capture_name:
                raise ValueError(
                    "Conflicting capture names for candidate "
                    f"{candidate.result_type}: {existing} vs {capture_name}"
                )

    if name_by_candidate:
        for candidate, capture_name in name_by_candidate.items():
            if candidate.schema is None:
                continue
            if capture_name not in candidate.schema:
                raise ValueError(
                    f"Capture '{capture_name}' not found in goal schema"
                )
            expected = candidate.schema[capture_name]
            if _is_expr_expected(expected):
                continue
            if not first.match_spec.match_all:
                projection_candidates = _projection_candidates(expected)
                if projection_candidates and not any(
                    type(first).can_project(candidate_type)
                    for candidate_type in projection_candidates
                ):
                    raise ValueError(
                        f"No projection from {type(first).__name__} to {expected}"
                    )
        merged_expr = MatchCapture(
            name_by_candidate=frozendict(name_by_candidate),
            subpattern=merged_expr,
        )

    if not has_expr_attrs:
        merged_expr = MatchGoal(
            subpattern=merged_expr,
            candidates=frozenset(candidates),
        )

    return merged_expr


class Matcher(Record):
    @classmethod
    def from_str(cls, *patterns: Expr | str) -> "Matcher.Evaluator":
        return cls.Evaluator.from_expr(*patterns)

    @singledispatchmethod
    def match(self, pattern: Any, value: Any) -> MatchResult | None:
        if pattern == value:
            return MatchResult.empty()
        return None

    @classmethod
    def impl_rule(cls, target_type: type[Node]):
        def decorator(func):
            cls.match.register(target_type, func)  # type: ignore[attr-defined]
            return func
        return decorator

    @match.register
    def match_matchswitch(self, switch: MatchSwitch, value: Any) -> MatchResult | None:
        if not isinstance(value, Expr):
            return None
        match_filter = _match_filter(value)
        target = switch.literals.get(match_filter)
        if target is not None:
            return self.match(target, value)

        candidate: Expr | None = None
        for filter_key, expr in switch.anys.items():
            if _filters_overlap(filter_key, match_filter):
                if candidate is not None:
                    raise ValueError(
                        f"Ambiguous match_any filters for {value}: {filter_key}"
                    )
                candidate = expr

        if candidate is not None:
            return self.match(candidate, value)

        if switch.match_all is not None:
            return self.match(switch.match_all, value)

        return None

    @match.register
    def match_matchcapture(self, capture: MatchCapture, value: Any) -> MatchResult | None:
        result = self.match(capture.subpattern, value)
        if result is None:
            return None
        capture_result = MatchResult.from_capture(capture, value)
        return MatchResult.unify(result, capture_result)

    @match.register
    def match_matchgoal(self, goal: MatchGoal, value: Any) -> MatchResult | None:
        if goal.subpattern is None:
            raise ValueError("MatchGoal missing subpattern")
        result = self.match(goal.subpattern, value)
        if result is None:
            return None
        return MatchResult.unify(result, MatchResult.from_goal(goal))

    @match.register
    def match_node(self, pattern: Node, value: Any) -> MatchResult | None:
        if not isinstance(value, type(pattern)):
            return None
        result = MatchResult.empty()
        for attr, attr_value in attrs_of(pattern).items():
            res = self.match(attr_value, getattr(value, attr))
            if res is None:
                return None
            result = MatchResult.unify(result, res)
        return result

    @match.register
    def match_tuple(self, pattern: tuple, value: Any) -> MatchResult | None:
        if not isinstance(value, tuple):
            return None
        if len(pattern) != len(value):
            return None
        result = MatchResult.empty()
        for left, right in zip(pattern, value):
            res = self.match(left, right)
            if res is None:
                return None
            result = MatchResult.unify(result, res)
        return result

    class Evaluator(Record):
        patterns: tuple[Expr, ...]
        _match_tree: Expr | None = None

        def _tree(self) -> Expr:
            if self._match_tree is None:
                candidate = MatchCandidate(result_type=None, schema=None)
                goals = {pattern: frozenset((candidate,)) for pattern in self.patterns}
                self._match_tree = merge(goals)
            return self._match_tree

        def __call__(self, expr: Expr | str) -> frozendict[str, Any] | None:
            if isinstance(expr, str):
                expr = Expr.from_str(expr)
            matcher = Matcher()
            result = matcher.match(self._tree(), expr)
            if result is None or not result.candidates:
                return None
            viable = [
                candidate
                for candidate in result.candidates
                if result.values_for(candidate) is not None
            ]
            if not viable:
                return None
            if len(viable) != 1:
                raise ValueError("Ambiguous candidates in evaluator result")
            candidate = viable[0]
            resolved = candidate.apply(result)
            if resolved is None:
                return None
            return cast(frozendict[str, Any], resolved)

        @classmethod
        def from_expr(cls, *patterns: Expr | str) -> Self:
            items = tuple(
                Expr.from_str(pattern) if isinstance(pattern, str) else pattern
                for pattern in patterns
            )
            return cls(patterns=items)


class ClassMatcher(Inmutable, abstract=True):
    match_patterns: ClassVar[tuple[Expr, ...]]
    __match_tree__: ClassVar[Expr | None] = None

    @classmethod
    def _candidate_for(cls, target: type["ClassMatcher"]) -> MatchCandidate:
        annotations = getattr(target, "__annotations__", {})
        schema = frozendict(annotations) if annotations else None
        return MatchCandidate(result_type=target, schema=schema)

    @classmethod
    def _collect_patterns(cls) -> dict[Expr, frozenset[MatchCandidate]]:
        patterns: dict[Expr, frozenset[MatchCandidate]] = {}

        def collect(target: type[ClassMatcher]):
            if hasattr(target, "match_patterns"):
                candidate = cls._candidate_for(target)
                for pattern in target.match_patterns:
                    patterns[pattern] = frozenset((candidate,))
            for subclass in target.__subclasses__():
                if is_abstract(subclass):
                    continue
                collect(subclass)

        collect(cls)
        return patterns

    @classmethod
    def _match_tree(cls) -> Expr:
        if cls.__match_tree__ is None:
            cls.__match_tree__ = merge(cls._collect_patterns())
        return cls.__match_tree__

    @classmethod
    def match(cls, _expr: Expr | str, *args, **kwargs) -> Self | None:
        if isinstance(_expr, str):
            _expr = Expr.from_str(_expr)
        matcher = Matcher()
        result = matcher.match(cls._match_tree(), _expr)
        if result is None or not result.candidates:
            return None
        viable = [
            candidate
            for candidate in result.candidates
            if result.values_for(candidate) is not None
        ]
        if not viable:
            return None
        if len(viable) != 1:
            raise ValueError("Ambiguous candidates in class matcher result")
        candidate = viable[0]
        values = result.values_for(candidate)
        if values is None:
            return None
        if candidate.result_type is None:
            return None
        for key in kwargs:
            if key in values:
                raise ValueError(f"Duplicate argument: {key}")
        instance = candidate.result_type(*args, **values, **kwargs)
        if not isinstance(instance, cls):
            raise ValueError("Resolved goal is not an instance of {cls.__name__}")
        return cast(Self, instance)


def _expected_candidates(expected: Any) -> tuple[Any, ...]:
    origin = get_origin(expected)
    if origin in (Union, UnionType):
        return get_args(expected)
    return (expected,)


def _is_expr_expected(expected: Any) -> bool:
    if isinstance(expected, type) and issubclass(expected, Expr):
        return True
    origin = get_origin(expected)
    if origin in (Union, UnionType):
        return any(_is_expr_expected(arg) for arg in get_args(expected))
    return False


def _projection_candidates(expected: Any) -> tuple[type, ...]:
    origin = get_origin(expected)
    if origin in (Union, UnionType):
        args = get_args(expected)
    else:
        args = (expected,)
    candidates = []
    for arg in args:
        if arg is type(None):
            continue
        if isinstance(arg, type) and not issubclass(arg, Expr):
            candidates.append(arg)
    return tuple(candidates)


def _project_value(value: Any, expected: Any) -> Any:
    candidates = _expected_candidates(expected)
    non_expr_candidates = [
        candidate
        for candidate in candidates
        if isinstance(candidate, type)
        and candidate is not type(None)
        and not issubclass(candidate, Expr)
    ]

    if isinstance(value, Node):
        for candidate in candidates:
            if candidate is type(None):
                continue
            if isinstance(candidate, type) and issubclass(candidate, Expr):
                if isinstance(value, candidate):
                    return value
        saw_projection = False
        for candidate in non_expr_candidates:
            projected = value.as_(candidate)
            if projected is NotImplemented:
                continue
            saw_projection = True
            if isinstance(projected, candidate):
                return projected
        if non_expr_candidates and not saw_projection:
            raise ValueError(
                f"No projection from {type(value).__name__} to {expected}"
            )
        return None

    for candidate in candidates:
        if candidate is type(None) and value is None:
            return None
        if isinstance(candidate, type) and isinstance(value, candidate):
            return value
    return None
