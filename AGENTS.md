# AGENTS

This file guides agentic coding agents working in /home/jdluque/Workspace/axis.
Primary scope for this package: packages/protobase.

Repository layout
- packages/protobase: Python package (Poetry-based)
- packages/protobase/src/protobase: runtime code
- packages/protobase/tests: unittest suite
- packages/protobase/examples: runnable examples
- packages/protobase/docs: extended documentation

Tooling rules discovery
- No Cursor rules found (.cursor/rules/ or .cursorrules).
- No Copilot instructions found (.github/copilot-instructions.md).

Environment expectations
- Python 3.13+ (see packages/protobase/pyproject.toml)
- Poetry for virtualenv and dependency management
- Use `poetry run` for commands to ensure correct env

Working directory
- Run commands from packages/protobase unless explicitly noted
- Paths in commands below are relative to packages/protobase

Build/lint/test commands
- List tasks: `just help`
- Tests (all): `just test`
- Tests (all, direct): `poetry run python -m unittest discover -s tests`
- Type checks: `just pyright`
- Type checks (direct): `poetry run pyright`
- Run example: `just run <example>`
- Run example (direct): `poetry run python "examples/<example>.py"`

Single-test commands (unittest)
- Single file: `poetry run python -m unittest tests.test_flux`
- Single class: `poetry run python -m unittest tests.test_flux.FluxMethodTest`
- Single test: `poetry run python -m unittest tests.test_flux.FluxMethodTest.test_cache_hits_for_same_args`

Optional/stress tests
- tests/optional_flux_stress.py
- tests/optional_gc_stress.py
- Run explicitly: `poetry run python -m unittest tests.optional_flux_stress`

Code style: general
- Follow existing patterns; there is no formatter config in this repo
- Keep code readable over cleverness
- Prefer small, explicit functions
- Avoid introducing new dependencies unless necessary
- Keep public API surface minimal and documented

Imports
- Order groups: standard library, third-party, local modules
- Separate groups with a blank line
- Prefer explicit imports; wildcard only in `__init__.py` for re-exports
- Keep relative imports within `protobase` where possible

Formatting
- Use 4-space indentation
- Keep line length reasonable; wrap complex expressions for clarity
- Use f-strings for formatting
- Keep docstrings short and action-oriented
- Avoid trailing whitespace

Typing and annotations
- Use type annotations for public functions, methods, and class attributes
- The codebase uses modern typing (PEP 695 generics, Self, ParamSpec)
- Use TYPE_CHECKING blocks for type-only helpers and overloads
- Prefer `type | None` over `Optional[type]` in runtime code
- Avoid runtime-heavy typing constructs in hot paths

Naming conventions
- Classes: CamelCase
- Functions/variables: snake_case
- Constants: UPPER_CASE
- Private helpers: leading underscore
- Descriptors and metaclasses follow established naming (Type, Record, Inmutable)

Error handling
- Use TypeError for misuse of API or invalid types
- Use ValueError for invalid values or state
- Preserve context when re-raising: `raise ... from exc`
- Provide clear, user-facing error messages
- For multiple validation errors, consider ExceptionGroup (see inmutable checks)

Immutability and records
- Inmutable objects must not allow attribute mutation after construction
- Use `mutate(record, **attrs)` for persistent updates
- Defaults are deep-copied in Record init; do not rely on shared mutable defaults
- If adding new Record-like behavior, use derived methods to keep semantics consistent

Slots and weakrefs
- `flux.method` and `flux.property` require weakrefable instances
- Ensure `__weakref__` is in `__slots__` for non-Record classes
- Record/Inmutable already add `__weakref__` automatically

Flux runtime constraints
- Queries must return concrete values; no generators, coroutines, or awaitables
- Args/kwargs must be hashable (cache key)
- Do not mutate `flux.input` values during a query
- Use invalidate/invalidate_for/invalidate_all to force recomputation

Caching helpers
- Prefer `protobase.cached_property` or `slot_cached_property`
- Avoid `functools.cached_property` (not supported in protobase Object classes)

Performance considerations
- Hash-consing improves sharing but adds hashing overhead
- Avoid heavy work in `__hash__` or `__eq__` beyond structural fields
- Keep query functions pure and deterministic for cache safety

Testing guidelines
- Tests use unittest; follow patterns in tests/test_flux.py
- Keep tests deterministic; avoid timing-sensitive asserts
- Name new tests `test_*.py` to be discovered by unittest

Docs and examples
- Keep README and docs/ consistent when behavior changes
- Add or update examples for new user-facing features
- Keep examples small and runnable from justfile

When unsure
- Inspect existing modules in `src/protobase` for patterns
- Prefer incremental changes that preserve current behavior
- Ask for clarification on public API changes
