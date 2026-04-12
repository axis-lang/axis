# RFC 3 - Solvers, Sessions, Queries, And Overlays

Status: draft

This RFC defines the runtime composition model for the redesigned `pm.logic`
solver.

It builds on RFC 1 and RFC 2.

## Scope

This RFC defines:

- solver composition as a DAG of logical universes
- flattened parent maps keyed by path
- bottom-up query/fixpoint access on `Solver`
- `Overlay` as the immutable session fact layer
- `Session` as a top-down snapshot over one solver and one overlay
- `Query` as a view over one query rooted in a session
- `join` and `rebase` semantics
- cache reuse boundaries for solver and session state
- one shared semantic engine for bottom-up and top-down execution

This RFC does not define:

- detailed primitive-constraint context APIs
- exact row or evidence classes
- helper-assertion deduplication across origins
- local logic programs or closure scopes
- exact internal task taxonomy

Those are deferred to later RFCs.

## Core Decisions

1. `Solver` and `Session` are different semantic layers.
2. `Solver` owns compiled program structure and bottom-up reusable caches.
3. `Session` owns top-down query evolution over one solver and one fact overlay.
4. Session facts are represented by `Overlay(fset[facts])`.
5. `Solver` and `Session` both use flattened parent maps keyed by `Path` as primary construction data.
6. The primary basis of a session is `SessionBasis(solver, parents, overlay)`.
7. `Session.join(...)` is only defined for sessions with the same basis.
8. If solver, parents, or overlay differ, sessions must be rebased before they can be joined.
9. `Solver.query(...)` is equivalent to `Solver.session().query(...)`.
10. Bottom-up and top-down execution share one semantic engine in `engine.py`.
11. Solvers and sessions resolve cross-universe access through flattened parent maps keyed by `Path`.
12. Top-down continuation is derived from persistent partial table state rather than persisted as raw frontier state.

## Universes And Solver Composition

type Path = tuple[Id, ...]


Each solver is a compiled logical universe.

A solver may depend on other solvers.

Parent visibility is flattened and keyed by path:

```python
Solver(parents: frozendict[Path, Solver], assertions: ...)
```

The parent mapping is primary construction data.

The current solver participates in dispatch implicitly at `path == ()`.

Derived flattened views over accessible parents are therefore part of the primary solver state, not merely a cache.

Examples:

- `x.pred(...)`
- `x.a.pred(...)`

The solver does not own a name for itself.
Path naming belongs to the calling context.

## DAG Composition

Solver composition is a DAG, not necessarily a tree.

Example diamond:

```text
A -> X
A -> Y
(X | Y) -> B
```

`B` may include `X` and `Y` in its flattened parent map.

`B` does not thereby collapse ownership with `A`.
It may refer to `A` through paths such as:

- `x.a`
- `y.a`

If `B` wants a direct `a`, it must include that path explicitly in its parent map.

## Path Resolution And Ownership

This RFC distinguishes two things:

- path-based lookup
- owner-based predicate identity

### Path-Based Lookup

Queries and premises may refer to predicates by qualified path.

Conceptually:

- path `()` refers to the current solver
- otherwise resolve by parent dispatch:

```python
if path == ():
    return self
return self.parents.get(path)
```

The flattened map therefore acts as a one-step dispatch table from visible path to owner solver.

### Owner-Based Identity

Ownership of a predicate is not determined by the caller path.

Once path resolution reaches the owning solver, the predicate is identified there by:

- owner solver context
- owner-local `PredicateKey`

This means the same solver may appear multiple times under different paths without duplicating predicate ownership.

## Solver API

The public immutable constructor surface is:

```python
solver.session(facts=()) -> Session
solver.query(goal) -> Query
solver.query(*goals) -> tuple[Query, ...]
```

Semantically:

```python
solver.query(goal)
```

is equivalent to:

```python
solver.session().query(goal)
```

and:

```python
solver.query(g1, g2)
```

is equivalent to:

```python
q1 = solver.session().query(g1)
q2 = q1.session.query(g2)
(q1, q2)
```

All returned `Query` values should therefore share one derived empty session.

## Solver Bottom-Up Semantics

`Solver` provides bottom-up evaluation under demand.

This is not a second solver.
It is the same semantic engine, driven bottom-up over compiled assertions and
primitive predicates that are solver-stable.

Bottom-up capabilities may include:

- table closure by `PredicateKey`
- table closure by component
- table closure by stratum
- direct bottom-up query access

These computations are:

- immutable relative to the solver
- reusable by descendant/composed solvers
- shareable across sessions over the same solver

Bottom-up evaluation is demand-driven, not eager by default.

## Solver-Stable vs Session-Sensitive Predicates

Primitive predicates may be classified as:

- `solver-stable`
- `session-sensitive`

### `solver-stable`

Depends only on:

- the compiled solver universe
- visible imported universes
- bottom-up reachable tables

These predicates are eligible for solver-side bottom-up caching.

### `session-sensitive`

Depends on:

- the session overlay
- session-local query evolution
- session-local assumptions or facts

These predicates are not fully representable in the solver cache alone and are
resolved through sessions.

## Overlay

Session facts are represented by:

```python
Overlay(fset[facts])
```

Overlay invariants:

- immutable
- extensional
- simple fact set only in RFC 3
- normalized independently of insertion order

Two overlays are equal if they expose the same normalized fact set.

## Session

`Session` is a top-down snapshot over one solver and one overlay.

Its primary construction data is:

```python
Session(solver, parents, overlay, fset[queries])
```

Conceptually, a session contains:

- one solver
- one flattened session parent map
- one immutable fact overlay
- one root query set
- one top-down local table cache
- one persistent partial table state

Top-down continuation is therefore derived from the session's partial table state.

## Session API

The public immutable API is:

```python
Session.query(goal) -> Query
Session.join(*sessions) -> Session
Session.rebase(...) -> Session
```

Sessions resolve path dispatch analogously to solvers:

```python
if path == ():
    return self
return self.parents.get(path)
```

The semantic model is centered on `(solver, parents, overlay, queries)`.

### `Session.query(goal)`

If the goal is already rooted in the session, return a `Query` over the same session.

If the goal is not yet rooted, return a `Query` over a derived session whose
root set includes that goal.

This preserves immutability while keeping the API compact.

### `Query.session`

Each `Query` exposes the session that owns that query root.

This is the session whose top-down cache and partial state are being observed.

## Query

`Query` is a view over one concrete goal rooted in a specific session.

It does not own a separate continuation object.
The query observes rows and partials rooted in the session.

`Query` should expose, at minimum:

- the root goal
- the owning session
- the current table view
- the current result view

## Session Join

`Session.join(...)` combines progress, not context.

It is only defined when all sessions share the same:

- `SolverCtx`
- parent map
- `Overlay`

This is a strict rule.

If solver, parents, or overlay differ, sessions are not directly joinable.
They must first be rebased.

### Why Join Is Strict

Negative answers and blocked states depend on the visible fact set.

Example:

- `Sx` proves `p` absent
- `Sy` adds a fact making `p` true

Reusing the negative result from `Sx` inside `Sy` would be unsound.

Therefore `join` is not a context merge.
It is only a merge of top-down progress inside the same context.

### Join Behavior

Given the same session basis, `join` may:

- union query roots
- reuse closed local tables
- reuse compatible open local tables conservatively
- union compatible persistent partial table state

The exact merge policy for unfinished table state is deferred, but the strict same-context rule is fixed.

## Session Rebase

`Session.rebase(...)` changes the base context of a session.

It may change:

- solver
- overlay
- or both

Rebase attempts to preserve:

- query roots
- reusable local cache entries
- compatible partial table state

but it does not guarantee exact preservation of all unfinished work.

In case of doubt, rebase preserves roots and closed tables first and replans open work.

## Overlay And Program Changes

Facts change the session overlay.
Assertions change the solver.

For that reason, adding assertions is not a primitive session mutation.

Convenience APIs such as:

```python
Session.overlay(assertions=...)
```

are understood as sugar for:

1. create a new solver overlay
2. rebase the session onto that solver

## Cache Layers

RFC 3 fixes two cache layers.

### Solver Cache

Owned by `Solver`.

Contains reusable bottom-up tables for solver-stable predicates.

These caches are:

- immutable relative to the solver
- shareable across sessions with that solver
- reusable in descendant/composed solvers when ownership and revision remain compatible

### Session Cache

Owned by `Session`.

Contains top-down local tables and persistent partial state tied to one overlay and one root set.

These caches are:

- reusable under strict same-session-basis joins
- partially reusable under rebase
- not globally shareable without compatibility checks

## Cache Reuse In DAGs

In a diamond composition:

```text
A -> X
A -> Y
(X | Y) -> B
```

cache reuse follows predicate ownership.

### Reusable directly in `B`

- bottom-up tables owned by `A`
- bottom-up tables owned by `X`
- bottom-up tables owned by `Y`

provided the referenced owner solver revision is the same.

### Not reusable as if identical

- caller-local path bindings such as `x.a` and `y.a` do not create distinct owners
- they are distinct path aliases to the same owner solver

### Session-local reuse

session-local top-down state can only be joined after rebasing to the same
`(solver, parents, overlay)` basis.

## Engine Unification

`engine.py` hosts the shared semantic kernel of the solver.

Bottom-up and top-down are not separate machines.
They are two coordinated drivers over the same semantic rules.

The shared engine semantics include:

- premise execution
- term-operator normalization
- primitive-constraint execution
- negative reasoning
- row production
- wakeup logic
- evidence propagation

The difference lies only in driving mode:

- `Solver` drives under-demand bottom-up closure
- `Session` drives top-down query evolution

## Suggested Responsibilities

### Solver

- compiled logical universe
- flattened visible parent map by path
- predicate ownership
- dependency graph, SCCs, strata
- reusable bottom-up fixpoint cache

### Session

- same solver-visible parent map semantics, but for session dispatch
- fact overlay
- root queries
- top-down local tables
- unfinished partial table state
- query-oriented views

### Query

- concrete root view inside one session
- access to table and result state

## Deferred To RFC 3.5 And RFC 4

- concurrent premise driving and convergence substrate
- exact bottom-up table API on `Solver`
- exact row/result/partial objects for solver and session queries
- exact frontier merge policy for `Session.join`
- task internal structures
- program-overlay joins across DAG branches
- advanced reuse of unfinished work across rebases
