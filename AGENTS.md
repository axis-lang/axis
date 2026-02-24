# AGENTS.md
# Guidance for agentic coding in this repo (Axis language)

## Quick context
- Axis is a language implementation in Python with a multi-stage pipeline.
- Core layers: syn (AST/grammar) -> dom (canonical data model) -> sem (semantics).
- Immutable, hash-consed structures are provided by protobase.Record.

## Essential commands
# List just commands
just --list

# Run the main module
just launch
# (equivalent) poetry run python -m axis

# Run all tests (unittest)
just test
# (equivalent) poetry run python -m unittest discover -s tests

# Run a single test file
poetry run python -m unittest tests/test_eval.py

# Run a single test case/method
poetry run python -m unittest tests.test_eval.EvalTest.test_eval_literal

# Regenerate ANTLR parser after grammar changes
just gen-parser

## Style and architecture conventions
- Prefer immutable data models via protobase.Record (frozen=True, consed=True).
- Avoid mutation of Record instances; use mutate() when needed.
- dom is the canonical data model; sem should gradually converge to dom types.
- dom.Ref API uses root/child/with_args; avoid old segments/parent properties.
- dom.Err is used for non-fatal resolution errors in the pipeline.
- Scope resolution is handled by sem.ScopeBinding (hierarchical, strict).

## Imports and module layout
- Use absolute imports from axis (e.g., from axis import dom, syn, expr).
- Keep imports grouped: stdlib, third-party, internal.
- dom.Tuple is the canonical tuple/shape container (index + values).

## Types and naming
- Use Type for type descriptors; Var.Type for type variables.
- Use Dom -> Val -> Const hierarchy for literal values.
- Use Ref.Type and Ref.Data nested classes for reference structure.
- Use dom.Tuple[str, T] with optional keys represented by None in index.

## Error handling and diagnostics
- For syntax/semantic diagnostics, prefer axis.log (diagnostic + labels).
- In dom/sem resolution flows, use dom.Err to keep the pipeline running.
- Keep errors strict in ScopeBinding lookup (return Err, do not throw).

## Tests
- Tests are unittest-based and live under tests/.
- Use poetry run python -m unittest to run tests.
- Do not introduce pytest unless requested.

## Build/lint/docs
- No lint tool is configured; do not assume black/ruff.
- Docs are built with Sphinx: just docs (poetry run sphinx-build docs dist/docs).

## Grammar and parser
- Grammar is in src/axis/syn/grammar/Axis.g4.
- Regenerate parser with: just gen-parser.

## Copilot instructions (summary)
Refer to .github/copilot-instructions.md for full details.
Key points:
- All data models inherit from protobase.Record (immutable, consed).
- Multi-stage pipeline: src -> syn -> sem -> (future codegen).
- AST nodes auto-bind to grammar rules via naming conventions.
- Use singledispatch for extensible operations.
- Use ContentTable/entries for symbol tables when relevant.
- Grammar changes require regeneration.
- Prefer existing import patterns; beware dependency order.

## Current dom/sem convergence notes
- sem now uses dom.Tuple[str, syn.Expr] in place of TupleShape.
- RefShape still exists for semantic indexing (segments + params_exprs).
- Plan is to move RefShape logic toward dom patterns/refs over time.

## Practical guidelines for changes
- Read the relevant layer (syn/dom/sem) before editing.
- Keep public API changes localized and update tests/docs.
- Use apply_patch for focused edits.
- Avoid introducing reflection (to_val/from_val) unless requested.

## Single test execution examples
# Run full suite
poetry run python -m unittest discover -s tests

# Run a specific module
poetry run python -m unittest tests.test_syn

# Run a specific test
poetry run python -m unittest tests.test_syn.DatabaseSmokeTest.test_database_build

## Useful paths
- dom: src/axis/dom/core.py
- sem: src/axis/sem/database.py, src/axis/sem/entity.py
- syn: src/axis/syn/
- expr: src/axis/expr/
- items: src/axis/items/

## Notes on scope resolution
- ScopeBinding lookup uses sym.at to target a named scope (nearest match).
- Unresolved names should return dom.Err, not raise.

## Formatting
- Keep code in ASCII where possible.
- Follow existing spacing and naming conventions in files you touch.
