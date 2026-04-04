# PM / Axis Clean-Cut Roadmap

## Purpose

This document freezes the current direction of travel for the clean-cut migration
from legacy `protomorph` to `pm`.

It is a roadmap and design memo, not the final low-level specification. Its role
is to record the architectural decisions already made, the implementation state
already reached, and the next design fronts that must remain coherent with those
decisions.

## Scope

This roadmap covers the work needed before and during the replacement of
Axis-facing legacy Protomorph functionality:

- structural domain type semantics
- qualifier algebra and qualifier-specific behavior
- placeholder taxonomy and marker semantics
- structural matching and public pattern APIs
- matching / substitution / dispatch semantics
- `Result[E] T` / `Optional T` modeling
- reasoning execution on top of `Realm`
- Axis integration on top of `pm`

This roadmap does not define every final class or function name.

## Current Status

The codebase now contains a clear split between stable foundations and active
rebuild fronts.

### Foundations already in place

- `pm.Realm`, `REALM`, and `current_realm()` are the semantic context model.
- `pm.reasoning` now runs against `Realm` rather than a separate host/database
  split.
- structural domain types in `pm` are real and canonical:
  - `VaryingType`
  - `UniformType`
  - `IndexedType`
  - `Qual`
- `Result[E] T` is implemented as a special qualified type:
  - `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Result", E))`
- `Optional T` is implemented as a special qualified type:
  - `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Optional"))`
- `pm.Result` and `pm.Option` carriers already exist with Rust-like APIs.
- `Qual.last_qualifier` and `Qual.unwrap` already exist and are the right
  direction for qualifier-chain structural behavior.

### Axis migration state already reached

- Axis has cut the dependency on `pm.VarType`, `pm.ContextProto`, and `pm.var`.
- `Context.LogicVar`, `Entity.SpecVar`, and `Entity.ParamVar` now derive from
  `pm.SimpleVar`.
- Axis `Report` is now a `pm.Builtin`.
- Axis scope lookup now returns `pm.Result[log.Report, _]` rather than encoding
  failures as `pm.Err` values.
- the first slice of Axis expression lowering, constraints, and claim lowering
  already uses `pm.Result[log.Report, _]` as the result model.

### Main fronts still open

- placeholder taxonomy is not fully split yet (`Var`, `Op`, `Mark`)
- `pm.ANY` is not yet reintroduced on the new foundations
- structural matching has not yet been redefined in `pm`
- binding / variadic / open-tail lowering still depends on a missing structural
  pattern model
- dispatch for specialization / overload / switch-match has not yet been
  rebuilt on top of the new foundations

## Canonical Decisions Already Fixed

### 1. Structural domain types are canonical

The structural forms in `pm` are the source of truth for Python annotation
projection:

- `tuple[T1, T2, ...] -> VaryingType(T1, T2, ...)`
- `tuple[T, ...] -> UniformType(T)`
- named record-like shapes -> `IndexedType`
- `list`, `set`, `frozenset`, `dict` -> `Qual(...)`

Documentation that still describes `tuple[...]` as `Spec("std.types.Tuple", ...)`
is obsolete.

### 2. `Realm` is the single semantic boundary

The separate conceptual roles of host and reasoning database are gone. The
semantic source of truth is `pm.Realm`.

`Realm` unifies:

- nominal schema lookup
- hosted value traversal and reconstruction
- qualifier behavior reduction
- rule and fact lookup for reasoning
- logic operator evaluation

Axis supplies its own `Realm`. `NativeRealm` remains useful, but it is not the
source of truth for Axis semantics.

### 3. The active semantic context is a single tracked `REALM`

There is one tracked semantic context variable:

- `flux.contextvar REALM`

The chain is:

- `REALM`
- type / qualifier queries
- `realm.reasoning`
- `pm.reasoning.Engine`

Changing the active `REALM` invalidates the relevant flux graph. That is an
acceptable property.

### 4. Anchors stay simple, but they are no longer a `NewType(str)`

`pm.Anchor` remains conceptually simple, but it is now a real foundation type
with helper APIs such as parent/child navigation. We are not returning to the
legacy DOM bridge model.

### 5. Legacy compatibility is not a design constraint

The goal is not to recreate legacy abstractions inside `pm`.

We are deleting, not porting, concepts such as:

- `SemanticBridge`
- legacy `Err`
- legacy DOM bridge machinery
- the old `MatchTree` implementation shape as an API commitment

Semantics may be preserved where they are fundamental, but not through direct
compatibility shims.

### 6. `claim` is in scope for the rebuild

The replacement is not limited to defs and overloads. `claim` is part of the
target architecture, so `pm.reasoning` must work correctly against non-native
realms.

### 7. `pm.Val` is gone conceptually; the runtime value notion is `pm.Carrier`

In the new design, what legacy code used to call `pm.Val` should be understood
as `pm.Carrier` (or its subclasses). Axis should not reintroduce `pm.Val` as a
conceptual category.

### 8. `Result[E] T` and `Optional T` are qualifier-based and already implemented

The canonical shapes are:

- `Result[E] T` -> `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Result", E))`
- `Optional T` -> `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Optional"))`

The runtime support is:

- `pm.Result`
- `pm.Option`

Current agreed semantics:

- `Result.ok` structurally delegates through the inner `T`
- `Result.err` is a leaf
- `Option.some` structurally delegates through the inner `T`
- `Option.none` is a leaf
- `unwrap`, `map`, `map_err`, `and_then`, etc. live on the carriers

### 9. Axis result modeling converges on `pm.Result[log.Report, X]`

Within Axis, the canonical expected-failure model is:

- `pm.Result[axis.log.Report, X]`

This is already the active direction for:

- scope lookup
- expression lowering
- constraint lowering
- claim lowering

Unexpected bugs and broken invariants may still use exceptions.

### 10. Placeholder taxonomy splits into `Var`, `Op`, and `Mark`

`Placeholder` should branch into three semantic families:

- `Var` for logical / capturable placeholders
- `Op` for operator-like placeholders
- `Mark` for punctuation-like markers

This is consistent with the current reasoning engine, which already treats only
`Var` as a logical placeholder.

### 11. `Wildcard` and `Ellipsis` are `Mark`s

The current direction is:

- wildcard (`_`) -> `Mark`
- ellipsis (`...`) -> `Mark`

They are not logical variables and must not participate in reasoning as such.

### 12. `Spread` stays, for now, as structural splice payload

The existing `Spread` object in `pm` currently works as a structural payload for
flattening during tuple/type reconstruction.

That use is valid and stays in place for now.

The possible future semantics of variadic capture are a separate question and
must not be conflated with the current structural `Spread` payload.

### 13. Structural matching is foundational and must live in `pm`

Structural matching is not an Axis-private convenience layer.

It must be specified in `pm` and used consistently by:

- specialization
- overload preparation / routing
- switch-match branching
- claim-related structural lowering
- reasoning internals where structural pattern semantics are needed

`pm.reasoning` must ultimately work on top of that same structural-matching
design.

### 14. Axis `BindingStruct` is frontend normalization, not the final semantic model

`BindingStruct` in Axis is still useful, but only as syntax-to-IR normalization.

The actual structural pattern semantics must live in `pm`, not in Axis.

### 15. Structural matching in `pm` must be tuple-based, not legacy-struct-based

The new `pm` foundations speak in terms of:

- tuple-like types
- indexed tuple-like types
- carrier reconstruction

Therefore the structural-matching specification must be based on tuple/indexed
tuple semantics, not on direct resurrection of legacy `Struct` semantics.

## Workstream A - Qualifier Algebra And Behaviors

### Goal

Define a future-proof qualifier model for `pm` that can express transparent,
opaque, collection-like, effect-like, and composition-sensitive qualifiers.

### Direction

`pm.Qual` remains the canonical normalized representation of a qualified type:

- one underlying type
- an ordered qualifier chain
- flattening / normalization rules

Behavior must not be hardcoded into `Qual` itself.

### Current implementation facts

- `Qual.last_qualifier` and `Qual.unwrap` already exist
- `Result` and `Optional` already depend on qualifier-tail semantics
- qualifier-chain order is semantically meaningful and must remain so

### Planned abstraction

`pm` will gain a public qualifier behavior layer, likely centered around a
registry/protocol such as `QualifierBehavior`.

That layer must answer questions such as:

- how a qualified value gets its carrier
- whether the qualifier is structurally transparent
- how projection works through the qualifier
- how lifting works through the qualifier
- how binary combination works, if at all
- how qualifiers interact in ordered chains

## Workstream B - `Result[E] T`, `Optional T`, And Convergent Error Modeling

### Goal

Replace legacy `pm.Err` with qualifier-based algebraic carriers that can support
language semantics and gradual convergence of expected semantic failures.

### Direction

The canonical shapes are already fixed and implemented:

- `Result[E] T` -> `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Result", E))`
- `Optional T` -> `pm.Qual.of(T, pm.Spec.of("std.qualifiers.Optional"))`

### Current runtime surface

`pm.Result` supports Rust-like operations such as:

- `is_ok`
- `is_err`
- `unwrap`
- `unwrap_err`
- `expect`
- `expect_err`
- `unwrap_or`
- `unwrap_or_else`
- `map`
- `map_err`
- `and_then`

`pm.Option` supports the analogous shape-oriented subset plus:

- `is_some`
- `is_none`
- `ok_or`

### Convergence rule

Not every failure path must move into `Result` immediately, but expected
semantic failures should converge toward this algebra where it improves clarity.

## Workstream C - Realm, Engine, And Context Lifecycles

### Goal

Make the roles of `pm.REALM`, `NativeRealm`, `pm.Realm`, and
`pm.reasoning.Engine` explicit and non-overlapping.

### Target model

- `pm.REALM` scopes the active semantic context
- `pm.Realm` is the canonical semantic interface
- `NativeRealm` is one concrete implementation
- `pm.reasoning.Engine` derives from a `Realm` and stays separate from it
- Axis supplies one object that implements `pm.Realm`

### Exit criteria

- no reasoning path hardcodes `NATIVE_HOST`
- the active semantic context is always `REALM`
- `Engine` depends on `Realm`, not a separate database abstraction
- custom realms are first-class in docs and APIs

## Workstream D - Structural Matching And `pm.patterns`

### Goal

Define a `pm`-native structural-matching model that becomes the semantic basis
for specialization, overloads, switch-match, and any structural pattern work in
reasoning.

### Direction

This work should likely surface under a public namespace such as:

- `pm.patterns`

with a canonical pattern IR such as:

- `BindingPattern`

The exact names are not frozen yet, but the semantics are.

### Foundational semantics to preserve

From the old Axis / legacy Protomorph binding system, the following semantics
are fundamental and should be preserved even if the implementation is entirely
new:

- mixed positional and nominal field matching
- exact fixed-layout matching by default
- one contiguous variadic middle region at most
- explicit distinction between spread capture and open tail
- binders vs non-capturing placeholders
- per-field match constraints
- defaults meaning optional presence

### Defaults policy

Defaults should not be part of the core matcher semantics.

They should be elaborated into explicit variants before matching / dispatching,
as the legacy system effectively did.

### Variadic policy

Variadic behavior should be modeled as a middle segment between fixed prefix and
fixed suffix, not as an arbitrary number of independent spread captures.

### Placeholder interaction policy

- `Var` captures and participates in reasoning
- `Mark` does not capture
- `_` is a wildcard mark
- `...` is an ellipsis/open-tail mark

### Relationship with Axis `BindingStruct`

Axis `BindingStruct` remains useful as frontend normalization, but its output
should lower into `pm.patterns.BindingPattern` (or the final equivalent), not
into an Axis-private matching model.

## Workstream E - Matching, Substitution, And Dispatch

### Goal

Build public matching / substitution / dispatch APIs on top of the structural
pattern specification rather than as disconnected subsystems.

### Direction

`pm` should expose public operations for:

- structural substitution over terms and types
- placeholder / variable enumeration
- reification against substitution environments
- structural matching over carriers / wrapped terms
- routing argument packs against pattern/signature schemas

Dispatch is a consumer of the structural-matching model, not a separate source
of semantics.

### Required use cases

- definition specialization
- overload candidate admission
- switch / match routing
- claim lowering support
- reasoning-internal structural rewrites

## Workstream F - Placeholder Families And Operators

### Goal

Make placeholder categories explicit and stop overloading one placeholder class
for unrelated semantics.

### Direction

`Placeholder` should split into:

- `Var`
- `Op`
- `Mark`

Current implications:

- reasoning should continue treating `Var` as logical placeholders
- `SolverOperator` should eventually derive from `Op`, not from generic
  `Placeholder`
- `Wildcard` and `Ellipsis` should become `Mark`s

### Current non-decision intentionally preserved

The existing `Spread` payload used for tuple/type flattening remains in place for
now. Its future relationship, if any, to variadic capture is not yet fixed.

## Workstream G - Axis Integration

### Goal

Rebuild Axis semantics directly on `pm` primitives without carrying over the
legacy semantic shell.

### Direction

Axis should own:

- parsing and syntax trees
- scopes and namespace resolution
- syntax lowering into `pm` terms, rules, and patterns
- language diagnostics and policy decisions
- claim validation rules such as range restriction

`pm` should own:

- terms, carriers, and type algebra
- structural matching and substitution primitives
- dispatching
- qualifier behavior plumbing
- reasoning execution

### Current implementation direction

Axis is already converging on:

- `pm.Result[log.Report, X]` as its expected-failure model
- `pm.SimpleVar` for logic variables
- `pm` lowering for claims / constraints / scope lookups

The next major integration front is binding / structural matching.

## Phase Plan

### Phase 0 - Roadmap And Semantic Freeze

- publish and maintain this roadmap
- mark obsolete docs as non-authoritative
- align obvious documentation drift such as tuple projection and qualifier docs
- keep architectural decisions coherent while implementation proceeds

### Phase 1 - `pm` Foundations For Replacement

- stabilize `Realm`, `REALM`, and reasoning on top of `Realm`
- stabilize qualifier-tail semantics already used by `Result` / `Optional`
- introduce placeholder family split (`Var`, `Op`, `Mark`)
- reintroduce `pm.ANY` on the new foundations
- define `pm.patterns` / structural pattern semantics
- define public matching / substitution APIs on top of that

### Phase 2 - Structural Matching And Dispatch Rebuild

- implement the first structural pattern IR in `pm`
- make dispatch consume the structural-matching semantics
- cover specialization, overload routing, and switch-match with the new APIs

### Phase 3 - Clean-Cut Axis Replacement

- remove Axis dependencies on legacy `protomorph`
- lower Axis `BindingStruct` into `pm.patterns`
- rebuild claim / defs / overloads / matching on the new APIs

### Phase 4 - Alias Removal And Legacy Deletion

- remove transitional aliases and compatibility leftovers
- delete obsolete legacy `protomorph` code paths
- ensure docs and tests use the new terminology consistently

## Non-Goals

This roadmap does not commit us to:

- preserving legacy `protomorph` API compatibility
- porting the old DOM bridge abstractions into `pm`
- directly preserving the old `MatchTree` implementation shape
- deciding today the final public names of every future pattern / dispatch class

## Immediate Documentation Tasks

The following docs must be realigned before detailed design work continues:

- `packages/protomorph/docs/manual/layer-3-domain-types.md`
- `packages/protomorph/docs/manual/layer-5-host-interface.md`
- `packages/protomorph/docs/manual/layer-6-native-host.md`
- `packages/protomorph/docs/manual/reasoning/database-rules.md`
- any docs that still describe legacy `Err`, legacy `MatchTree`, or the old DOM
  bridge model as authoritative

## Next Step

After this roadmap update, the next design documents to write should define:

1. `pm.patterns` and structural-matching semantics
2. reasoning alignment on top of that pattern model
3. placeholder families (`Var`, `Op`, `Mark`)
4. dispatch semantics derived from the pattern model
5. qualifier behavior abstractions beyond the current hardcoded special cases
