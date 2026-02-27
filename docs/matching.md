# Matching

This project uses a structural matcher to bind AST patterns to values.
Matching is functional: it produces a result object and never mutates state.

## Core concepts

- `MatchExpr`: AST nodes used only for matching.
- `MatchCapture`: wraps a subpattern and records a captured name.
- `MatchGoal`: marks the expected result type and schema.
- `MatchSwitch`: lookup node with priority order (literal -> any -> match_all).
- `MatchResult`: immutable bundle of goals and captures.

## Matcher contract

- `Matcher.match(pattern, value)` returns `MatchResult` or `None`.
- `MatchResult.unify(a, b)` merges goals and captures.
- `MatchGoal` is applied at the end to validate and build the output.

For ad-hoc matching, use `Matcher.from_str(...)` which returns a
`Matcher.Evaluator` configured with the given patterns.

## Captures

- Captures are only produced by `MatchCapture` nodes.
- Each capture records a name and the captured value.
- Variadic captures use `MatchCapture(variadic=True)`.

## Goals and schemas

- `MatchGoal` can be typed (`result_type`) or untyped (for the evaluator).
- If typed, the goal uses the class annotations as a schema.
- If untyped, the goal returns a `frozendict` of captures.

## Projections

- Projections are defined per AST node through `Node.as_(type)`.
- If a goal expects a non-Expr type, resolution calls `as_` on the captured node.
- Missing projections raise `ValueError`.
- If the goal expects an `Expr` subclass, the value must already be that type.

## Switch priority

`MatchSwitch` tries rules in order:

1) literal filters
2) filters with `Any`
3) `match_all`

Ambiguous filters at the same priority level raise `ValueError`.
