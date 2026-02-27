# FAQ

## Why are defaults deep-copied?

To avoid shared mutable defaults between instances. Each instance gets its own
copy, even for lists or dicts.

## How do I update a record immutably?

Use `mutate(record, **attrs)` to create a new record with updated fields.

## Why does `@flux.method` fail for global functions?

It requires an instance for dependency tracking. Use `@flux.functions` for
module-level functions instead.

## Why do I need `__weakref__` in `__slots__`?

Flux stores weak references for instance keys. If your class uses `__slots__`,
include `__weakref__`.

## How do I force recomputation?

Invalidate inputs or properties with `Input.invalidate(obj)` or
`Property.invalidate(obj)` and then access the value again (pull-based).

## Do flux queries support generators or async?

No. Flux rejects generators, coroutines, async generators, and other awaitables.
Materialize generator results or resolve async work outside the query.
