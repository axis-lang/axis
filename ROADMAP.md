# Semantic Layer Roadmap

## Goal

Make `axis.sem` capable of deciding whether a declaration, specialization, and
call are semantically valid against declared bounds, using `protomorph` as the
semantic backend.

## Current Baseline

- The repository already has the core scaffolding: `Realm`, `Context`,
  `Entity`, lexical `Scope`, semantic bindings in `axis.sem`, and bound/default
  lowering through `syn.Expr.to_bound(...)` and `sem.build_bound(...)`.
- Inline and block binding forms now converge on one semantic binding model, and
  `QualDef` already emits semantic contributions.
- `std-core` now follows the canonical module layout:
  - `std.core.*`
  - `std.types.*`
  - `std.qualifiers.*`
- Axis tests now have dedicated semantic helper infrastructure under
  `tests/helpers/`, including `TestPackage`, `SemanticTestCase`,
  `StdPackageTestCase`, and `InlinePackageTestCase`.
- Axis tests are now organized by theme under `tests/bounds/`, `tests/defs/`,
  `tests/helpers_tests/`, `tests/sem/`, and `tests/syn/`.
- `packages/protomorph` has evolved significantly and now exposes a matching-
  and schema-centric semantic backend centered on:
  - `Layout`
  - `AtomicLayout`
  - `StructLayout`
  - `type.construct(...)`
  - `type.decode(...)`
  - `type.serialize(...)`
  - `value.encode()`
  - **NEW**: `Val.subst(env)` for symbolic term substitution
  - **NEW**: `Val.as_type()` for type-like interpretation
  - **NEW**: `Fact = Spec` alias for logical term model
- `packages/protomorph` now also exposes a compiled matching model centered on:
  - `StructSchema`
  - `MatchTree`
  - `compile(...)`
  - structural result traces and ambiguity buckets
- `axis.sem` now aligns with the new Protomorph matching model:
  - semantic bindings lower to `StructSchema`
  - `SpecIndex` is now a thin semantic facade over `pm.compile(...)`
  - `OverloadIndex` exists as the next matching facade to complete
  - Bound expressions use `bound.subst(env).as_type()` pattern
- Declaration lowering has also progressed:
  - qualifier declarations expose `underlying_bound_expr` / `underlying_bound`
  - function implementations expose `result_bound_expr` / `result_bound`
  - inline and block `returns` forms are merged before semantic contribution creation
- Semantic bindings now have a stronger split between declarative and lowered forms:
  - `BindingStruct.Field`
  - `LoweredBindingStruct.Field`
  - `lower_binding_struct(...)`
  - `binding_schema(...)`
- What is still missing is decision-making semantics in `axis.sem`: there is no
  reusable semantic relation like `satisfies(actual, bound)`, no specialization
  resolver, and no call resolver.
- Declaration support is still incomplete even after the binding and bridge work:
  - contribution `check()` methods mostly force lowering instead of performing
    declaration validation
  - `Type` is not yet established as an explicitly usable semantic type-value in
    the relevant scopes
  - there is still no reusable declaration-validation layer for duplicate names,
    invalid defaults, unresolved symbols, and malformed bounds
- `just test` remains the package-level gate and `just test-all` is the
  repository-level integration gate; both must be green before moving to the
  next stage.

## Parallel Track - Editor Tooling

- The repository now also has an editor-only VS Code extension scaffold under
  `ide/vscode/`.
- This track is intentionally separate from the semantic roadmap. It currently
  includes:
  - `*.ax` file association
  - syntax highlighting
  - snippets
  - comments, brackets, and indentation rules
  - Markdown-style doc block highlighting for `---`
- This editor track does not yet include semantic IDE features such as
  diagnostics, hover, go-to-definition, or language-server integration.
- `axis-lsp` remains a later milestone, after the editor baseline is stable.

## Design Rules

- `axis.expr.ir` remains a lowering layer. It builds semantic values from AST,
  but it does not decide validity.
- `axis.sem` owns validation, candidate selection, ambiguity handling, and
  diagnostics.
- `axis.sem` should talk to `protomorph` through `StructSchema`, `compile(...)`,
  and related matching/runtime hooks, not through older Axis-local routing logic.
- Bound construction and bound satisfaction are separate concerns.
- The first iteration uses strict compatibility, not subtyping.
- `Realm` and `SemanticBridgeBase` should only grow when the semantic layer
  truly needs host-specific type relations.

## First-Pass Matching Semantics

- Argument shape must match after applying defaults.
- `None` bound means unconstrained.
- `pm.Err` fails the candidate and emits a diagnostic.
- `pm.Anchor` and `pm.Spec` match by exact nominal identity.
- Type-like bounds compare on `pm.Type` values, not on surface syntax.
- No implicit coercions, variance, operator laws, or qualifier-specific lifting
  rules are part of the first pass.

## Milestone 0 - Baseline Hygiene

Target files: `justfile`, `tests/test_defs.py`, and the implementation files
needed to restore the intended behavior.

- Restore a green `just test` baseline.
- Align `just test` with the intended full-suite workflow.
- Resolve the current mismatch around `build_binding_struct(...)` and
  `tests/test_defs.py` so the test suite reflects the current semantic intent.

Exit criteria:

- `just test` passes locally.
- The test suite reflects the intended declaration semantics, not stale
  behavior.

Status:

- Completed.
- The repository baseline is green and declaration tests already reflect the
  current binding intent.

## Milestone 1 - Declaration Integrity

Target files: `src/axis/items/defs/base.py`, `src/axis/items/defs/qual.py`,
`src/axis/items/defs/fn.py`, `src/axis/sem/entity.py`,
`src/axis/expr/ir/bound.py`, and related tests.

- Preserve inline spec and param bindings instead of dropping them when no
  block form exists.
- Wire `QualDef` into semantic contributions so declarations like `Optional`,
  `Array`, `Struct`, and `Struct.Index` exist as semantic entities.
- Make `Type` available as a usable type-value in the relevant scopes.
- Lower return declarations into semantic data instead of leaving them as raw
  `syn.Expr`.
- Turn declaration `check()` methods into real validation for duplicate names,
  invalid defaults, unresolved symbols, and malformed bounds.

Exit criteria:

- `std-core` qualifier-like definitions appear in `entities_by_anchor`.
- Inline and block binding forms produce the same semantic binding model.
- Contributions expose bounds, defaults, and returns as semantic values with
  meaningful diagnostics.

Status:

- Partially completed.
- Done:
  - inline/block bindings converge on one semantic binding model
  - `QualDef` emits semantic contributions
  - qualifier-like definitions from `std-core` appear in the semantic graph
  - qualifier declarations now lower `underlying_bound_expr` into semantic values
  - function implementations now carry merged `result_bound_expr` / `result_bound`
- Still open:
  - `Type` as an explicitly usable semantic type-value in scopes
  - turning contribution `check()` into real declaration validation
  - deciding whether any remaining declaration syntax still needs semantic lowering
    before the constraint kernel lands

## Milestone 1.5 - Semantic Bridge Alignment

Target files: `packages/protomorph/src/protomorph/`, `src/axis/sem/realm.py`,
`src/axis/sem/entity.py`, `src/axis/items/defs/fn.py`,
`src/axis/items/defs/qual.py`, and focused tests.

- Align `axis.sem` with the new Protomorph runtime model:
  - `Layout`
  - `AtomicLayout`
  - `StructLayout`
  - `type.construct(...)`
  - `type.decode(...)`
  - `type.serialize(...)`
  - `value.encode()`
- Replace remaining older structural assumptions in `axis.sem` with
  `layout(...)`-based reasoning.
- Decide what semantic entities in Axis should expose structural or atomic
  layouts through `Realm`.
- Lower declaration-level `returns` and qualifier `underlying_expr` into
  semantic values that are meaningful to the Protomorph backend.
- Re-evaluate whether Axis-specific contribution logic still belongs inside
  `sem.Entity` or should move into `items`-owned contribution types.

Exit criteria:

- `Realm` participates coherently in the layout-based Protomorph model.
- `NominalType` / `NominalQualifier` semantics used by Axis no longer rely on
  stale bridge assumptions.
- Return and underlying declarations are represented as semantic values instead
  of raw syntax where needed by later validation.

Status:

- Completed.
- Done:
  - Added logical term model to Protomorph: `Val.subst(env)`, `Val.as_type()`, `Fact = Spec` alias
  - Implemented `OverloadContribution.layout(args)` for preliminary layout construction
  - Implemented `Realm.layout(nominal_type)` to resolve and delegate to overload layouts
  - Updated bound expression processing to use `bound.subst(env).as_type()` pattern
  - Aligned field naming: `underlying_bound_expr`/`underlying_bound`, `result_bound_expr`/`result_bound`
  - All tests passing: 101 tests in `just test-all`

## Near-Term Next Steps

1. Finish Milestone 1 by turning remaining `check()` methods into real
   declaration validation, with focused diagnostics for malformed declarations.
2. Implement the first reusable constraint kernel in `src/axis/sem/constraints.py`
   on top of the new binding and index model.
3. Decide and implement how `Type` should be introduced as a usable semantic
   type-value in the scopes that need it.
4. Consolidate the new logic frontend by validating `claim` safety and keeping
   Realm/solver integration documented and covered by tests.
5. In parallel, manually validate `ide/vscode/` in VS Code and simplify the
   grammar further if any freeze or performance issue remains.

## Immediate Action - Protomorph MatchTree Refactor

Target files: `packages/protomorph/src/protomorph/index.py`,
`packages/protomorph/src/protomorph/operators.py`,
`packages/protomorph/src/protomorph/match.py`, `src/axis/sem/index.py`,
`src/axis/sem/binding.py`, `src/axis/sem/entity.py`, and focused tests under
`packages/protomorph/tests/` and `tests/sem/`.

Goal:

- Replace the current Axis-owned specialization/index matching model with a
  Protomorph-owned compiled `MatchTree` model that can drive both spec
  resolution and overload resolution through thin semantic facades.

Design intent:

- `MatchTree` is the compiled matching program.
- `MatchResult` is the structural execution trace produced while descending the
  tree.
- `MatchLeaf` contains only terminal goals/payloads; matching semantics are
  absorbed into the compiled nodes.
- `StructSchema` is the Protomorph IR corresponding to the current Axis
  `BindingStruct` model.
- `bridge` is not part of the public matching contract; matching obtains the
  active bridge from `pm.BRIDGE.get()` where needed.

### Phase A - Stabilize the MatchTree Kernel

- Keep the new tree runtime minimal and explicit:
  - `MatchNode`
  - `MatchTree`
  - `MatchResult`
  - `MatchEnv`
  - `MatchLeaf`
  - `MatchSwitch`
  - `MatchStruct`
  - `MatchVariadicStruct`
- Clarify the role of technical nodes such as `MatchMany`; either harden them as
  real semantics or replace them with a more intentional grouping node.
- Keep `MatchResult` as a trace tree, not as a flattened set of captures or a
  boolean success marker.

Exit criteria:

- The Protomorph test suite covers tree compilation, descent, branching, and
  terminal goal collection.
- `CompileResult` exposes stable terminal leaves/goals for later ambiguity
  analysis.

Status:

- Completed for the first structural iteration.
- Done:
  - added `MatchTree`, `CompileResult`, `ResolveResult`, and structural result nodes
  - added closed `StructSchema` support
  - added first variadic `StructSchema` support via `MatchVariadicStruct`
- added stronger `Struct`/`Index` slicing and helper APIs used by matching code
- Still open:
  - richer ambiguity diagnostics derived from `CompileResult`

### Phase B - Static Discrimination and Compilation Strategy

- Add first-class compile-time discrimination for:
  - exact literal/value keys
  - closed `Struct.Shape`
  - variadic signatures
  - field metatypes via `Val.__type__`
- Revisit the current notion of `Discriminant` and split passive metadata from
  active compile/runtime discriminators if needed.
- Decide whether the compiler remains heuristic-first, greedy, or hybrid.

Exit criteria:

- `MatchTree` can prune closed and variadic candidates before structural descent.
- Variadic candidates no longer rely solely on runtime matching after landing in
  the same broad bucket.

Status:

- Partially completed.
- Done:
  - exact literal/value discrimination
  - closed `Struct.Shape` discrimination
  - first variadic signature guards
  - first field metatype discrimination via `Val.__type__`
- Still open:
  - broader discriminator set
  - policy for greedy vs heuristic compilation

### Phase C - StructSchema Completeness

- Finish the Protomorph-side schema model so it can absorb the current Axis
  binding semantics.
- Define how defaults and optional bindings are represented declaratively in
  `StructSchema`.
- Keep the schema declarative and let compilation expand internal routing
  variants instead of exposing pre-expanded variants to Axis.
- Move `VariadicSignature` ownership fully into Protomorph.

Exit criteria:

- `StructSchema` can represent the current `BindingStruct` semantics closely
  enough to compile both specializations and overloads.
- Defaults, optional named bindings, and open-tail/variadic cases are handled in
  one compilation pipeline.

Status:

- Partially completed.
- Done:
  - closed schemas
  - variadic schemas
  - open-tail semantics
  - internal expansion of closed defaults
  - explicit `VariadicSignature` in Protomorph
- Still open:
  - fuller optional/default semantics
  - richer placeholder/operator interaction

### Phase D - Axis Adapter Layer

- Add a translation layer from Axis semantic bindings to `pm.StructSchema`.
- Introduce schema properties on semantic contributions in place of the old
  pattern/index plumbing.
- Keep declarative binding fields and lowered binding fields distinct.

Exit criteria:

- Axis can build `StructSchema` from semantic bindings without losing binder
  identity, defaults, or variadic information.
- Focused tests prove that inline/block binding forms still converge to one
  semantic representation.

Status:

- Largely completed.
- Done:
  - matching support moved out of `expr` nodes into support modules
  - declarative bindings and lowered bindings split in `axis.sem.binding`
  - semantic contributions now expose `spec_schema` / `param_schema`
  - `Entity` validates `anchor` while `Index` remains purely structural
- Still open:
  - further cleanup of remaining compatibility helpers in `sem.binding`

### Phase E - Replace SpecIndex with MatchTree

- Rewrite Axis semantic indexes as thin wrappers around `pm.compile(...)`
  and `MatchTree.search/resolve`.
- Preserve or improve current reporting for:
  - no match
  - ambiguous match
  - inspection of terminal goal buckets
- Reuse the compiled leaves/goals for ambiguity diagnosis instead of reconstructing
  shape clusters inside Axis.

Exit criteria:

- `SpecIndex` no longer owns the core matching algorithm.
- Specialization resolution in Axis is delegated to Protomorph's compiled tree.

Status:

- Partially completed.
- Done:
  - `SpecIndex` is now folded into `src/axis/sem/index.py`
  - `Entity.spec_index` is a thin facade over `pm.compile(...)`
  - old `spec_index.py`, `overload_index.py`, and `result_index.py` were removed
- Still open:
  - implement `OverloadIndex` behavior beyond the minimal wrapper
  - replace remaining compatibility logic with pure compiled matching

### Phase F - Rebuild Operator / Placeholder / match Semantics

- Reimplement `Operator`, `Placeholder`, and the general matching runtime on top
  of the new `MatchTree` model instead of adapting the old `MatchState`-centric
  system.
- Decide which semantics stay as local pattern nodes and which belong in
  specialized operators.
- Update or replace `packages/protomorph/src/protomorph/match.py` so the public
  matching model is consistent with the compiled tree runtime.

Exit criteria:

- There is one coherent Protomorph matching model rather than a split between
  old `pm.match(...)` semantics and the new compiled tree.
- Operators and placeholders participate naturally in compiled matching and in
  structural result traces.

### Phase G - Overload and Call Resolution Migration

- Reuse the same `StructSchema` + `MatchTree` machinery for overload resolution.
- Retire the Axis-local overload routing logic once the Protomorph matcher can
  handle defaults, ambiguity, and param bounds.
- Connect call resolution to the new compiled backend after specialization
  matching is stable.

Status:

- Not started semantically, but scaffolding exists.
- Done:
  - `OverloadIndex(Index[OverloadContribution])` now exists as a clean wrapper shell
- Still open:
  - overload search semantics
  - overload ambiguity handling
  - integration with call materialization and constraints

Exit criteria:

- The same compiled matching backend can drive both spec and overload matching.
- Axis call resolution no longer depends on separate ad-hoc shape/index logic.

## Logic Frontend and Solver

Target files: `src/axis/items/claim.py`, `src/axis/expr/bound_support.py`,
`src/axis/sem/realm.py`, `packages/protomorph/src/protomorph/logic.py`,
`packages/protomorph/src/protomorph/solvers/`, and focused tests.

- Add a first logical frontend in Axis using `claim`, `where:`, `when:`, and
  `-` body clauses.
- Lower empirical facts and conditional claims into semantic contributions.
- Keep logic execution in Protomorph behind `LogicBackend` and `LogicSolver`.
- Implement a first saturated solver using `GlobalFixedPointSolver`.
- Enforce a conservative safety policy for conditional claims.

Exit criteria:

- Claims parse and lower into facts/clauses with dedicated tests.
- `Realm` aggregates logical contributions and delegates queries to the solver.
- Recursive logical derivations work through fixed-point saturation.
- Unsafe conditional claims fail with focused diagnostics.

Status:

- Completed for v1.
- Done:
  - Added `claim` frontend syntax with `where:` and `when:` blocks
  - Lowered `extends` and explicit claims into fact/clause contributions
  - Added `LogicBackend`, `LogicSolver`, and `GlobalFixedPointSolver`
  - Wired `SemanticBridgeBase.solve(...)` and `Realm.logic_solver`
  - Added recursive solver coverage and first conservative claim-safety checks
- Still open:
  - richer safety validation beyond the current conservative checks
  - integrating logical queries with future entity/spec match providers
  - adding alternate solver strategies beyond global saturation

## Milestone 2 - Constraint Kernel

Target files: new `src/axis/sem/constraints.py`, `src/axis/sem/entity.py`, and
new focused tests.

- Introduce reusable helpers for argument materialization, default insertion,
  and bound satisfaction.
- Proposed primitives:
  - `materialize_args(...)`
  - `satisfies_bound(...)`
  - `validate_bindings(...)`
- Centralize diagnostics for missing args, unknown keys, duplicate supply,
  unbound symbols, and defaults that violate bounds.

Status:

- Current primary milestone.
- Prerequisites now in place:
  - declarative `BindingStruct`
  - `LoweredBindingStruct`
  - `StructSchema`
  - `Index` / `SpecIndex` facade over `pm.compile(...)`
  - semantic layout explicitly disabled until rebuilt on top of the new model

Exit criteria:

- Unit tests cover valid and invalid materialization.
- Bound validation exists in one place and is reused by later specialization
  and call resolution.

## Milestone 3 - Specialization Resolution

Target files: `src/axis/sem/entity.py`, possible new helper modules under
`src/axis/sem/`, and new tests.

- Resolve specialization candidates by shape, defaults, and `spec_bounds`.
- Build the instantiation environment for `Self` and `SpecVar` bindings.
- Report `no match` and `ambiguous match` explicitly.
- Keep the resolution logic in `sem`, not in `expr.ir`.

Exit criteria:

- A specialization can be classified as valid, invalid, or ambiguous.
- Tests cover exact match, missing specialization args, defaulted args, and
  bound violations.

## Milestone 4 - Call and Overload Resolution

Target files: new call-resolution helpers under `src/axis/sem/`,
`src/axis/sem/entity.py`, and new tests.

- Introduce a semantic API that resolves a call against an `Entity`.
- Resolve the callee entity, then specialization, then overload.
- Materialize call arguments, apply defaults, and validate `param_bounds`.
- Select one overload or report `no match` / `ambiguous match`.

Exit criteria:

- Calls can be validated against declared parameter bounds.
- Tests cover valid calls, missing args, unknown args, defaults, and overload
  ambiguity.

## Milestone 5 - Result Semantics and Indexing Cleanup

Target files: `src/axis/sem/entity.py`, `src/axis/items/defs/fn.py`, and
related tests.

- Lower and instantiate return declarations in the selected specialization /
  overload environment.
- Revisit `impl_by_result` so result indexing reflects actual implementations,
  not only parameterless cases.
- Connect additional declaration kinds such as `Global` only as needed by the
  resolver.

Exit criteria:

- Resolved calls can expose a semantic return value or return type.
- Result indexing matches the actual implementation model.

## Milestone 6 - Coverage and Next Semantics

Target files: `tests/`, `docs/`, and any cleanup needed in `src/axis/sem/`.

- Add focused tests for declaration validation, specialization validity, and
  call validity.
- Document the first-pass matching rules once they stabilize.
- Only after that, evaluate whether richer assignability belongs in `sem` or in
  the `Realm` bridge.

Exit criteria:

- Semantic validation is covered by dedicated tests, not only by construction
  tests.
- The first-pass rules are explicit and stable enough to extend.

## Out of Scope for the First Pass

- General subtyping or variance.
- Operator semantics and `combine(...)` rules.
- Rich qualifier algebra beyond strict declared bounds.
- Runtime evaluation strategy.
- Implicit coercions or host-language conversions.

## Immediate Implementation Order

1. Restore the green baseline under `just test`.
2. Fix declaration integrity: inline bindings, `QualDef`, `Type`, and returns.
3. Replace Axis-local matching/indexing with `StructSchema` + `pm.compile(...)` facades.
4. Add the constraint kernel in `sem`.
5. Implement specialization resolution.
6. Implement call and overload resolution.
7. Rebuild semantic layout on top of the new matching/binding model.
8. Revisit result semantics and expand tests.

Updated status note:

- Steps 1 and 3 are complete in their current iteration.
- Step 2 is partially complete.
- The logic frontend/solver milestone is complete for v1.
- Step 4 remains the current primary semantic milestone.
- Semantic layout is intentionally disabled while the new binding/index model settles.
- VS Code editor support is now an active parallel track, but it does not change
  the semantic implementation order above.
