# API reference (compact)

This is a concise reference for Protobase's public API. See topic guides for
details and usage patterns.

## Core classes

- `Record` (`src/protobase/record.py`)
  - Base class for slot-based records.
  - Derived `__init__`, `__eq__`, `__repr__`, ordering.
  - `mutate(record, **attrs)` helper for persistent updates.

- `Inmutable` (`src/protobase/inmutable.py`)
  - Frozen records with structural hashing and immutability checks.

- `Consed` (`src/protobase/consed.py`)
  - Hash-consed immutable records (canonicalization).

## Flux

Decorators:

- `@flux.property`
- `@flux.method`
- `@flux.functions`
- `@flux.input`

Runtime helpers:

- `flux.invalidate(obj, prop_or_method)`
- `flux.collect(query, ...)`
- `flux.collect_all(query)`
- `flux.emit(item)`
- `flux.iter(root, next=..., children=...)`
- `flux.in_query()`

Return value constraints:

- Queries must return concrete values.
- Generators, coroutines/awaitables, and async generators are rejected.

Input helpers (descriptor methods):

- `Input.set(obj, value)`
- `Input.invalidate(obj)`
- `Input.invalidate_all()`

## Immutability utilities

- `check_inmutable(tp)`
- `register_inmutable(*types)`
- `is_inmutable(cls)`

## Notes

- Defaults are deep-copied on initialization.
- `@flux.method` requires an instance; use `@flux.functions` for globals.
- Instances used in queries must be weakrefable.
