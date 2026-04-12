# RFC 1 - Operators And Constraints

Status: draft

This RFC defines the first semantic base for the redesigned `pm.logic` solver.
It intentionally keeps the model flat and restrictive.

## Scope

This RFC defines:

- naming for table identity concepts
- term operators inside assertion bodies
- primitive constraints as first-level premises
- the control results of operator and constraint evaluation
- how primitive constraints consume and produce tabling state

This RFC does not define:

- assertion skeletonization and compilation internals
- cross-solver path dispatch
- variable families and contexts in detail
- union-find participation rules
- local subprograms or temporary assertions
- negative primitive constraints

Those are deferred to RFC 2 and later RFCs.

## Terminology

- `PredicateKey`: stable family identifier for a logical predicate
- `GoalShape`: canonical tabling shape for one demand
- `GoalTable`: memo table attached to one `GoalShape`

`PredicateKey` and `GoalShape` are owner-local projections.

Cross-solver path dispatch is defined in later RFCs and does not participate in
these projections.

## Core Decisions

1. Operators and primitive constraints are internal to `pm.logic`.
2. `Realm` does not evaluate logic operators or constraints.
3. Runtime operators are not allowed inside `Assertion.fact`.
4. Term operators only appear inside assertion body premises, including inside constraint arguments.
5. Primitive constraints are first-level premises.
6. Primitive constraints participate in tabling.
7. `Expand` is not part of RFC 1.
8. A primitive constraint may query the solver internally, but it does not return subpremises to the outer scheduler.
9. A `PredicateKey` is owned either by compiled assertions or by one primitive predicate family, but not both.
10. Primitive constraints may query only positive subgoals in RFC 1.
11. All blocked results must carry explicit wake conditions.
12. Term operators return a single deterministic rewrite in RFC 1.

## Model

```python
class Assertion(Builtin):
    fact: Goal
    premises: tuple[Assertion.Premise, ...]


class Assertion.Premise(Builtin, abstract=True):
    pass


class Assertion.PositivePremise(Assertion.Premise):
    goal: Goal


class Assertion.NegativePremise(Assertion.Premise):
    goal: Goal


class Assertion.Constraint(Assertion.Premise, abstract=True):
    pass
```

Primitive constraints are subclasses of `Assertion.Constraint`.

Examples:

- `KeyOfPremise(T, K)`
- `Subtype(A, B)`
- `ImplSelect(Trait, Self, Impl)`
- `InferShape(spec, inputs, output)`

Term operators remain separate from premises:

```python
class Op(Placeholder, abstract=True):
    pass


class TermOp(Op, abstract=True):
    pass
```

Examples:

- `AttrOp(X, name: Id)`
- `KeyOfOp(X)`
- `EvalOp(X, To)`

## Result Types

Term operators and primitive constraints do not share the same control algebra.

### Term Operators

```python
class Rewrite(Builtin):
    value: Goal


class Blocked(Builtin):
    blocker: Blocker
    wake_on: tuple[WakeCondition, ...] = ()


class Failed(Builtin):
    reason: str
    detail: Goal | None = None
```

`Rewrite(value=x)` is the only rewrite form in RFC 1.

### Primitive Constraints

```python
class Satisfy(Builtin):
    solutions: tuple[ConstraintSolution, ...] = ()


class ConstraintSolution(Builtin):
    export: frozendict[Var, Goal] = frozendict()
    evidence: Goal | None = None
```

Primitive constraints return exactly one of:

- `Satisfy`
- `Blocked`
- `Failed`

They do not return `Rewrite`.
They do not return `Expand`.

## Invariants

### Assertion Fact

`Assertion.fact` must have stable `PredicateKey` and `GoalShape` during assertion analysis.

RFC 1 therefore forbids runtime term operators inside `Assertion.fact`.

### Premise Classes

- All premise types live in the internal predicate universe of the solver.
- `PositivePremise` and `NegativePremise` are relational premises.
- `Constraint` is a primitive first-level premise.
- `Constraint` is not encoded as a goal inside `PositivePremise`.

### Primitive Predicate Ownership

If a primitive constraint family owns a `PredicateKey`, compiled assertions do not also own that same `PredicateKey` in RFC 1.

### Negative Constraints

RFC 1 does not support negating primitive constraints directly.
Negation applies only to relational goals through `NegativePremise`.

### Negative Premises With Term Operators

Because term operators rewrite deterministically in RFC 1, they may appear inside
`NegativePremise.goal` and still normalize to a canonical negated goal.

Analysis may also optionally synthesize an auxiliary positive assertion and then
negate that helper predicate instead. That normalization strategy is not required
for RFC 1, but it is allowed and is specified further in RFC 2.

## Term Operator Semantics

Term operators operate only inside assertion bodies.

They may appear inside:

- `PositivePremise.goal`
- `NegativePremise.goal`
- any argument of a primitive constraint

They are evaluated locally and structurally.

They may:

- rewrite one subterm to one replacement term
- block waiting for more information
- fail definitively

They may not:

- open their own `GoalTable`
- emit rows directly into a table
- expand into new premises

In practice, a term operator is a local normalizer or projector, not a first-level solver predicate.

## Primitive Constraint Semantics

A primitive constraint is a first-level premise and therefore a first-level predicate of the solver.

It has:

- a `PredicateKey`
- a `GoalShape`
- a `GoalTable`

The engine evaluates a primitive constraint against the current proof state.

That evaluation may:

- inspect already-bound visible variables
- introduce local variables for internal search
- query positive subgoals through the solver
- emit zero or more `ConstraintSolution` rows to its own table
- block with explicit wake conditions
- fail definitively

It may not:

- return subpremises to the outer scheduler
- mutate foreign tables directly
- introduce temporary assertions in RFC 1

## Constraint Interaction With Tabling

This is the core rule.

A primitive constraint does not return an opaque host value. It contributes answers to its own `GoalTable`.

Conceptually:

1. The solver creates or reuses the `GoalTable` for the current constraint call.
2. The primitive evaluator receives the current call plus a solver-facing query context.
3. The evaluator may query positive subgoals.
4. The evaluator combines those results with its own local logic.
5. The evaluator emits `ConstraintSolution` rows for the current table, or returns `Blocked`, or returns `Failed`.

The primitive evaluator therefore consumes tabling and produces tabling, but does not expose a second external scheduling language.

## Examples

### A. `KeyOfPremise(T, K)`

```python
Assertion(
    fact=FieldName(T, K),
    premises=(
        KeyOfPremise(T, K),
    ),
)
```

If `T` is a record-like type with keys `a` and `b`, then:

```python
Satisfy((
    ConstraintSolution(export={K: pm.val("a")}),
    ConstraintSolution(export={K: pm.val("b")}),
))
```

This is a tabled primitive predicate that enumerates solutions for `K`.

### B. `Subtype(A, B)`

```python
Assertion(
    fact=Compatible(A, B),
    premises=(
        Subtype(A, B),
    ),
)
```

For structural tuples, the primitive evaluator may internally query:

- `Subtype(A1, B1)`
- `Subtype(A2, B2)`

If both dependent tables support success, the current table receives one empty solution:

```python
Satisfy((ConstraintSolution(),))
```

If one dependent table is blocked, the current call returns `Blocked` with wake conditions referencing those dependencies.

If one dependent table fails, the current call emits no solution.

No `Expand` is returned to the outer scheduler.

### C. `AttrOp(T, Id("x"))`

```python
Assertion.PositivePremise(
    goal=Assignable(AttrOp(T, pm.Id("x")), U),
)
```

If attribute lookup succeeds with `Int`, the operator returns:

```python
Rewrite(value=pm.val(Int))
```

The enclosing premise then continues as:

```python
Assignable(Int, U)
```

### D. `InferShape(spec, inputs, output)`

```python
Assertion(
    fact=HasOutputShape(spec, inputs, output),
    premises=(
        InferShape(spec, inputs, output),
    ),
)
```

`InferShape` may introduce local variables, query positive subgoals, and export only externally visible bindings.

Example result:

```python
Satisfy((
    ConstraintSolution(export={output: inferred_shape}),
))
```

## Why `Expand` Is Excluded

`Expand` would create a second external proof language on top of ordinary premises.

RFC 1 rejects that direction.

If a primitive constraint needs decomposition, it must perform that decomposition internally by querying the solver and then emitting rows, blocking, or failing.

This keeps the outer planner flat:

- relational premises
- negative premises
- primitive constraints

and nothing else.

## Deferred To RFC 2

- `Assertion` as an autonomous consed object with rich derived API
- `PredicateKey`, `GoalShape`, and `GoalTable` data model details
- variable families and context identity
- which variable families participate in the main union-find
- traceability of equivalence classes and variable origins
- local variable export rules for primitive constraints
- local closures and local logic scopes
