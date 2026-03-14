# Protomorph Test Suite Guidelines

This package uses a path-oriented test strategy.

The goal is not only to assert outcomes, but to make the intended execution path obvious so future contributors can extend coverage deliberately and diagnose regressions quickly.

## Core Principles

- Write tests by subsystem, not as one large smoke file.
- Cover happy paths first, then branch paths, then exceptional paths.
- Name each test after the route it intends to exercise.
- Make the expected control flow visible in the test name and assertion shape.
- Prefer small, purpose-built fixtures over shared magical setup.
- When a behavior is surprising, preserve it with a test before changing it.

## File Organization

Group tests by runtime area so missing coverage is easy to spot:

- `test_api_happy_paths.py`
- `test_api_exception_paths.py`
- `test_base_and_format.py`
- `test_bridge_paths.py`
- `test_refs_and_vars.py`
- `test_struct_and_map_paths.py`
- `test_types_and_qualifiers_paths.py`
- `test_native_frontend_and_backend_paths.py`

Shared fixtures and helper classes live in `tests/support.py`.

When adding coverage for a new subsystem, prefer a new focused file over growing an unrelated one.

## Naming Pattern

Use names that describe the exact route being exercised.

Recommended pattern:

- `test_<surface>_route_<expected_path>`
- `test_<surface>_happy_paths_cover_<paths>`
- `test_<surface>_exception_paths_cover_<failures>`

Examples:

- `test_val_route_accepts_struct_inputs_and_sequences`
- `test_registry_construct_routes_cover_success_and_exceptional_paths`
- `test_spec_type_exception_routes_reject_incompatible_meta_payloads`

The name should answer: "what path is this test trying to force?"

## Test Construction Order

For each API or module, add tests in this order:

1. Happy path for the main public route.
2. Alternative branches of the same route.
3. Boundary cases.
4. Exceptional or unsupported paths.
5. Formatting and representation checks for debugging value.

This keeps the suite readable and makes it easier to see what still lacks coverage.

## Assertions

- Assert the most semantically useful property first.
- Use `repr(...)` assertions when representation is part of the public debugging contract.
- For unordered results, assert sets instead of string order.
- When validating a branch-specific behavior, keep assertions narrow so failures identify the branch clearly.
- Prefer explicit `assertRaises` around the smallest possible call.

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
