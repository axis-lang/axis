# RFC 4B - Rows, Partials, And Query Observation

Status: draft

This RFC will define the observable informational model of query solving.

It assumes RFC 1, RFC 2, RFC 3, and the outcomes of RFC 3.5 and RFC 4A.

The central claim of this RFC is that `Row` and `Partial` are the two underlying
subjects of query observation:

- `Row` represents a solved contribution to a canonical table
- `Partial` represents an unfinished but informative state of inference

## Purpose

RFC 4B exists to clarify:

- what a `Row` really stores
- how a `Row` relates to `GoalShape` and `PredicateKey`
- how a query exposes partial information before it fully closes
- how proof artifacts such as evidence and judgments fit into that model

## Working Assumptions

1. `Row` and `Partial` are distinct concepts.
2. `Row.fact` is derived sugar, not primary storage.
3. `Partial` is the public unfinished-query model and the basis from which top-down continuation should be reconstructed.
4. `Evidence` and `Judgment` only remain first-class if they add real explanatory value beyond what `Row` and `Partial` already provide.
5. `Partial` exposes monotone established information plus unresolved `Need`s, not an arbitrary snapshot of transient engine queues.
6. `Partial` may refine while its table remains open, but at local fixpoint the remaining `Partial` values are themselves the stable unfinished snapshots for that session state.
7. Public observation is table-boundary oriented: child-private variables are not exposed as stable query-level identities.

## Non-Goals

This RFC does not define:

- low-level task scheduling
- wakeup indexing internals
- the final primitive-constraint context API

Those belong in RFC 4A or later RFCs.

## Planned Sections

1. Scope and relationship to RFC 3.5 and RFC 4A
2. Query observation model
3. `Row` as canonical table output
4. `Partial` as unfinished-query state
5. Filling canonical skeletons and slot-based substitution
6. `Row.fact` as derived projection
7. Query result views over rows and partials
8. Evidence and judgment, if retained
9. Public APIs for partial and solved observation
10. Deferred proof-model extensions

## Immediate Questions To Resolve

1. What is the minimal primary content of a `Row`?
2. Which parts of a `Partial` are directly observable, and which are rendered as derived user-facing views?
3. Which parts of a query's current inferred state are guaranteed observable?
4. Are `Evidence` and `Judgment` primitive fields or derived projections?
5. How should `Partial` explain unresolved subgoals and unmet needs?
6. How much of `EqSet` should be shown directly versus reified into slot/value views?
7. Should public partial observation expose `TableRef(path, goal_shape)` directly, or a more user-facing rendering of unresolved targets?
8. How should observation distinguish parent-visible variables from child-private frontier variables that were existentially forgotten during refinement?
