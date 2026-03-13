# Semantic Layer Roadmap

## Goal

Make `axis.sem` capable of deciding whether a declaration, specialization, and
call are semantically valid against declared bounds, using `protomorph` as the
semantic backend.

## Current Baseline

- The repository already has the right scaffolding: `Realm`, `Context`,
  `Entity`, lexical `Scope`, and bound/default lowering in `axis.expr.ir`.
- `spec_scope`, `overload_scope`, `spec_bounds`, `param_bounds`,
  `spec_defaults`, and `param_defaults` already exist.
- What is still missing is validation: there is no semantic relation like
  `satisfies(actual, bound)`, no specialization resolver, and no call resolver.
- Declaration support is still incomplete: inline bindings are currently lost,
  `QualDef` emits no contributions, `returns` remain mostly as raw syntax, and
  `Type` is not yet a usable type-value in semantic scopes.
- `just test` is the gate for all milestones and must be green before moving to
  the next stage.

## Design Rules

- `axis.expr.ir` remains a lowering layer. It builds semantic values from AST,
  but it does not decide validity.
- `axis.sem` owns validation, candidate selection, ambiguity handling, and
  diagnostics.
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

- `std.core` qualifier-like definitions appear in `entities_by_anchor`.
- Inline and block binding forms produce the same semantic binding model.
- Contributions expose bounds, defaults, and returns as semantic values with
  meaningful diagnostics.

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
3. Add the constraint kernel in `sem`.
4. Implement specialization resolution.
5. Implement call and overload resolution.
6. Revisit result semantics and expand tests.
