# AGENTS

This file guides agentic coding agents working in /home/jdluque/Workspace/axis.
Primary scope: repository root (axis). For protobase-specific rules see packages/protobase/AGENTS.md.

Repository layout
- src/axis: Axis runtime and language implementation
- tests: root unittest suite for axis
- packages/protobase: shared primitives package (own tests/examples/docs)
- codebase: Axis source packages used by tests and demos
- docs: design notes and specs
- scripts: ad-hoc tools

Environment expectations
- Python 3.13 (see .python-version, pyproject.toml)
- Poetry for virtualenv and dependency management
- Use `poetry run` for commands to ensure correct env
- Default working directory is repo root unless noted
- For protobase commands, run from packages/protobase

Build/lint/test commands (root)
- List tasks: `just help`
- Run Axis module: `just launch -- --help`
- Run Axis on std.core: `just launch -- --package codebase/std.core`
- Tests (all): `just test`
- Tests (all, include packages): `just test-all`
- Tests (direct): `poetry run python -m unittest discover -s tests`
- Single file: `poetry run python -m unittest tests.test_eval`
- Single class: `poetry run python -m unittest tests.test_eval.EvalTest`
- Single test: `poetry run python -m unittest tests.test_eval.EvalTest.test_eval_additive`
- Type checks: `poetry run pyright`
- Docs build: `just docs`
- Regenerate parser: `just gen-parser`
- Watch mode: `just watch` (requires watchexec)

Build/lint/test commands (protobase)
- Working directory: packages/protobase
- List tasks: `just help`
- Tests (all): `just test`
- Tests (direct): `poetry run python -m unittest discover -s tests`
- Single file: `poetry run python -m unittest tests.test_flux`
- Single class: `poetry run python -m unittest tests.test_flux.FluxMethodTest`
- Single test: `poetry run python -m unittest tests.test_flux.FluxMethodTest.test_cache_hits_for_same_args`
- Type checks: `just pyright`
- Run example: `just run <example>`
- Run example (direct): `poetry run python "examples/<example>.py"`
- See packages/protobase/AGENTS.md for protobase-specific rules

Code style: general
- Follow existing patterns; there is no formatter config in this repo
- Keep code readable over cleverness; favor small explicit functions
- Avoid introducing new dependencies unless necessary
- Keep public APIs minimal and documented
- Prefer persistent, immutable data structures (tuple, frozenset, frozendict)
- Use protobase Consed/Inmutable classes for semantic data models
- Use `mutate(obj, ...)` for updates instead of attribute mutation
- Avoid side effects inside pure/consed objects
- Avoid large refactors unless required by the task

Imports
- Order groups: standard library, third-party, local modules
- Separate import groups with a blank line
- Prefer explicit imports; wildcard only in __init__.py for re-exports
- Prefer absolute imports (axis.*, protobase.*) for clarity
- Use relative imports only for tight, local coupling
- Use TYPE_CHECKING blocks for type-only imports

Formatting
- Use 4-space indentation
- Keep line length reasonable; wrap complex expressions for clarity
- Use f-strings for formatting
- Keep docstrings short and action-oriented
- Avoid trailing whitespace
- Keep inline comments minimal; add only for non-obvious logic
- Preserve existing spacing style in a file
- Match existing language in comments/docstrings (Spanish or English)

Typing and annotations
- Use type annotations for public functions, methods, and class attributes
- The codebase uses modern typing (PEP 695 type params, `type Alias`)
- Prefer `T | None` over `Optional[T]` in runtime code
- Use `Self` for fluent APIs and builders
- Keep runtime-heavy typing out of hot paths
- Prefer narrow, explicit union types for AST/data structures
- Use `cast` only when unavoidable and explain with a short comment
- Respect pyright excludes (generated grammar in src/axis/syn/grammar)

Naming conventions
- Classes: CamelCase
- Functions/variables: snake_case
- Constants: UPPER_CASE
- Type aliases: PascalCase or descriptive alias names (e.g., EntitiesByRef)
- Private helpers: leading underscore
- Keep domain suffixes consistent: Type, Ref, Expr, Item, Scope, Realm

Error handling and diagnostics
- Use TypeError for misuse of API or invalid types
- Use ValueError for invalid values or state
- Preserve context when re-raising: `raise ... from exc`
- Prefer `src.error(...)` to build diagnostics with labels and notes
- Use `diag.throw()` for fatal errors; `diag.emit()` for non-fatal
- Represent error values with `dom.Err(diagnostic=diag)`
- Attach spans using `node.as_label(...)` or `src.Label(...)` when available
- Avoid broad exception catches; narrow to expected errors

Immutability and caching
- Consed/Inmutable objects should be treated as immutable after build
- Use `mutate` or `.with_attr(...)` helpers for modifications
- Prefer `frozendict` over dict for stored maps in data models
- Use `cached_property` from protobase when caching object state
- Keep `__hash__` and `__eq__` cheap; avoid heavy work there

Performance considerations
- Hash-consing improves sharing but adds hashing overhead
- Avoid heavy work in `__hash__` or `__eq__` beyond structural fields
- Cache expensive derived values via `cached_property`
- Keep query functions pure and deterministic for cache safety
- Avoid rich rendering or printing in hot-path logic

Axis-specific notes
- AST lives in `src/axis/syn` and `src/axis/expr`
- Canonical data model lives in `src/axis/dom`
- Semantic database and scopes live in `src/axis/sem`
- Use `src.Source`/`SourceDir` helpers for file/dir access
- Grammar and generated parser live in `src/axis/syn/grammar`
- Do not hand-edit generated grammar outputs; use `just gen-parser`
- Tests rely on `codebase/std.core`; run commands from repo root

Testing guidelines
- Tests use unittest; follow patterns in tests/test_*.py
- Keep tests deterministic; avoid timing-sensitive asserts
- Name new tests `test_*.py` so unittest discovery picks them up
- Prefer small, focused tests that isolate a single behavior

Docs and examples
- Keep README and docs/ in sync when behavior changes
- Add or update examples for new user-facing features
- For protobase examples, keep them runnable via `just run <example>`

Development tips
- Prefer `just` tasks when available; they set up the expected environment
- Use `poetry run` for ad-hoc scripts (e.g., `poetry run python scripts.py`)
- The debug runner lives in `src/axis/__main__.py`
- `python -m axis --repl` uses IPython if installed
- Use `python -m axis --package <path>` to point at other codebase dirs

When unsure
- Inspect existing modules under `src/axis` for patterns
- Prefer incremental changes that preserve current behavior
- If changing public APIs, update docs and add tests
- Check packages/protobase/AGENTS.md for package-specific rules
