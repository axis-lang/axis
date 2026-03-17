# Axis Tests

Axis tests use `unittest` and are organized by theme:

- `tests/bounds/`: bound lowering, scopes, and expression-to-semantic conversion
- `tests/defs/`: def parsing and contribution/binding behavior
- `tests/helpers_tests/`: tests for test infrastructure itself
- `tests/sem/`: semantic bridge, layouts, projection, and realm behavior
- `tests/syn/`: parser and syntax-level behavior

Testing conventions:

- New semantic tests should usually inherit from `tests.helpers.StdPackageTestCase`.
- Use `tests.helpers.InlinePackageTestCase` for small inline packages and regression tests.
- `std-core` is always the base STD layer for semantic tests.
- Prefer string-based semantic assertions when possible:
  - `assertBoundEq(...)`
  - `assertTypeEq(...)`
  - `assertProjectEq(...)`
  - `assertAnchor(...)`
- Prefer `TestPackage.with_def(...)` / `TestPackage.with_unit(...)` for inline fixtures.
- Inline multiline Axis source strings are dedented automatically, so write them with
  natural indentation.
- For direct def parsing, prefer `TestPackage.parse_def(DefCls, source)`.
- If a test intentionally triggers a structured report error and the console output is
  noise, use `self.suppress_report_output()` around the assertion.
