# Axis Coding Style

This document captures the current repository-wide rules for code structure,
imports, package surfaces, public API design, and testing philosophy.

It is intentionally opinionated. Prefer clean cuts over compatibility layers,
explicit architecture over accidental behavior, and public-surface tests over
implementation-detail tests.

## Core Principles

- Prefer the smallest clean design over incremental clutter.
- Do not preserve dead compatibility paths unless there is a real external need.
- Do not add shims, aliases, wrappers, or compatibility adapters "just in case".
- If a design is being replaced, finish the replacement and remove the old path.
- Avoid parallel sources of truth.
- Keep bootstrap and runtime ownership explicit.
- Treat package structure and imports as part of the architecture, not mere style.

## Imports

- Prefer package imports:
  - `import protomorph as pm`
  - `from axis import syn, sem`
- Prefer package-qualified names in code and annotations instead of importing
  symbols only to shorten references.
- Type hints do not count as architectural dependencies.
- Do not add direct imports only to satisfy annotations when `pm.*`, `sem.*`,
  or other package namespaces are enough.
- Use direct internal imports only when they are real runtime dependencies:
  - class bases
  - descriptors
  - constants
  - module initialization
  - top-level executable behavior
- Prefer weak or local imports only when they genuinely reduce coupling and do
  not hide the real module dependency graph.
- Avoid `typing.TYPE_CHECKING` as a structural escape hatch. If imports are
  awkward, fix the dependency structure instead.

## Package `__init__` Policy

- Package surfaces should generally be assembled with `from .subpackage import *`.
- Prefer naming-based privacy over `__all__`.
- Avoid `__all__` by default.
- Private names must start with `_`.
- If a module is re-exported with `import *`, keep support imports private too:
  - `_Any`
  - `_cast`
  - `_Callable`
  - etc.
- Do not hand-maintain long export lists in `__init__.py` unless there is a
  concrete exception that justifies it.
- If something should be available from the package root, make that decision
  intentionally as public API. Do not leak it accidentally.

## Namespace Policy

- When a subsystem starts accumulating many types with the same prefix, prefer a
  namespace package over repeating the prefix in every public symbol.
- Example:
  - prefer `pm.match.Tree`, `pm.match.CaseSummary`, `pm.match.GuardShape`
  - instead of `pm.MatchTree`, `pm.MatchCaseSummary`, `pm.MatchGuardShape`
- When making this kind of cleanup, do the rename completely.
- Do not keep both naming schemes alive.
- Do not leave compatibility aliases behind unless there is a concrete external
  compatibility requirement.

## Public API Cleanliness

- Public API should be deliberate, small, and coherent.
- If a helper is private, keep it private and do not test or export it from the
  package root.
- If a helper is promoted because users need it, promote it cleanly as public API
  and move tests to that public name.
- If code outside the defining module needs a symbol, either:
  - promote it to a real public API, or
  - refactor so the cross-module dependency disappears.
- Prefer one clean public entry point over several overlapping ones.
- Remove dead indirection when it no longer expresses meaningful architecture.
- Avoid magic-string or path-based classification when a structural check is enough.
- Keep helper modules small. If a helper exists only as a compatibility shim,
  remove it.

## Compatibility and Cleanup Policy

- Do not keep old and new structures alive at the same time without a real need.
- Do not leave partially migrated packages, duplicate modules, or fallback trees.
- After a rename or namespace cleanup, remove the old surface in the same change.
- When refactoring package layout:
  - move the implementation
  - update imports
  - update tests
  - delete the abandoned path
- Prefer a short period of breakage during refactor over long-term architectural
  debt from compatibility glue.

## Dependency Policy

- Strong dependency:
  - class inheritance
  - top-level executable references
  - global initialization
  - bootstrap ordering
- Weak dependency:
  - deferred use inside methods or functions
  - local imports used to avoid unnecessary coupling
- Type annotations do not define dependency hierarchy.
- The runtime import graph should reflect the real architecture.

## Bootstrap and Global State

- `protomorph.__init__` is the package orchestrator and public API surface.
- Bootstrap should happen in `__init__`, after package imports, in a deliberate
  and readable order.
- Do not reintroduce bootstrap helpers in side modules.
- Minimize package globals.
- Globals are allowed only when they are:
  - real public API
  - bootstrap-owned shared state
  - runtime singletons
- Prefer private globals over exported globals.

## Typing and Annotations

- Use type annotations for public functions, methods, and class attributes.
- Prefer package-qualified annotations:
  - `value: pm.Carrier`
  - `shape: pm.match.ShapeSummary`
  - `scope: sem.Scope`
- Prefer `type | None` over `Optional[type]` at runtime.
- For genuinely arbitrary payloads, prefer `Any` over `object`.
- Do not import internal names only to shorten annotations.

## Naming

- Classes: CamelCase
- Functions and variables: snake_case
- Constants: UPPER_CASE
- Private helpers: leading underscore
- Do not encode redundant subsystem prefixes in public types when a namespace is
  already carrying that information.

## Formatting

- Use 4-space indentation.
- Keep line length reasonable.
- Wrap complex expressions instead of compressing them.
- Use f-strings for formatting.
- Keep docstrings short and action-oriented.
- Avoid trailing whitespace.

## Errors and Diagnostics

- Use `TypeError` for invalid API use or invalid types.
- Use `ValueError` for invalid values or invalid state.
- Preserve context when re-raising with `raise ... from exc` where useful.
- Keep error messages user-facing and precise.
- Prefer structured diagnostics over raw print/debug output in core logic.

## Testing Philosophy

- Tests should validate public behavior, public surface, and usability.
- Prefer end-to-end or behavior-oriented tests over tests that mirror private
  implementation details.
- Do not test private helpers through package-root imports.
- If a helper seems important enough to test directly, first decide whether it
  should become public API.
- When a public feature can be exercised through a user-facing entry point,
  prefer that route over testing internal plumbing.
- Keep assertions focused on semantically useful outcomes.
- For unordered results, assert sets instead of order-dependent strings.
- Use explicit `assertRaises` around the smallest failing call.

## Test Organization

- Write tests by subsystem, not as one large smoke file.
- Cover happy paths first, then branch paths, then exceptional paths.
- Name tests after the route or behavior being exercised.
- Prefer small, purpose-built fixtures over magical shared setup.
- When a behavior is surprising, preserve it with a test before changing it.
- When adding coverage for a new subsystem, prefer a new focused file over
  growing an unrelated one.

Recommended naming patterns:

- `test_<surface>_route_<expected_path>`
- `test_<surface>_happy_paths_cover_<paths>`
- `test_<surface>_exception_paths_cover_<failures>`

## Module Responsibilities

- `axis.expr`
  - syntax and local lowering helpers only
- `axis.expr.ir`
  - declarative IR lowering
  - should not own semantic resolution
- `axis.sem`
  - semantic lowering, validation, indexing, and entity logic
- `protomorph`
  - generic matching, indexing, type/value runtime machinery, and schemas

## Matching and Indexing

- Axis semantic indexes should be thin facades over `protomorph` facilities.
- Avoid duplicating matching logic in `axis.sem` when `protomorph` can own it.
- Prefer structural and typed representations over ad-hoc signatures or magic
  shape logic.

## Flux, Records, and Immutability

- Use `@flux.property` for derived, dependency-tracked values.
- Use `@flux.method` for cached derivations and queries.
- Invalidate flux properties explicitly on mutation.
- Do not mutate immutable/consed objects after construction.
- Use persistent updates rather than in-place mutation.
- Avoid manual caches when the data already belongs to the registry or flux model.

## Repository Notes

- Follow existing patterns where they are clean and current, not where they are
  clearly transitional or obsolete.
- Avoid new dependencies unless there is a concrete need.
- Prefer incremental implementation steps, but each committed design step should
  still be architecturally clean.
