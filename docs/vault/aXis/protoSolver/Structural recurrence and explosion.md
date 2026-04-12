# Structural recurrence and explosion

Related: [[protoSolver]]

## Context

This research line explores a Flix-like global-table solver adapted to `protomorph`, where everything is structured data (`pm.Val`) rather than a clean predicate/data split. Heads and premises are both structural patterns over nested trees.

The main concern is not only logical recursion, but structural explosion: rules can open search into increasingly complex patterns, and can also materialize increasingly complex results.

## Core premise

- In `protomorph`, a goal is a structured value, not just `Pred(arg1, arg2, ...)`.
- A rule head materializes facts/results.
- A premise opens search space.
- Structural growth may appear in both directions:
  - search direction: `head -> premise`
  - result direction: `premise -> head`

The solver therefore needs a structural analysis layer, not only logical dependency analysis.

## Skeleton and unnest

Two complementary transforms are emerging:

- `skeleton(goal)`
  - replaces leaves with wildcards
  - preserves coarse structure
  - useful for indexing, table identity, and shape comparison

- `unnest(goal)`
  - flattens a tree into a root plus structural variables / bindings for branches
  - turns nested structure into a graph-like representation
  - useful for compiled analysis and cheaper runtime propagation

Example intuition:

```text
A(B(C), X)

root = A(v0, v1)
v0 = B(v2)
v1 = X
v2 = C()
```

`unnest` is not the opposite of `skeleton`, but another projection of the same structural object:
- `skeleton` changes information level
- `unnest` changes representation

## Static structural graph

Compilation should analyze rules (ignoring ground facts for this phase) and match premises with compatible rule heads, producing a graph of structural possibilities.

This graph should be richer than the current dependency graph:

- not only `who can call whom`
- also `how structure moves and grows`
- how variables are projected
- where constructors are added
- where equalities collapse structure
- where recursive closure is possible

This analysis likely belongs at SCC granularity rather than per isolated rule.

## Explosion as a compile-time property

The current idea is:

1. Detect structural explosion statically.
2. Allow recurrent assertions / SCCs that capture that explosion.

Not every recursive SCC is the same. A useful classification may be:

- bounded exact
- regular recursive
- abstractly bounded by shape summaries
- unbounded

The interesting cases are the middle two.

## Occurs check as recurrence detection

The classical `occurs_check` rejects equations such as:

```text
X = f(X)
```

under finite-tree semantics.

The new intuition is to reinterpret such events as signals of structural recurrence rather than unconditional failure.

Example:

```text
T = A(B(T), M)
M = C(D(_), T)
```

This is not representable as a finite tree, but it is representable as a finite cyclic graph / regular recursive equation system.

So the goal is not to materialize infinite trees, but to capture their finite fractal description.

This suggests:

- do not think of `occurs_check` only as rejection
- think of it as a detector of self-contained structural equations
- allow these only when the surrounding rule/SCC admits a finite recurrent representation

## Exact recurrence vs abstract recurrence

There are at least three semantic levels:

1. finite exact terms
2. exact cyclic term graphs (regular infinite structure)
3. abstract shape summaries

The first new direction is level 2: exact finite graphs with cycles.

But some exploding SCCs may not collapse into one exact cyclic graph. Those may still need level 3: abstract shape summarization.

## Shape lattice

Structural keys/shapes may form a lattice of precision, e.g.:

```text
A(_, _) < A(B(_), _)
A(_, _) < A(_, C(_))
A(B(_), _) <> A(_, C(_))
```

This lattice could be used to:

- measure progress/refinement
- measure or detect structural explosion
- define widening/collapse policies
- compare competing summaries
- reason about dominance/subsumption

At least initially, this shape lattice should likely live in the payload/summary layer, not in the table key itself.

## Persistent state intuition

The persistent state should not be a live mutable `UF`, but a frozen structural graph, something like:

- public `Pattern.Slot`s
- internal binding variables
- exact structural nodes when possible
- summarized shape nodes when necessary

Conceptually this is closer to a frozen `UF` / term graph than to a reified tree snapshot.

## Working direction

The solver direction being explored is:

- global tables inspired by Flix
- compiled structural transitions using `unnest`
- static SCC analysis of structural growth
- recurrence detection via occurs-like self-containment
- exact cyclic graph capture when possible
- shape-lattice abstraction when exact capture is insufficient

This is still theory-stage. The next step is to formalize the static structural graph, the SCC classification, and the criteria under which a recurrent SCC is considered admissible.
