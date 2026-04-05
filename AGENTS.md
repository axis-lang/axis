# AGENTS

This file guides agentic coding agents working in /home/jdluque/Workspace/axis.
Primary scope: repository root (Axis project).

Repository layout
- src/axis: main Axis package (parser, semantic model, evaluator, TUI)
- codebase: example Axis source files
- tests: unittest suite for Axis
- docs: Sphinx docs (Markdown via MyST)
- packages/protobase: Protobase runtime (has its own AGENTS.md)

Tooling rules discovery
- No Cursor rules found (.cursor/rules/ or .cursorrules).
- No Copilot instructions found (.github/copilot-instructions.md).

Environment expectations
- Python 3.13+ (see pyproject.toml)
- Poetry for env and dependency management
- Use `poetry run` to ensure correct environment

Working directory
- Run commands from repo root unless noted
- For Protobase-specific work, use packages/protobase and follow its AGENTS.md

Build/lint/test commands (Axis)
- List tasks: `just help`
- Run app: `just launch -- --help`
- Tests (all): `just test`
- Tests (all, direct): `poetry run python -m unittest discover -s tests`
- Tests (all packages + root): `just test-all`
- Type checks: `poetry run pyright`
- Docs build: `just docs`
- Parser generation: `just gen-parser`

Single-test commands (unittest)
- Single file: `poetry run python -m unittest tests.test_syn`
- Single class: `poetry run python -m unittest tests.test_syn.TestSyn`
- Single test: `poetry run python -m unittest tests.test_syn.TestSyn.test_parse_basic`

Interactive / watch commands
- Watch tests + launch: `just watch`
- REPL mode: `poetry run python -m axis --repl`
- Watch mode: `poetry run python -m axis --watch`
- TUI mode: `poetry run python -m axis --tui`

Docs (Sphinx + MyST)
- Source: `docs/*.md`
- Build output: `dist/docs`
- Theme: pydata-sphinx-theme (configured in docs/conf.py)
- Use MyST directives (e.g. ```{toctree}```) in Markdown
- Keep README and docs in sync when behavior changes

Parser tooling
- Grammar: `src/axis/syn/grammar/Axis.g4`
- Regenerate: `just gen-parser` (uses antlr4)

Code style: general
- Follow existing patterns; there is no auto-formatter configured
- Keep functions small and explicit over cleverness
- Avoid new dependencies unless required
- Prefer incremental changes that preserve behavior

Imports
- Order groups: standard library, third-party, local modules
- Separate groups with a blank line
- Prefer explicit imports; wildcard only in `__init__.py` for re-exports
- Keep relative imports within axis package where possible
- For Axis internals, prefer top-level package imports and namespace access
  (`from axis import log` -> `log.Report`, `log.error(...)`) over deep imports
  like `from axis.log.report import Report`

URS import policy (`packages/protomorph/src/pm/reasoning/`)
- Apply this policy strictly and systematically across all URS modules.
- Categorize every dependency as exactly one of:
  - `annotation-only`
  - `import-time runtime`
  - `runtime-late`
- `annotation-only`
  - Always import `import pm` and `from pm import reasoning as urs`.
  - All URS type hints must use qualified names through `urs.*` or `pm.*`.
  - Do not add direct sibling imports only to shorten annotations.
  - Example: `db: urs.Database`, `goal: pm.Spec`, `tables: urs.SessionTables`.
- `import-time runtime`
  - Use selective direct imports only for symbols actually needed while the module
    is importing or for top-level executable runtime use.
  - These imports define the real dependency graph and layering.
  - Example: `from .stratify import build_dependency_graph`.
- `runtime-late`
  - Decide the import form from the origin module:
    - if that module is already present in `import-time runtime`, use that path
    - otherwise use the global rule (`urs.*` / `pm.*`) instead of introducing a
      new hidden sibling dependency
- Do not use `typing.TYPE_CHECKING` in URS.
- Treat as private only the names that remain inside their defining module.
  - If a symbol is referenced from another URS module, do not keep it private by
    convention alone; either export a public name or refactor so it stops crossing
    module boundaries.
- Keep `pm.reasoning.__init__` ordered according to the real URS layering so the
  `urs.*` annotation namespace is available during module initialization.
- This policy resolves three recurring problems:
  - annotation imports accidentally creating fake architectural dependencies
  - circular imports hidden inside local imports and `TYPE_CHECKING`
  - cross-module use of pseudo-private helpers without an explicit public surface

Formatting
- Use 4-space indentation
- Keep line length reasonable; wrap complex expressions
- Use f-strings for formatting
- Keep docstrings short and action-oriented
- Avoid trailing whitespace

Typing and annotations
- Use type annotations for public functions, methods, and class attributes
- Codebase uses modern typing (PEP 695 generics, Self, ParamSpec)
- Prefer `type | None` over `Optional[type]` at runtime
- Use the protobase `_` sentinel for required fields after defaults
- Use `TYPE_CHECKING` for type-only imports and overloads outside URS; in
  `packages/protomorph/src/pm/reasoning/` follow the URS import policy above and
  do not use it
- For genuinely arbitrary payloads, prefer `typing.Any` over `object`; in URS do
  not use `object` as a placeholder for unknown runtime values

Naming conventions
- Classes: CamelCase
- Functions/variables: snake_case
- Constants: UPPER_CASE
- Private helpers: leading underscore

Error handling
- Use TypeError for misuse of API or invalid types
- Use ValueError for invalid values or state
- Preserve context when re-raising: `raise ... from exc`
- Prefer structured reports when available (axis.log.report)
- Keep error messages user-facing and precise

Logging and diagnostics
- Use `axis.log.report` builders for diagnostics in semantic/eval layers
- Emit reports in checks and avoid raw print/traceback in core logic

Protobase / Flux usage (Axis)
- Use `Inmutable` for stable value objects and evaluators
- Use `Consed` for canonical nodes in semantic graphs
- Use `@flux.property` for derived, dependency-tracked values
- Use `@flux.method` for derived queries with args/kwargs
- Use `@flux.input` for the only mutable inputs
- Queries must return concrete values (no generators/async)
- Args/kwargs must be hashable
- Do not mutate `flux.input` during a query

Immutability and records
- Do not mutate attributes on Inmutable/Consed after construction
- Use `mutate(record, **attrs)` for persistent updates
- Defaults are deep-copied in Record init; avoid relying on shared defaults

Caching helpers
- Prefer `protobase.cached_property` or `slot_cached_property`
- Avoid `functools.cached_property` for protobase Objects

Incremental dataflow conventions
- Keep the pipeline: Package -> Item(Context) -> Realm -> Entity
- Items emit contributions via `@flux.property`
- Realm is the sole aggregator for entities_by_anchor
- IO should live in source layer (SourceFile.content, SourceDir.glob)

Sources and IO
- Prefer Source/SourceFile abstractions over direct file reads
- Invalidation should go through `FSWatcher` or `@flux.input`

Testing guidelines
- Tests use unittest; keep them deterministic
- Name tests `test_*.py` for discovery
- Prefer focused tests over end-to-end tests for core logic
- Organize Axis tests by theme under subdirectories of `tests/`
  (`tests/bounds/`, `tests/defs/`, `tests/helpers_tests/`, `tests/sem/`, `tests/syn/`)
- Prefer `tests.helpers.StdPackageTestCase` or `tests.helpers.InlinePackageTestCase`
  for new Axis semantic tests
- All Axis semantic tests should assume `std-core` is loaded as the base STD layer
- Prefer string-based semantic assertions such as `assertBoundEq`, `assertTypeEq`,
  `assertProjectEq`, and `assertAnchor` over manual `pm.nominal_type(...)` /
  `pm.nominal_qual(...)` construction when practical
- Use `TestPackage.with_def(...)` / `TestPackage.with_unit(...)` for inline package
  fixtures instead of assembling filesystem fixtures unnecessarily
- Multiline inline sources passed to test helpers are dedented automatically; write them
  with natural indentation for readability
- For direct def parsing in tests, use `TestPackage.parse_def(DefCls, source)`;
  use `parse_any_def(...)` only when the exact def subclass is intentionally variable
- If a test expects a structured report exception and the report output is just noise,
  use `self.suppress_report_output()` around the assertion

Examples and sandbox
- Use `codebase/sandbox` for quick manual checks
- Keep sample `.ax` files minimal and descriptive

When working in packages/protobase
- Follow `packages/protobase/AGENTS.md`
- Run commands from packages/protobase

When unsure
- Inspect nearby modules for patterns before introducing new ones
- Ask for clarification on public API changes or cross-package refactors
