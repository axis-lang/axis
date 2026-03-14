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
- Use TYPE_CHECKING for type-only imports and overloads

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

Examples and sandbox
- Use `codebase/sandbox` for quick manual checks
- Keep sample `.ax` files minimal and descriptive

When working in packages/protobase
- Follow `packages/protobase/AGENTS.md`
- Run commands from packages/protobase

When unsure
- Inspect nearby modules for patterns before introducing new ones
- Ask for clarification on public API changes or cross-package refactors
