# PM / Axis Clean-Cut Roadmap

## Purpose

This document establishes the roadmap for the clean-cut migration from legacy
`protomorph` to `pm`, before the detailed semantic definitions are rewritten.

It is intentionally a planning document, not the final specification. Its role
is to freeze the direction of travel so that subsequent API and semantic work is
coherent.

## Scope

This roadmap covers the work needed before and during the replacement of
Axis-facing legacy Protomorph functionality:

- structural domain type semantics
- host and reasoning database responsibilities
- qualifier algebra and qualifier-specific behavior
- public matching and substitution APIs
- dispatch semantics for specialization, overloads, and switch-style matching
- convergent `Result[E] T` modeling
- Axis integration through `Realm` or its replacement

This roadmap does not define the final low-level API surface of each subsystem.

## Status

The current codebase contains a mix of:

- stable `pm` foundations worth preserving
- legacy `protomorph` semantics that will be deleted rather than ported
- documentation written against older DOM / bridge / introspector concepts
- temporary couplings to `NativeHost` inside `pm.reasoning`

The clean-cut plan assumes that compatibility with legacy `protomorph` is not a
goal.

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

### 2. `Host` and `Database` converge into `Realm`

The separate conceptual roles of `pm.Host` and `pm.reasoning.Database` are too
artificial for the future design. There must be a single semantic source of
truth.

The target abstraction is `pm.Realm`.

`Realm` will unify:

- nominal schema lookup
- hosted value traversal and reconstruction
- behaviour lookup and qualifier behaviour reduction
- rule and fact lookup for reasoning
- coinduction and logic operator evaluation

`Axis` will provide its own `Realm` implementation. `NativeRealm` remains a
useful built-in implementation, but it is not the source of truth for Axis
semantics.

`Engine` remains separate. It is an execution and caching layer over a `Realm`,
not part of the `Realm` contract itself.

### 3. `claim` is in scope for the rebuild

The replacement is not limited to defs and overloads. `claim` must be included,
which means `pm.reasoning` has to work correctly against non-native hosts.

### 4. The active semantic context is a single tracked `REALM`

There should not be distinct active `Host` and active `Database` context
variables. The semantic context is a single tracked `REALM` context variable.

The chain is:

- `flux.contextvar REALM`
- type and qualifier queries (`Type.behaviour`, `Spec.arity`, `Spec.item`, ...)
- `realm.reasoning`
- `pm.reasoning.Engine`

Changing the active `REALM` invalidates the relevant flux graph. This is an
acceptable and intended property for phase 0.

### 5. Anchors stay simple

`pm.Anchor` remains a simple identifier type (`NewType(str)`), with helper
functions rather than a return to the richer legacy object API.

### 6. Legacy compatibility is not a design constraint

The goal is not to recreate `MatchTree`, `SemanticBridgeBase`, `Err`, or the
older DOM bridge model inside `pm`.

## Workstream A - Qualifier Algebra And Behaviors

### Goal

Define a future-proof qualifier model for `pm` that can express transparent,
opaque, collection-like, effect-like, and composition-sensitive qualifiers.

### Direction

`pm.Qual` should remain the canonical normalized representation of a qualified
type:

- one underlying type
- an ordered qualifier chain
- flattening / normalization rules

Behavior must not be hardcoded into `Qual` itself.

### Planned abstraction

`pm` will gain a qualifier behavior layer, likely centered around a public
protocol or registry such as `QualifierBehavior`.

That layer must be able to answer questions such as:

- how a qualified value gets its carrier
- whether the qualifier is structurally transparent
- how projection works through the qualifier
- how lifting works through the qualifier
- how binary combination works, if at all
- whether multiple qualifiers interact in an order-sensitive way

### Behavior classes that must be supported

- transparent wrappers
- collection qualifiers such as `List`, `Set`, `Map[K]`
- opaque wrappers
- effect-like qualifiers
- result-like qualifiers
- qualifiers whose semantics depend on chain order

### Documentation consequence

The obsolete DOM-specific qualifier spec under `docs/dom_qualifiers.md` is no
longer authoritative. The authoritative qualifier design will live in the
Protomorph manual.

## Workstream B - `Result[E] T` And Convergent Error Modeling

### Goal

Replace legacy `pm.Err` with a qualifier-based result model that can support
both language-level semantics and gradual convergence of semantic failures into
the model.

### Direction

The target shape is:

- language type: `std.qualifiers.Result[E] T`
- `pm` support type: `pm.Qual.of(T, Spec.of("std.qualifiers.Result", E))`
- runtime support: a dedicated result carrier, likely `pm.ResultCarrier`

### Initial runtime behavior

The result carrier should support Rust-like operations:

- `is_ok`
- `is_err`
- `unwrap`
- `map`
- `map_err`
- `and_then`

### Convergence rule

We do not need to move every diagnostic and compiler failure into `Result`
immediately. But the model should be designed so that expected semantic failures
can eventually be represented inside the same algebraic framework.

Exceptions remain valid for implementation bugs and violated invariants.

### Naming cleanup

Before a public `pm.Result` value/type API is introduced, `pm.reasoning.Result`
should be renamed to something less ambiguous, such as `QueryResult`.

## Workstream C - Realm, Engine, And Context Lifecycles

### Goal

Make the roles of `pm.REALM`, `NativeRealm`, `pm.Realm`, and
`pm.reasoning.Engine` explicit and non-overlapping.

### Current issue

The current model is blurred:

- ordinary type operations rely on `pm.HOST`
- `NativeHost` is both default implementation and implicit global fallback
- `RuleSetDatabase` partly delegates semantic truth to a host
- `pm.reasoning` still forces `NATIVE_HOST` in some internal paths
- there is no single explicit semantic context object

### Target model

- `pm.REALM` scopes the active semantic context for type, qualifier, and
  reasoning operations
- `pm.Realm` is the canonical semantic interface
- `NativeRealm` is one concrete `Realm` implementation
- `pm.reasoning.Engine` is derived from a `Realm` and stays separate from it
- Axis will supply one object that implements `pm.Realm`
- test overlays live in the native/testing branch, not in the general `Realm`
  contract

### Exit criteria

- no reasoning path hardcodes `NATIVE_HOST`
- the active semantic context is always the active `REALM`
- `Engine` depends on `Realm`, not on a separate `Database`
- custom `Realm` implementations are first-class in docs and APIs

### Native testing overlays

Testing helpers such as `with_rules(...)`, `with_facts(...)`, and
`with_impls(...)` do not belong on the general `Realm` contract.

They belong on `NativeRealm`, or a native overlay type layered over it, so that
tests can reuse native semantics while injecting rules, facts, and impls.

Axis-specific realms are not expected to implement these helpers.

### Temporary aliases

During migration, the codebase may keep compatibility aliases such as:

- `Host -> Realm`
- `Database -> Realm`
- `NativeHost -> NativeRealm`
- `HOST -> REALM`
- `current_host() -> current_realm()`
- `RuleSetDatabase -> native overlay realm helper`

These aliases are transitional only and must be removed before the roadmap is
considered complete.

## Workstream D - Public Matching And Substitution API

### Goal

Standardize a generic public API for structural term matching and substitution.

### Required use cases

- specialization
- overload preparation and instantiation
- switch-style pattern matching
- claim lowering and reasoning support
- internal semantic rewrites over `Spec`, `Qual`, tuples, and placeholders

### Direction

`pm` should expose generic public operations instead of relying on scattered
ad-hoc helpers or `pm.reasoning.subst` internals.

The API should cover at least:

- structural substitution over terms and types
- placeholder enumeration / free placeholder discovery
- reification against an existing substitution environment
- structural matching over carriers or wrapped terms

This API belongs in `pm` even if specific callers live in Axis.

## Workstream E - Dispatching

### Goal

Provide a first-class dispatch system in `pm` for routing argument packs against
signature schemas.

### Required use cases

- definition specialization
- overload resolution candidate generation
- switch / match routing

### Direction

Dispatch should be a dedicated `pm` subsystem rather than a direct port of the
legacy match tree.

The system must formalize:

- positional arguments
- named arguments
- variadic positional capture
- defaults
- placeholder binding / substitution outputs

### Boundary

`pm.dispatch` should answer which candidates are admitted and how arguments bind
to slots. It should not decide Axis-specific overload preference policy.

### Deliverables

- argument pack representation
- signature representation
- routing algorithm
- public match / bind result structures
- clear laws for defaults and variadics

## Workstream F - Axis Integration

### Goal

Rebuild Axis semantics directly on `pm` primitives without carrying over the
legacy semantic shell.

### Direction

Axis should own:

- parsing and syntax trees
- scopes and namespace resolution
- lowering from Axis syntax into `pm` terms, rules, and signatures
- language diagnostics and policy decisions
- claim validation rules such as range restriction

`pm` should own:

- terms, carriers, and type algebra
- matching and substitution primitives
- dispatching
- qualifier behavior plumbing
- reasoning execution

### Target integration point

`Realm` becomes the semantic boundary object that exposes:

- host semantics for nominal schemas and hosted values
- reasoning database semantics for facts, rules, and logic operators

## Phase Plan

### Phase 0 - Roadmap And semantic freeze

- publish this roadmap
- mark obsolete docs as non-authoritative
- align obvious documentation drift such as tuple projection
- fix the semantic-context direction around `Realm`, `REALM`, and `Engine`

### Phase 1 - `pm` foundations for replacement

- introduce `pm.Realm`, `REALM`, and `current_realm()`
- introduce tracked flux contextvars for semantic context reads
- keep compatibility aliases temporarily while the migration is in progress
- remove host hardcoding from reasoning
- define qualifier behavior abstractions
- introduce public matching and substitution APIs
- define the dispatch model and implement the initial engine
- introduce `Result[E] T` and its carrier

### Phase 2 - Clean-cut Axis replacement

- remove Axis dependencies on legacy `protomorph`
- implement Axis realm semantics on top of `pm`
- rebuild defs, overloads, and `claim` on the new APIs

### Phase 2.5 - Alias removal

- remove transitional aliases such as `Host`, `Database`, `NativeHost`, and
  `RuleSetDatabase`
- remove transitional context names such as `HOST` / `current_host()`
- ensure docs and tests use `Realm` terminology consistently

### Phase 3 - Semantic convergence

- migrate more internal semantic failure paths toward result-modeling where it
  improves clarity
- deepen qualifier semantics and behavior composition
- refine Axis policy layers on top of stable `pm` primitives

## Non-Goals

This roadmap does not commit us to:

- preserving legacy `protomorph` API compatibility
- porting the old DOM bridge abstractions into `pm`
- freezing the exact final names of all future public APIs

## Immediate Documentation Tasks

The following docs must be realigned before detailed design work continues:

- `packages/protomorph/docs/manual/layer-3-domain-types.md`
- `packages/protomorph/docs/manual/layer-5-host-interface.md`
- `packages/protomorph/docs/manual/layer-6-native-host.md`
- `packages/protomorph/docs/manual/reasoning/database-rules.md`
- `docs/dom_qualifiers.md`

## Next Step

After this roadmap is published, the next documents to write should define:

1. qualifier algebra and `QualifierBehavior`
2. host / database lifecycle and context ownership
3. matching / substitution API
4. dispatch semantics
5. result carrier semantics
