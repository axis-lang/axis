# RFC 2 - Assertions, Contexts, And Scheduling

Status: draft

This RFC defines the analysis and execution scaffolding for the redesigned
`pm.logic` solver.

It builds directly on RFC 1.

## Scope

This RFC defines:

- `Assertion` as an autonomous semantic object
- premise families and premise normalization
- assertion skeletonization
- derivation of `PredicateKey` and `GoalShape` from the same skeletonization method
- premise path dispatch as a separate concern from skeletonization
- variable families and context identity
- one runtime union-find per executing assertion frame
- one shared task model per active engine run
- premise-driven scheduling

This RFC does not define:

- the detailed algebra of type operators such as `KeyOf`, `Attr`, or `Spread`
- the exact primitive constraint catalog
- helper-assertion deduplication or sharing across origins
- bottom-up global closure strategy
- coinduction redesign

Those are deferred to later RFCs.

## Core Decisions

1. `Assertion` is a consed, autonomous semantic object.
2. There is no separate `CompiledAssertion` type in RFC 2.
3. Assertion analysis is expressed as derived properties on `Assertion`.
4. `PredicateKey` and `GoalShape` are distinct projections derived from the same skeletonization method.
5. Path dispatch is resolved outside owner-local skeletonization.
6. One shared task model drives solver execution per active engine run.
7. Premises control their own resolution logic through a common action protocol.
8. The engine orchestrates scheduling, tabling, wakeups, and fairness, but does not hardcode the detailed semantics of each premise family.
9. One runtime union-find is shared by the active branch of one assertion instance.
10. Primitive constraints do not own separate schedulers. Stateful constraints are resumed on the active run worklist.
11. All tables share one internal row model, regardless of whether they are populated by derived assertions or primitive constraints.

## Assertion As A Semantic Object

`Assertion` is not a passive record waiting to be compiled elsewhere.
It is the semantic unit that exposes its own analyzed structure.

Conceptually:

```python
class Assertion(Builtin):
    fact: Goal
    premises: tuple[Assertion.Premise, ...]

    @slot_cached_property
    def normalized_premises(self) -> tuple[Assertion.Premise, ...]: ...

    @slot_cached_property
    def synthesized_assertions(self) -> tuple[Assertion, ...]: ...

    @slot_cached_property
    def template_vars(self) -> tuple[Assertion.TemplateVar, ...]: ...

    @slot_cached_property
    def fact_skeleton(self) -> Goal: ...

    @slot_cached_property
    def predicate_key(self) -> PredicateKey: ...

    @slot_cached_property
    def goal_shape(self) -> GoalShape: ...
```

The exact API may grow, but the design rule is fixed:

- intra-assertion analysis belongs on `Assertion`
- inter-assertion analysis belongs on `Solver`

## Premise Families

RFC 2 keeps the flat premise model introduced in RFC 1.

```python
type Path = tuple[Id, ...]


class Assertion.Premise(Builtin, abstract=True):
    pass


class Assertion.PositivePremise(Assertion.Premise):
    path: Path = ()
    goal: Goal


class Assertion.NegativePremise(Assertion.Premise):
    path: Path = ()
    goal: Goal


class Assertion.Constraint(Assertion.Premise, abstract=True):
    path: Path = ()
    pass
```

All premise types live in the internal predicate universe of the solver.

- `PositivePremise` calls a solver predicate positively.
- `NegativePremise` negates a solver predicate.
- `Constraint` is a primitive first-level predicate.

`Assertion.fact` is always local to the owning solver of the assertion and does
not carry a path prefix.

## Path Dispatch

Premises may carry a `Path` prefix.

`Path` is a resolution prefix, not part of the owner-local logical shape.

Conceptually:

- `()` means the current solver/session
- any non-empty path is resolved through dispatch on the active solver/session

The path itself is not part of:

- `PredicateKey`
- `GoalShape`
- owner-local skeletonization

Instead, path dispatch selects the owner context first.
Only then are owner-local `PredicateKey` and `GoalShape` projected from the
premise goal.

## Premise Normalization

Assertion analysis normalizes its premises before global indexing.

This includes:

- canonicalizing deterministic term operators inside premise bodies
- deriving skeletons for premise goals
- recording visible variables and local variables per premise
- optionally synthesizing helper assertions when a negative premise should be lifted to a positive auxiliary predicate

### Optional Negative Rewriting

Because term operators are deterministic in RFC 1, a `NegativePremise` can remain
directly representable as a canonical goal.

RFC 2 also allows an optional normalization strategy:

- synthesize a positive helper assertion
- preserve the frozen operator structure in the helper head shape
- replace the original negative premise with a negation of that helper predicate

This is optional in RFC 2.
It is not required for correctness in version 1.

When used, the synthesized helper assertion is real, not virtual:

- it has a real `PredicateKey`
- it has a real `GoalShape`
- it owns a real `GoalTable`

Deduplicating helpers across different origins is explicitly out of scope for RFC 2.

## Skeletonization

Assertion analysis produces a skeletonized view of its fact and premises.

Skeletonization is the single method from which both `PredicateKey` and
`GoalShape` are projected.

The skeleton retains:

- structural constructors
- frozen operator syntax that remains after analysis
- repeated-variable equality information
- source-relative variable positions

The skeleton removes:

- user-facing variable names
- accidental identity of placeholder objects
- branch-local runtime bindings

### Shared Method, Distinct Projections

From the same skeletonization method, the solver derives two projections.

Both projections are owner-local.
They are computed after path dispatch has selected the owner solver for the premise.

#### `GoalShape`

`GoalShape` is the canonical tabling form of a call.

It preserves:

- full structural call shape
- slot identity and repeated-slot equality
- frozen operator structure that survives analysis

Conceptual example:

```text
Attr(X, KeyOf(T))
-> GoalShape = Attr($0, KeyOf($1))
```

```text
Eq(X, X)
-> GoalShape = Eq($0, $0)
```

```text
Eq(X, Y)
-> GoalShape = Eq($0, $1)
```

#### `PredicateKey`

`PredicateKey` is the coarser family identity used for:

- assertion indexing
- predicate ownership
- dependency graphs
- stratification

It preserves:

- the head predicate constructor
- frozen operator structure that changes the semantic family

It abstracts away:

- per-call slot identity
- repeated-slot equality details that only matter for tabling

Conceptual example:

```text
Attr(X, KeyOf(T))
-> PredicateKey = Attr(_, KeyOf(_))
```

```text
Eq(X, X)
-> PredicateKey = Eq(_, _)
```

```text
Eq(X, Y)
-> PredicateKey = Eq(_, _)
```

`PredicateKey` and `GoalShape` are therefore related but never identical by definition.

## Variable Families

RFC 2 fixes the semantic variable families used by solver analysis and runtime.

Conceptually:

```python
QueryVar(ctx=QueryCtx, slot=...)
Assertion.TemplateVar(ctx=Assertion.Ctx, slot=...)
Assertion.InstanceVar(ctx=Assertion.InstanceCtx, slot=...)
ConstraintLocalVar(ctx=ConstraintScopeCtx, slot=...)
GoalShapeVar(ctx=GoalShapeCtx, slot=...)
```

### Roles

- `QueryVar`: user-visible variables in a query
- `Assertion.TemplateVar`: variables in the analyzed assertion template
- `Assertion.InstanceVar`: runtime variables of one assertion instance
- `ConstraintLocalVar`: local variables introduced by one primitive constraint evaluation
- `GoalShapeVar`: slots used only to represent canonical tabled shapes

### Identity Rule

Variables are unique by structured context identity.

RFC 2 does not require a separate freshening pass.

Instead:

- instantiating an assertion creates `Assertion.InstanceVar`s with a unique `Assertion.InstanceCtx`
- creating local constraint variables creates `ConstraintLocalVar`s with a unique `ConstraintScopeCtx`
- canonicalizing a goal creates `GoalShapeVar`s with a unique `GoalShapeCtx`

## Union-Find Participation

There is one runtime union-find per active assertion branch.

The main runtime union-find includes:

- `QueryVar`
- `Assertion.InstanceVar`
- `ConstraintLocalVar`

The main runtime union-find does not include:

- `Assertion.TemplateVar`
- `GoalShapeVar`

`GoalShapeVar` belongs only to canonical tabling identity and never participates in
runtime branch unification.

Branching is handled through union-find snapshots and rollback.

## Assertion Frames

The unit of execution is an assertion frame, not a loose collection of unrelated premise tasks.

Conceptually:

```python
class AssertionFrame(Builtin):
    assertion: Assertion
    premise_index: int
    uf: UnionFind
    evidence: tuple[Judgment, ...] = ()
```

An assertion frame represents one active application of one assertion.

All premises in that frame share:

- the same runtime union-find
- the same branch-local bindings
- the same evidence chain

## Single Worklist Per Engine Run

RFC 2 defines exactly one worklist per active engine run.

There is no dedicated scheduler per primitive constraint.

Stateful constraints are resumed as ordinary tasks on that active run worklist.

Conceptually, the worklist may contain tasks such as:

- `RunPremise(frame)`
- `ResumeConstraint(frame, state)`
- `ResumeTable(frame, waiting_on=...)`

The exact task types are deferred, but the single-worklist-per-run rule is fixed.

## Premise-Driven Scheduling

Premises own the logic of how they advance.

The engine does not hardcode detailed semantic branches for positive, negative,
and primitive premises inline.

Instead, each premise family yields solver actions through a common protocol.

Conceptual actions:

- `NeedTable(goal)`
- `NeedClosed(goal)`
- `EmitRow(row)`
- `Advance(frame)`
- `Suspend(blocker)`
- `Fail(reason)`

The premise describes what should happen next.
The solver applies those actions and owns fairness, tabling, wakeups, and requeueing.

## Positive, Negative, And Constraint Execution

### Positive Premise

A positive premise:

1. dispatches its `path` to the active owner context
2. normalizes deterministic term operators inside its goal
3. computes the resulting owner-local goal
4. asks for the table of that goal
5. extends the current assertion frame once rows are available

### Negative Premise

A negative premise:

1. dispatches its `path` to the active owner context
2. normalizes deterministic term operators inside its goal, unless analysis already lifted them to a helper predicate
3. computes the resulting owner-local goal
4. asks for the table of that goal
5. succeeds only if that table is closed and empty
6. fails if that table has rows
7. suspends if closure or bindings are still insufficient

### Primitive Constraint

A primitive constraint:

1. dispatches its `path` to the active owner context
2. runs as a first-level premise
3. may normalize deterministic term operators inside its arguments
4. may consult positive solver tables
5. may introduce local variables in the shared branch union-find
6. may keep internal state across resumptions
7. emits rows to its own table through the common row model
8. may suspend or fail

Primitive constraints do not inject new outer premises into the global scheduler.

## One Internal Row Model

Derived assertions and primitive constraints must converge to the same internal row representation.

RFC 2 fixes that requirement even though the exact row type is deferred.

This means:

- constraints do not own a separate answer store
- derived and primitive predicates can share tabling machinery
- the scheduler does not branch on table kind when storing or replaying rows

Externally, primitive constraints may still report `Satisfy(...)` as their
control result, but the engine must normalize that to the shared internal row model.

## Solver Responsibilities

With RFC 2 in place, responsibilities are split as follows.

### Assertion

- intra-assertion analysis
- premise normalization
- skeletonization
- variable inventory
- projection helpers for `PredicateKey` and `GoalShape`

### Solver

- inter-assertion indexing
- ownership checks for `PredicateKey`
- dependency graphs and stratification
- engine-run orchestration
- table lifecycle and wakeups

### Primitive Constraints

- predicate-specific internal semantics
- positive subqueries
- local variable introduction
- row emission or suspension or failure

## Deferred To RFC 3.5 And RFC 4

- concurrent premise driving and convergence semantics
- exact task and action classes for the engine
- concrete row and partial models
- detailed primitive-constraint context API
- helper-assertion sharing and deduplication
- closure-like local scopes and local logic programs
- bottom-up closure over compiled assertions and primitive predicates
