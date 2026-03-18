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
- `packages/protomorph` has evolved significantly and now exposes a layout-based
  semantic backend centered on:
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
- `axis.sem` now aligns with Protomorph's layout-based model:
  - `Realm.layout(nominal_type)` resolves entities and delegates to overload layouts
  - `OverloadContribution.layout(args)` constructs preliminary layouts from param bounds
  - Bound expressions use `bound.subst(env).as_type()` pattern
- Declaration lowering has also progressed:
  - qualifier declarations expose `underlying_bound_expr` / `underlying_bound`
  - function implementations expose `result_bound_expr` / `result_bound`
  - inline and block `returns` forms are merged before semantic contribution creation
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
- `axis.sem` should talk to `protomorph` using the current layout-centric model,
  not older ad-hoc structural hooks.
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

1. Finish Milestone 1 by turning contribution `check()` methods into real
   declaration validation, with focused diagnostics for malformed declarations.
2. Decide and implement how `Type` should be introduced as a usable semantic
   type-value in the scopes that need it.
3. Start Milestone 2 by introducing a dedicated constraint kernel in
   `src/axis/sem/constraints.py` for argument materialization, default insertion,
   and bound satisfaction.
4. Add focused tests for that kernel before beginning specialization and call
   resolution work.
5. In parallel, manually validate `ide/vscode/` in VS Code and simplify the
   grammar further if any freeze or performance issue remains.

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
3. Align `axis.sem` with the current Protomorph bridge and layout model.
4. Add the constraint kernel in `sem`.
5. Implement specialization resolution.
6. Implement call and overload resolution.
7. Revisit result semantics and expand tests.

Updated status note:

- Steps 1 and 3 are complete.
- Step 2 is partially complete.
- Step 4 is the current primary semantic milestone.
- VS Code editor support is now an active parallel track, but it does not change
  the semantic implementation order above.
