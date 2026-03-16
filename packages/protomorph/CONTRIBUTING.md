# Protomorph Contributing Guide

This package favors a small explicit runtime, a controlled bootstrap, and minimal duplicated state.

## Architecture rules

- `protomorph.__init__` is the package orchestrator and public API surface.
- Bootstrap happens in `__init__`, after package imports, in a deliberate order.
- Do not reintroduce bootstrap helpers in side modules.
- `NativeRegistry` is the runtime owner for native type mappings, python transforms, and atomic layouts.
- If some runtime data already belongs to `NativeRegistry`, do not mirror it in package globals.

## Imports and dependency style

- Treat a module dependency as direct only when it is needed in module global scope.
- Type hints do not count as direct dependencies.
- Use `import protomorph as pm` for cross-module type hints and package-level coordination.
- Prefer `pm.Val`, `pm.Type`, `pm.Struct`, etc. in annotations.
- Do not add imports only to satisfy annotations when `pm.*` is enough.
- Keep first-order imports explicit when they are required for inheritance, descriptors, constants, or bootstrap-time evaluation.

## Global state policy

- Minimize package globals.
- Globals are allowed only when they are:
  - public API with real users,
  - bootstrap state, or
  - runtime singletons.
- Prefer private globals over exported globals.
- Avoid parallel sources of truth.
- `pm._ANCHOR_TYPE` is bootstrap-owned shared state.

## Flux and registry policy

- Use `flux.property` for registry-backed source-of-truth views.
- Use `flux.method` for cached derivations and queries.
- Invalidate flux properties explicitly on mutation.
- Avoid manual caches if the data already belongs to the registry model.
- `NativeRegistry.native_types` is the canonical host/native mapping.

## Value/type model

- `type.construct(...)` is the Python-friendly entry point.
- `type.decode(raw)` is the canonical typed deserializer.
- `type.serialize(data)` is the low-level type serializer.
- `value.encode()` is the public value serializer.
- `type.layout()` describes semantic shape.
- `Val.wrap()` should validate the real semantic condition directly, not through path-based metadata heuristics.

## Simplification policy

- Prefer fewer concepts over more compatibility layers.
- Remove dead indirection when it no longer expresses meaningful architecture.
- Avoid path-based or magic-string classification when a structural check is enough.
- Keep helper modules small; if a helper is only a compatibility shim and has no users, remove it.

## Testing guidelines

This package uses a path-oriented test strategy.

The goal is not only to assert outcomes, but to make the intended execution path obvious so future contributors can extend coverage deliberately and diagnose regressions quickly.

### Core principles

- Write tests by subsystem, not as one large smoke file.
- Cover happy paths first, then branch paths, then exceptional paths.
- Name each test after the route it intends to exercise.
- Make the expected control flow visible in the test name and assertion shape.
- Prefer small, purpose-built fixtures over shared magical setup.
- When a behavior is surprising, preserve it with a test before changing it.

### File organization

Group tests by runtime area so missing coverage is easy to spot:

- `test_core_api.py`
- `test_failure_paths.py`
- `test_layout_and_native.py`

Shared fixtures and helper classes live in `tests/support.py`.

When adding coverage for a new subsystem, prefer a new focused file over growing an unrelated one.

### Naming pattern

Use names that describe the exact route being exercised.

Recommended pattern:

- `test_<surface>_route_<expected_path>`
- `test_<surface>_happy_paths_cover_<paths>`
- `test_<surface>_exception_paths_cover_<failures>`

### Assertions

- Assert the most semantically useful property first.
- Use `repr(...)` assertions when representation is part of the public debugging contract.
- For unordered results, assert sets instead of string order.
- When validating a branch-specific behavior, keep assertions narrow so failures identify the branch clearly.
- Prefer explicit `assertRaises` around the smallest possible call.
- Prefer the type-centric API over older internal implementation details.
- When testing shape-dependent behavior, assert the `Layout` kind explicitly before asserting fields or atomic contracts.

### Coverage workflow

Run:

```bash
just test
```

`just test` is the default verification command and includes coverage reporting.

Use coverage to fill missing happy paths first, then branches, then exceptional behavior.
