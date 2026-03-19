# Axis Coding Style

This document captures repository-specific style rules for imports, type
annotations, semantic layering, and a few recurring architectural patterns.

## Imports

- Prefer package imports:
  - `import protomorph as pm`
  - `from axis import syn, sem`
- Prefer package-qualified names in code and in type annotations instead of
  importing symbols only to shorten references.
- Use direct internal imports when they represent a hard dependency at runtime.
- Use weak direct imports only when the imported module is clearly foundational
  and there is no suspected circularity.
- Avoid direct internal imports used only for annotations.

## Type Annotations

- In annotations, prefer package-qualified names:
  - `value: pm.Val`
  - `fields: dict[str, pm.Val]`
  - `scope: sem.Scope`
- Type annotations do not count as dependencies for architectural reasoning.
- Do not import internal names only to shorten annotations.

## Dependency Policy

- Strong dependency:
  - class bases
  - top-level executable references
  - global initialization using symbols from another module
- Weak dependency:
  - deferred access inside methods or functions
  - local imports used to avoid unnecessary coupling
- Type annotations do not count as dependencies.

## Module Responsibilities

- `axis.expr`
  - represents syntax and expression nodes
  - should stay focused on syntax and local lowering helpers
- `axis.expr.ir`
  - lowers syntax into declarative IR
  - should not own semantic resolution
- `axis.sem`
  - owns semantic lowering, validation, indexing, and entity logic
- `protomorph`
  - owns generic matching, indexing, schemas, and runtime machinery

## Matching and Indexing

- Axis semantic indexes should be thin facades over `pm.compile(...)`.
- Avoid duplicating matching logic in `axis.sem` when `protomorph` can own it.
- Prefer `pm.StructSchema` over ad-hoc shape/signature logic.
- Entity-level methods may validate nominal identity (`anchor`) before delegating
  to a structural index.

## Bindings

- Keep declarative bindings separate from lowered bindings.
- Prefer nested field types:
  - `BindingStruct.Field`
  - `LoweredBindingStruct.Field`
- Bounds and defaults should be lowered once per scope, then reused.

## Struct Usage

- Make `None` explicit in struct key types:
  - `pm.Struct[str, T]`
  - `pm.Struct[str | None, T]`
- Prefer `prefix`, `middle`, `suffix`, and `split_variadic` over manual index slicing.
- Prefer `with_values(...)` and `map(...)` over reconstructing structs with
  `from_keys(...)` when keys do not change.

## Testing

- Add direct tests for each representation case, not only integration coverage.
- Cover positive, negative, ambiguous, and edge cases.
- When a subsystem is intentionally disabled, tests should assert the explicit
  failure message rather than silently skipping behavior.
