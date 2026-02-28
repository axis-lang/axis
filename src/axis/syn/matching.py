"""
Matching

This module documents the matching contract used across the project.
Matching is functional: it produces a result object and never mutates state.

Core concepts
- MatchExpr: AST nodes used only for matching.
- MatchCapture: wraps a subpattern and records a captured name.
- MatchGoal: marks the expected result type and schema.
- MatchSwitch: lookup node with priority order (literal -> any -> match_all).
- MatchResult: immutable bundle of goals and captures.

Matcher contract
- Matcher.match(pattern, value) returns MatchResult or None.
- MatchResult.unify(a, b) merges goals and captures.
- MatchGoal is applied at the end to validate and build the output.

Captures
- Captures are only produced by MatchCapture nodes.
- Each capture records a name and the captured value.
- Variadic captures use MatchCapture(variadic=True).

Goals and schemas
- MatchGoal can be typed (result_type) or untyped (for the evaluator).
- If typed, the goal uses the class annotations as a schema.
- If untyped, the goal returns a frozendict of captures.

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


class MatchGoal(MatchExpr):
    subpattern: Expr | None = None
    result_type: type["ClassMatcher"] | None = None
    schema: frozendict[str, type] | None = None

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        assert isinstance(other, MatchGoal)
        return self.result_type == other.result_type and self.schema == other.schema

    def __hash__(self) -> int:
        return hash((self.result_type, self.schema))

    def apply(self, result: "MatchResult") -> object | None:
        values = result.values_for(self)
        if values is None:
            return None
        if self.result_type is None:
            return frozendict(values)
        return self.result_type(**values)


class MatchCapture(MatchExpr):
    name: str
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
    goals: frozenset[MatchGoal] = frozenset()
    captures: tuple[CaptureEvent, ...] = ()

    @classmethod
    def empty(cls) -> "MatchResult":
        return cls()

    @classmethod
    def from_goal(cls, goal: MatchGoal) -> "MatchResult":
        return cls(goals=frozenset((goal,)))

    @classmethod
    def from_capture(cls, capture: MatchCapture, value: Node | tuple[Node, ...]) -> "MatchResult":
        return cls(captures=(CaptureEvent(capture=capture, value=value),))

    @classmethod
    def unify(cls, left: "MatchResult", right: "MatchResult") -> "MatchResult":
        return cls(
            goals=left.goals | right.goals,
            captures=left.captures + right.captures,
        )

    def values_for(self, goal: MatchGoal) -> dict[str, Any] | None:
        values: dict[str, Any] = {}
        for event in self.captures:
            name = event.capture.name
            value = event.value
            if goal.schema is not None:
                if name not in goal.schema:
                    return None
                expected = goal.schema[name]
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


def _patterns_from_pairs(pairs: Iterable[tuple[Expr, MatchGoal]]):
    result: dict[Expr, MatchGoal] = {}
    for expr, goal in pairs:
        if expr in result and result[expr] != goal:
            raise ValueError(f"Ambiguous match: {expr} maps to multiple goals")
        result[expr] = goal
    return result


def merge(patterns: dict[Expr, MatchGoal]) -> Expr:
    if not patterns:
        raise ValueError("merge() requires at least one pattern")

    match_all_items = [
        (expr, goal)
        for expr, goal in patterns.items()
        if expr.match_spec.match_all
    ]
    if len(match_all_items) > 1:
        raise ValueError("Ambiguous match_all patterns in same switch")

    match_all_expr: Expr | None = None
    if match_all_items:
        match_all_expr = _reify_group(_patterns_from_pairs(match_all_items))
        if len(patterns) == 1:
            return match_all_expr
        patterns = {
            expr: goal
            for expr, goal in patterns.items()
            if expr is not match_all_items[0][0]
        }

    groups: dict[MatchFilter, dict[Expr, MatchGoal]] = {}
    for expr, goal in patterns.items():
        match_filter = _match_filter(expr)
        groups.setdefault(match_filter, {})[expr] = goal

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


def _reify_group(group: dict[Expr, MatchGoal]) -> Expr:
    patterns = list(group.keys())
    first = patterns[0]
    target_type = type(first)

    capture_names = {pattern.match_spec.capture_name for pattern in patterns}
    if len(capture_names) > 1:
        raise ValueError("Conflicting capture names in group")
    capture_name = capture_names.pop()

    attrs: dict[str, Any] = {}
    has_expr_attrs = False
    pairs = list(group.items())

    for attr, value in attrs_of(first).items():
        values = [getattr(pattern, attr) for pattern, _ in pairs]
        if _is_expr_value(value):
            has_expr_attrs = True
            sub_pairs = [(v, goal) for (pattern, goal), v in zip(pairs, values)]
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

        if not all(v == values[0] for v in values):
            raise ValueError(
                f"Ambiguous literal value for {target_type.__name__}.{attr}"
            )
        attrs[attr] = values[0]

    goals = set(group.values())
    if not has_expr_attrs:
        if len(goals) != 1:
            raise ValueError("Ambiguous goal types for leaf match")
        merged_expr: Expr = target_type(**attrs)
    else:
        merged_expr = target_type(**attrs)

    if capture_name is not None:
        for goal in group.values():
            if goal.schema is None:
                continue
            if capture_name not in goal.schema:
                raise ValueError(
                    f"Capture '{capture_name}' not found in goal schema"
                )
            expected = goal.schema[capture_name]
            if _is_expr_expected(expected):
                continue
            if not first.match_spec.match_all:
                candidates = _projection_candidates(expected)
                if candidates and not any(
                    type(first).can_project(candidate) for candidate in candidates
                ):
                    raise ValueError(
                        f"No projection from {type(first).__name__} to {expected}"
                    )
        merged_expr = MatchCapture(
            name=capture_name,
            subpattern=merged_expr,
        )

    if not has_expr_attrs:
        goal_template = next(iter(goals))
        merged_expr = MatchGoal(
            subpattern=merged_expr,
            result_type=goal_template.result_type,
            schema=goal_template.schema,
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
                goals = {
                    pattern: MatchGoal(subpattern=None, result_type=None, schema=None)
                    for pattern in self.patterns
                }
                self._match_tree = merge(goals)
            return self._match_tree

        def __call__(self, expr: Expr | str) -> frozendict[str, Any] | None:
            if isinstance(expr, str):
                expr = Expr.from_str(expr)
            matcher = Matcher()
            result = matcher.match(self._tree(), expr)
            if result is None or not result.goals:
                return None
            if len(result.goals) != 1:
                raise ValueError("Ambiguous goals in evaluator result")
            goal = next(iter(result.goals))
            resolved = goal.apply(result)
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
    def _goal_for(cls, target: type["ClassMatcher"]) -> MatchGoal:
        annotations = getattr(target, "__annotations__", {})
        schema = frozendict(annotations) if annotations else None
        return MatchGoal(subpattern=None, result_type=target, schema=schema)

    @classmethod
    def _collect_patterns(cls) -> dict[Expr, MatchGoal]:
        patterns: dict[Expr, MatchGoal] = {}

        def collect(target: type[ClassMatcher]):
            if hasattr(target, "match_patterns"):
                goal = cls._goal_for(target)
                for pattern in target.match_patterns:
                    patterns[pattern] = goal
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
        if result is None or not result.goals:
            return None
        if len(result.goals) != 1:
            raise ValueError("Ambiguous goals in class matcher result")
        goal = next(iter(result.goals))
        values = result.values_for(goal)
        if values is None:
            return None
        if goal.result_type is None:
            return None
        for key in kwargs:
            if key in values:
                raise ValueError(f"Duplicate argument: {key}")
        instance = goal.result_type(*args, **values, **kwargs)
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
