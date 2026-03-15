# Protomorph Test Suite Guidelines

This package uses a path-oriented test strategy.

The goal is not only to assert outcomes, but to make the intended execution path obvious so future contributors can extend coverage deliberately and diagnose regressions quickly.

## Runtime Model

The current Protomorph runtime is organized around a small set of core ideas:

- `type.construct(...)` is the Python-friendly entry point.
- `type.decode(raw)` is the canonical typed deserializer.
- `type.serialize(data)` is the low-level type serializer.
- `value.encode()` is the public value serializer.
- `type.layout()` describes the semantic shape of a type.

Layout kinds:

- `AtomicLayout(valid_types=...)` validates raw scalar-like host values.
- `StructLayout(fields=..., builtin_cls=...)` describes structured values and optional host materialization.

Tests should prefer these surfaces over older implementation details.

## Core Principles

- Write tests by subsystem, not as one large smoke file.
- Cover happy paths first, then branch paths, then exceptional paths.
- Name each test after the route it intends to exercise.
- Make the expected control flow visible in the test name and assertion shape.
- Prefer small, purpose-built fixtures over shared magical setup.
- When a behavior is surprising, preserve it with a test before changing it.

## File Organization

Group tests by runtime area so missing coverage is easy to spot:

- `test_core_api.py`
- `test_failure_paths.py`
- `test_layout_and_native.py`

Shared fixtures and helper classes live in `tests/support.py`.

When adding coverage for a new subsystem, prefer a new focused file over growing an unrelated one.

## Naming Pattern

Use names that describe the exact route being exercised.

Recommended pattern:

- `test_<surface>_route_<expected_path>`
- `test_<surface>_happy_paths_cover_<paths>`
- `test_<surface>_exception_paths_cover_<failures>`

Examples:

- `test_struct_and_struct_type_routes_cover_value_and_schema_construction`
- `test_construct_route_rejects_opaque_types_and_layout_mismatches`
- `test_native_registry_routes_cover_template_layout_and_construct`

The name should answer: "what path is this test trying to force?"

## Test Construction Order

For each API or module, add tests in this order:

1. Happy path for the main public route.
2. Alternative branches of the same route.
3. Boundary cases.
4. Exceptional or unsupported paths.
5. Encoding, layout, and representation checks that make debugging easier.

This keeps the suite readable and makes it easier to see what still lacks coverage.

## Assertions

- Assert the most semantically useful property first.
- Use `repr(...)` assertions when representation is part of the public debugging contract.
- For unordered results, assert sets instead of string order.
- When validating a branch-specific behavior, keep assertions narrow so failures identify the branch clearly.
- Prefer explicit `assertRaises` around the smallest possible call.
- Prefer the type-centric API (`type.decode(...)`, `type.construct(...)`, `value.encode()`) over legacy global helpers.
- Prefer `spec(...)`, `struct_type(...)`, and `union_value(...)` when expressing new API examples over hand-built structural constants.
- When testing codecs, distinguish clearly between `type.serialize(data)` and `value.encode()`.
- When testing shape-dependent behavior, assert the `Layout` kind explicitly before asserting fields or atomic contracts.

## Coverage Workflow

Coverage is part of the intended development loop.

Run:

```bash
just test
```

`just test` is the default verification command and includes coverage reporting.
`just coverage` is kept as an alias.

Coverage is configured in `packages/protomorph/pyproject.toml` with branch coverage enabled.

Use the report to choose the next tests intentionally:

- fill missing happy paths first for major public modules
- then target unvisited branches
- then lock down exceptional behavior

## When Expanding the Suite

- Add tests that target one missing route at a time.
- Avoid broad integration tests when a direct unit route is available.
- If a new test exposes surprising current behavior, keep the test and document whether it is intentional or provisional.
- If a bug depends on a very specific construction, encode that construction directly in the test instead of hiding it behind helpers.
- Exercise both canonical tuple decoding and Python-friendly construction when covering structural layouts.

## Fixture Policy

- Keep helpers in `tests/support.py` explicit and boring.
- Shared helpers should model reusable shapes, not hide control flow.
- If a fixture is only needed by one file, keep it in that file.

## Review Standard

A good Protomorph test should make all of the following obvious:

- which module or public surface it targets
- which route or branch it intends to traverse
- why the chosen input triggers that route
- what observable contract must hold afterward

If those four things are not obvious from the file, test name, and assertions, rewrite the test until they are.
