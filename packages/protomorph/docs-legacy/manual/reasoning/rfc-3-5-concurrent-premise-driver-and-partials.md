# RFC 3.5 - Concurrent Premise Driver And Partials

Status: draft

This RFC sits between RFC 3 and RFC 4.

Its purpose is to define the convergence model of the new solver before RFC 4A
and RFC 4B freeze runtime internals.

The core claim of this RFC is that, for the relational fragment of the solver,
the engine should converge tables of `Row` and `Partial` rather than step a
sequential backtracking proof procedure.

For this RFC, primitive constraints are deliberately left aside.
The focus is restricted to:

- positive premises
- negative premises
- assertion compilation
- local fixpoint over query tables

## Scope

This RFC defines:

- a concurrent reading of assertion premises
- `GoalTable` as the tabled unit of local convergence
- `EqSet` as the semantic substrate of equality/binding information
- `Need` as the semantic substrate of unresolved premise obligations
- `Row` and `Partial` as the two tabled result forms
- strong precompilation of assertions and premises on the solver side
- algebraic instantiation of subgoals from compiled premise structure

This RFC does not define:

- primitive constraints
- proof/evidence richness
- the final engine task/action protocol
- the exact storage strategy of `EqSet`

Those belong to RFC 4A and RFC 4B.

## Motivation

Sequential premise driving coupled to branch-local backtracking does not align
well with the desired model of the solver.

The desired solver should:

- extract as much information as possible from all premises of an assertion
- propagate information across premises before declaring a branch blocked
- expose useful partial query state publicly
- avoid making continuation depend on preserving an exact suspended worklist

This RFC therefore shifts the center of the design from procedural proof search
to local convergence over tabled partial states.

## Core Decisions

1. Premises are treated as semantically unordered for convergence purposes.
2. The solver converges tables of `Row` and `Partial`.
3. `Partial` is a first-class public concept.
4. Continuation should be reconstructable from persistent partial state rather than from raw worklist state.
5. `EqSet` is the semantic abstraction of equality/binding information.
6. `Need` is the semantic abstraction of unresolved premise obligations.
7. `Assertion` and `Premise` compile themselves as rich semantic objects.
8. Matching of an assertion head against a table goal is an engine/solver responsibility, not an `Assertion` responsibility.
9. Negative premises produce a different kind of need than positive premises.

## Runtime Entities

RFC 3.5 uses the following dynamic entities.

### `GoalTable`

A table keyed by one owner-local `GoalShape`.

Conceptually:

```python
class GoalTable(Builtin):
    goal_shape: GoalShape
    rows: frozenset[Row] = frozenset()
    partials: frozenset[Partial] = frozenset()
    closed: bool = False
```

`GoalTable` is the local convergence unit of the top-down solver.

### `Entry`

`Row` and `Partial` are two kinds of table entry.

Conceptually:

```python
class Entry(Builtin, abstract=True):
    eqs: EqSet


class Row(Entry):
    pass


class Partial(Entry):
    needs: frozenset[Need] = frozenset()
```

The intended reading is:

- `Row` = complete entry
- `Partial` = incomplete entry

`Partial` is not an arbitrary debugger snapshot of solver internals.
It is a semantic state of one unfinished contribution to the enclosing table.

While the table is still evolving, a `Partial` may itself be refined.
When the table reaches local fixpoint, any remaining `Partial` is a stable
snapshot of unfinished inference for that session state.

`Row` differs in that it may be materialized as soon as one contribution has no
remaining needs. It does not have to wait for table closure.

Its invariants are:

- `eqs` contains only monotone information already established for that
  contribution in the local slot space of the table/assertion interaction
- `needs` contains exactly the remaining obligations that still have to be
  discharged for that contribution to become a `Row`
- removing a need without adding new obligations is progress
- adding information to `eqs` is progress

`Row.fact` is not primary data. It is a derived projection from the table's
canonical skeleton together with the row's `EqSet`.

### Slot Spaces

Every `EqSet` lives in one explicit slot space.

For RFC 3.5, the relevant spaces are:

- the parent contribution space of one evolving assertion contribution
- the canonical child table space induced by one compiled premise

`Row.eqs` lives in the canonical slot space of its table.
`Partial.eqs` may live in a larger contribution-local space that still contains
private assertion slots not visible on the table boundary.

This distinction matters because a premise needs two different things:

- a public child table shape that can be indexed and shared
- a compiled bridge that moves information between parent and child spaces

### Variable Identity And Frontier Roles

All solver variables are `pm.Var` values.

Their semantic identity is structured.
At minimum, it comes from:

- variable family
- variable context
- local identifier within that context, typically an `id` or a `slot`

So two variables with the same printed name are still distinct if their contexts
or families differ.

RFC 3.5 cares about variable roles at one compiled premise frontier more than
about the final concrete subclass layout.

For one assertion contribution and one compiled premise, the relevant roles are:

- `HeadVar`: an assertion variable that appears in the assertion head
- `BodyVar`: an assertion variable that does not appear in the head, but must
  persist across premise interactions inside the same contribution
- `PrivateVar`: a variable whose meaning is local to one premise frontier only
- `SlotVar`: a canonical table-boundary variable in one `GoalTable`

Their intended semantics are:

- `HeadVar` lives in the parent contribution space and may survive to the parent
  row if solving completes
- `BodyVar` also lives in the parent contribution space, but is never exported
  directly as part of the parent row boundary
- `PrivateVar` does not require a parent-side runtime identity and never crosses
  back to the parent as a named variable
- `SlotVar` lives in a table slot space and is the key by which row and partial
  information is stored or exported at a table boundary

This gives the parent/child frontier its asymmetry:

- parent contribution space is keyed by `HeadVar` and `BodyVar`
- child table space is keyed by `SlotVar`
- `PrivateVar` may affect child solving, but it does not create a transport key
  on the parent side

So instantiation and refinement are not variable-sharing by identity across the
frontier.
They are transports between two different keyed spaces.

In RFC 2 terms:

- `HeadVar` and `BodyVar` are roles played by assertion-instance variables
- `SlotVar` is the role played by canonical goal-shape or table-slot variables
- `PrivateVar` is a semantic role, not necessarily a required concrete subclass

### `EqSet`

`EqSet` is the semantic representation of established equality/binding
information in one local slot space.

It is not defined as `UnionFind`.
An implementation may use union-find internally, but the RFC keeps `EqSet`
abstract.

The semantic reading of an `EqSet` is conjunctive:

- each equality it carries is known to hold
- adding equalities makes the state more informative
- inconsistency is represented as `conflict`, not as an `EqSet` value

An `EqSet` is therefore a partial-information object, not a full proof branch
dump.

Minimal conceptual form:

```python
EqSet = frozenset[Eq]
```

with:

```python
class Eq(Builtin):
    left: Term
    right: Term
```

Minimal semantic operations:

- `empty() -> EqSet`
- `merge(eqset1, eqset2) -> EqSet | conflict`
- `normalize(eqset) -> EqSet | conflict`
- `project(eqset, onto) -> EqSet`
- `reify(eqset, skeleton) -> Goal`

Minimal semantic laws:

1. `empty()` is the least informative consistent `EqSet`.
2. `merge` is commutative and associative up to normalization.
3. `merge` is monotone: it never removes established information.
4. `project` is forgetful and monotone: it may discard out-of-scope information,
   but it does not invent new equalities.
5. `reify` substitutes what is entailed by the `EqSet` into a skeleton and leaves
   unresolved slots symbolic.

This RFC uses the following order:

```text
eqs1 <= eqs2  iff  eqs2 entails every equality in eqs1
```

So larger `EqSet` values are more informative.

This is the only algebraic commitment RFC 3.5 needs:

- `EqSet` supports monotone refinement
- `EqSet` supports conflict detection
- `EqSet` supports projection between parent and child slot spaces

The exact runtime representation remains deferred.

### `TableRef`

In a composed solver/session graph, bare `GoalShape` is not enough to identify
the dynamic target of a need.

Conceptually:

```python
class TableRef(Builtin):
    path: Path
    goal_shape: GoalShape
```

`path` is dispatch context.
`goal_shape` is owner-local table identity once that path is resolved.

### `Need`

`Need` is the semantic representation of an unresolved premise obligation.

Conceptually:

```python
class Need(Builtin, abstract=True):
    premise: Assertion.Premise
    target: TableRef


class PositiveNeed(Need):
    pass


class NegativeNeed(Need):
    pass
```

For RFC 3.5, the two need kinds differ semantically:

- `PositiveNeed` waits for rows from another table
- `NegativeNeed` waits for closure information from another table or stratum

The key point is that a need is not keyed only by `GoalShape`.
It is keyed by a target table in the current solver/session topology.

## Compiled Assertion Surface

This RFC keeps compilation responsibilities local to the objects that can derive
their own structure.

### `Assertion`

`Assertion` remains a rich autonomous semantic object.

It may derive and cache properties such as:

- `fact_skeleton`
- `predicate_key`
- `goal_shape`
- `template_slots`
- normalized premises

But it does not own head matching against a query table.

Head matching is an engine/solver responsibility driven by:

- `dict[PredicateKey, fset[Assertion]]`
- owner-local `GoalShape`

### `Premise`

Each premise compiles itself and caches what it can derive from its own shape.

At minimum, a premise should be able to expose:

- `path`
- `polarity`
- `subgoal_skeleton`
- `child_table_space`
- `interface_eqs`

`child_table_space` is the canonical slot space of the child goal table induced
by this premise.

`subgoal_skeleton` is reified in that child table space.

`interface_eqs` is the precompiled relation between:

- the parent contribution space
- the child table space

`interface_eqs` is not itself the child table space.
It is the compiled bridge used in both directions:

- forward, to instantiate a child subgoal from parent information
- backward, to refine a parent from child rows or child partial exports

RFC 3.5 does not require a concrete representation for that bridge.
It may be modeled as an `EqSet`, a mapping, or another compiled object, as long
as it supports those two directional uses.

This is why `interface_eqs` is not the same thing as `child_table_space`.

`child_table_space` contains all child boundary slots.
`interface_eqs` only captures how some of those child boundary slots relate to
parent `HeadVar`s and `BodyVar`s.

Some child slots may therefore be frontier-private relative to the parent:

- they belong to `child_table_space`
- they participate in child rows and child partials
- but they have no named parent counterpart

This is the key to algebraic instantiation at runtime.

### Premise Interface Semantics

Semantically, a compiled premise induces a boundary between two spaces:

- the parent contribution space
- the canonical `child_table_space`

The compiled interface must support two derived transports:

```python
premise.forward_eqs(parent_eqs) -> EqSet[child_table_space] | conflict
premise.backward_eqs(child_eqs) -> EqSet[parent_space] | conflict
```

Their intended reading is:

- `forward_eqs` extracts the child table information implied by the current
  parent contribution state
- `backward_eqs` transports child table information back into the parent
  contribution space

RFC 3.5 does not require those operations to be primitive methods on the object.
It only requires that the compiled premise semantics behave as if those
operations existed.

One valid mental model is relational:

- the interface is represented on a joint parent-plus-child space
- forward transport means merge, normalize, then project onto
  `child_table_space`
- backward transport means merge, normalize, then project onto the parent space

The RFC cares about the induced transports, not about whether the bridge is
stored literally as equations, as a mapping, or as another compiled form.

The key transport rule is:

- parent refinement may only mention parent `HeadVar`s and `BodyVar`s
- child export is keyed only by child `SlotVar`s
- child frontier-private variables never cross the frontier as variables

So `forward_eqs` and `backward_eqs` do not identify parent and child variables
directly.
They derive target-space equalities from source-space equalities.

### Frontier Terminology

For one compiled premise, RFC 3.5 uses the following names:

- parent/child frontier: the boundary between parent contribution space and
  `child_table_space`
- instantiation: forward transport from parent contribution state to child table
  state
- total refinement: backward transport from a child `Row`
- partial refinement: backward transport from the exported boundary of a child
  `Partial`

The difference between total and partial refinement is semantic, not merely
procedural:

- total refinement discharges the corresponding positive need
- partial refinement keeps that positive need pending

## Head Matching

Given one `GoalTable(goal_shape)`, the engine selects candidate assertions by:

1. computing the owner-local `PredicateKey` of that table
2. looking up `dict[PredicateKey, fset[Assertion]]`
3. structurally matching each candidate assertion head against the table goal shape

If a head matches, the engine produces an initial `Partial` for that
assertion/table pair.

That initial `Partial` contains:

- an `EqSet` induced by head matching
- one `Need` per compiled premise of the assertion

This is an engine responsibility because matching depends on the queried table
shape and on the solver's assertion index.

## Instantiating Subgoals

This is the central operation of the runtime.

Each positive or negative premise supports a conceptual operation:

```python
premise.instantiate(eqs, dispatch) -> Need | conflict
```

where:

- `eqs` is the current equality/binding state of a parent `Partial`
- `dispatch` resolves the premise path to the owner solver/session context

Operationally, `instantiate(...)`:

1. resolves `path`
2. computes `child_eqs = premise.forward_eqs(parent.eqs)`
3. reifies the premise's `subgoal_skeleton` in the child table space using `child_eqs`
6. canonicalizes the result to an owner-local `GoalShape`
7. packages that with the resolved dispatch path as `TableRef(path, goal_shape)`
8. returns either:
   - `PositiveNeed(target=...)`
   - `NegativeNeed(target=...)`
   - or `conflict`

This makes subgoal instantiation algebraic rather than recursive-by-structure at runtime.

The intended variable behavior during instantiation is:

- parent `HeadVar`s and `BodyVar`s may constrain corresponding child `SlotVar`s
- child slots with no parent counterpart remain symbolic child-side slots
- no parent variable is copied into child space by identity
- the resulting child goal is keyed entirely by child `SlotVar`s and rigid terms

## Positive Premise Semantics

A positive premise induces a `PositiveNeed`.

That need targets another `GoalTable` through its `TableRef`.

The table may contribute two things back to the parent partial:

- `Row`
- `Partial`

### `consume_row` (Total Refinement)

Conceptually:

```python
premise.consume_row(parent: Partial, child: Row) -> Partial | Row | conflict
```

This operation:

1. computes `parent_delta = premise.backward_eqs(child.eqs)`
2. merges that with the parent `EqSet`
4. removes the satisfied `PositiveNeed`
5. returns a refined entry or a conflict

Its intended variable behavior is:

- child `SlotVar` information is translated back into consequences over parent
  `HeadVar`s and `BodyVar`s
- child frontier-private slots are forgotten unless they imply an equality over
  mapped parent variables
- the child `Row` is complete enough to discharge the need

### `refine_from_partial` (Partial Refinement)

This operation is deliberately narrower.

Semantically, a child `Partial` may refine a parent only through information
that survives projection to the child's canonical table boundary and remains
monotone under further refinement of that same child partial.

A child `Partial` may carry child-local slots that are meaningful for continued
solving inside the child table.
Those child-private slots are not exported back to the parent.

So the conceptual operation is:

```python
premise.refine_from_partial(parent: Partial, child: Partial) -> Partial | conflict
```

with the following rule:

- the engine may use only the child partial's exported table-space information,
  not its child-private internal state
- that exported information must already be safe to treat as established
  lower-bound knowledge
- the positive need remains pending until a `Row` arrives
- correctness must not rely on aggressive partial-to-partial propagation

Operationally, when such exported information is available, the operation:

1. computes `child_export = project(normalize(child.eqs), onto=child_table_space)`
2. computes `parent_delta = premise.backward_eqs(child_export)`
3. merges that with the parent `EqSet`
4. keeps the `PositiveNeed` pending
5. returns a refined partial or a conflict

This means:

- a positive need is satisfied only by `Row`
- `Partial` only refines the parent, it does not close the need
- engines may conservatively skip `refine_from_partial` and remain correct
- the refined parent entry remains conditional on the same unresolved child need
- if the child contribution later dies, the refined parent may die as well;
  soundness is preserved because no `Row` was emitted prematurely

Its intended variable behavior is:

- only the child boundary projection participates in transport
- parent refinement may mention only parent `HeadVar`s and `BodyVar`s
- child frontier-private variables are existentially forgotten
- no new parent variable identity is created by partial refinement

## Negative Premise Semantics

A negative premise induces a `NegativeNeed`.

Negative needs do not consume rows as positive support.
They depend on closure information.

For RFC 3.5, the rule is:

- if the target table is closed and empty, the need is satisfied
- if the target table has any row, the parent partial fails
- if the target table is not yet closed, the need remains pending

This means negative needs are closer to closure obligations than to positive row consumption.

Their exact interaction with strata and closure scheduling is deferred to RFC 4A.

## Local Fixpoint of a Table

Each `GoalTable` evolves by local fixpoint.

Conceptually:

1. create initial partials from matching assertions
2. instantiate needs for those partials
3. consume rows from dependent tables
4. refine from dependent partials when useful and sound
5. collapse partials with no remaining needs into rows
6. repeat until no new rows or refined partials appear

A table reaches local fixpoint when:

- no new `Row` appears
- no existing `Partial` is strictly refined

## Rows, Partials, and Continuation

RFC 3.5 does not treat continuation as preservation of the raw engine worklist.

Instead:

- `Partial` is the persistent semantic state of unfinished solving
- `Partial` may keep evolving while its table is open
- once no more refinement is possible, remaining partials are the stable
  unfinished snapshots of that session state
- continuation should be reconstructable from the graph of tables, rows, and partials

This is better aligned with the immutable session model than persisting exact
scheduler frontier state.

## Session Topology

The solver/session topology that matters dynamically is minimal:

- `GoalTable`
- `Row`
- `Partial`
- `Need`

The dynamic graph arises from:

```text
GoalTable -> Partial -> Need -> GoalTable
```

Rows terminate branches of that graph.

The solver governs the static topology:

- assertions
- premise structure
- dependency graph
- skeletons
- owner-local predicate families

The session governs the dynamic topology:

- which tables are open
- which rows exist
- which partials remain unresolved
- which needs connect one table to another

## Payload Note

RFC 3.5 does not include payloads in the semantic identity of rows or partials.

However, this RFC leaves room for a future extension in which a table may carry
auxiliary payloads per entry, for example:

- implementation witnesses
- evaluator handles
- cached auxiliary runtime data

Such payloads are not part of convergence identity in RFC 3.5.

## Deferred To RFC 4A And RFC 4B

- exact storage strategy for `EqSet`
- exact engine task/action protocol
- exact closure/wakeup protocol for negative needs
- final `Row` content and projection model
- final `Partial` public observation model
- evidence and judgment, if retained
