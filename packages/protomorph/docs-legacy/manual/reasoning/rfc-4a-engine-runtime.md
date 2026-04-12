# RFC 4A - Engine Runtime

Status: draft

This RFC will define the implementation-facing runtime semantics of the shared
logic engine.

It assumes RFC 1, RFC 2, RFC 3, and the outcomes of RFC 3.5.

The focus of RFC 4A is not public user API polish.
It is the internal runtime contract that allows:

- bottom-up closure on `Solver`
- top-down query evolution on `Session`
- one shared semantic engine in `engine.py`
- confined mutability during evaluation

## Purpose

RFC 4A exists to define the execution machinery that both solver-side and
session-side evaluation use.

In particular, it should answer:

- what mutable runtime state exists inside one engine run
- how that mutability is confined
- what task/action protocol the engine offers to premises and constraints
- how tables evolve, suspend, wake, and close
- how bottom-up and top-down differ only by driver strategy, not by semantics

## Working Assumptions

These assumptions may still be revised by RFC 3.5.

1. `engine.py` is the confined mutability cell of the solver runtime.
2. `Solver` and `Session` remain immutable semantic objects whose internal state is derived through engine runs.
3. Bottom-up and top-down must share one semantic runtime protocol.
4. Transient work queues are engine-private implementation details.
5. Top-down continuation is derived from persistent partial table state, not from exposing or persisting the raw work queue.

## Non-Goals

This RFC does not define:

- the final public shape of `Partial`
- the final `Row` structure
- detailed proof/evidence richness
- the detailed algebra of operators and constraints
- the full algebraic specification of `EqSet` beyond the monotone refinement
  contract fixed in RFC 3.5

Those belong in RFC 4B or later RFCs.

## Planned Sections

1. Scope and relationship to RFC 3.5
2. Engine as confined mutability cell
3. Persistent state vs transient run state
4. Table lifecycle and status model
5. Task/action protocol
6. Suspension and wakeup machinery
7. Bottom-up driver on `Solver`
8. Top-down driver on `Session`
9. Interaction with `join` and `rebase`
10. Public/internal API boundary

## Immediate Questions To Resolve

1. Which entities are persistent, and which are reconstructed per engine run?
2. What is the minimal task/action protocol that serves both bottom-up and top-down?
3. How are wake conditions represented and indexed?
4. How much unfinished state is persisted explicitly in `Session`, and how much is reconstructed from `Partial` tables?
5. What bottom-up table API should `Solver` expose directly?
6. Which exported child-partial facts are sound enough to drive `refine_from_partial` wakeups?
7. How are `TableRef(path, goal_shape)` targets stored and indexed across composed sessions?
