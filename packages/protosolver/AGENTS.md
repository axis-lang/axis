# AGENTS

This file guides agentic coding agents working in /home/jdluque/Workspace/axis.
Primary scope for this package: packages/protosolver.

Repository layout
- packages/protosolver: Python package (Poetry-based)
- packages/protosolver/src/protosolver: runtime code
- packages/protosolver/tests: unittest suite

Environment expectations
- Python 3.13+ (see packages/protosolver/pyproject.toml)
- Poetry for virtualenv and dependency management
- Use `poetry run` for commands to ensure correct env

Working directory
- Run commands from packages/protosolver unless explicitly noted
- Paths in commands below are relative to packages/protosolver

Build/lint/test commands
- List tasks: `just help`
- Tests (all): `just test`
- Tests (all, direct): `poetry run python -m unittest discover -s tests`
- Type checks: `just pyright`
- Type checks (direct): `poetry run pyright`

Single-test commands (unittest)
- Single file: `poetry run python -m unittest tests.test_solver`
- Single class: `poetry run python -m unittest tests.test_solver.TestSolver`
- Single test: `poetry run python -m unittest tests.test_solver.TestSolver.test_basic`

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
- Keep relative imports within `protosolver` where possible

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

Naming conventions
- Classes: CamelCase
- Functions/variables: snake_case
- Constants: UPPER_CASE
- Private helpers: leading underscore

Error handling
- Use TypeError for misuse of API or invalid types
- Use ValueError for invalid values or state
- Preserve context when re-raising: `raise ... from exc`
- Provide clear, user-facing error messages

Testing guidelines
- Tests use unittest; keep them deterministic
- Name new tests `test_*.py` to be discovered by unittest
- No `__init__.py` needed in `tests/`

When unsure
- Inspect existing modules in `src/protosolver` for patterns
- Prefer incremental changes that preserve current behavior
- Ask for clarification on public API changes
