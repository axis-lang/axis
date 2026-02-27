# Flux queries and invalidation

Flux provides dependency-tracked computed values. It memoizes results, records
dependencies during evaluation, and uses pull-based invalidation to determine
when recomputation is required.

## Decorators

- `@flux.property` - computed attribute on instances.
- `@flux.method` - computed method on instances.
- `@flux.functions` - computed global function (no instance).
- `@flux.input` - mutable input stored in the runtime (supports assignment).

## Inputs

Inputs are the only mutable source in the system. They are stored by the
runtime, not on the object, and can be set by assignment:

```python
class Config:
    __slots__ = ("__weakref__",)

    @flux.input
    def value(self) -> int:
        raise NotImplementedError

cfg = Config()
cfg.value = 3
```

You can also invalidate an input without changing the value:

```python
Config.value.invalidate(cfg)
```

## Invalidation model

Flux uses *pull-based* invalidation:

- Mutations (input set/invalidate) advance the global revision.
- Queries are not recomputed immediately.
- On access, the runtime checks whether dependencies changed since the last
  verification and recomputes only if needed.

This keeps invalidation cheap and recomputation proportional to what is used.

## Exceptions

If a query raises an exception:

- The exception propagates to the caller.
- No memo is written or updated.
- The previous memo (if any) remains unchanged and will be revalidated on the
  next access.

## Collecting emitted values

During a query, you can `flux.emit(obj)` and later collect:

- `flux.collect(query, ...)` - run one query and collect emitted items.
- `flux.collect_all(query)` - collect for all cached keys (forces fetches).

## Iteration helper

`flux.iter` provides stack-safe traversal for linked lists or DAGs:

```python
for node in flux.iter(root, next=lambda n: n.next):
    ...

for node in flux.iter(root, children=lambda n: n.children):
    ...
```

## Unsupported return types

Flux queries must return concrete, fully-evaluated values. The runtime rejects
the following return types:

- Generators (including generator functions and generator objects)
- Coroutines / awaitables
- Async generators

These return types cannot be memoized safely because evaluation happens outside
of the query context. If you need them, materialize the result (e.g. `list(...)`)
or resolve async work outside the query and pass data in via `@flux.input`.

## Common gotchas

- `@flux.method` requires an instance; use `@flux.functions` for globals.
- Instance methods require `__weakref__` in `__slots__`.
- Do not mutate inputs during query execution; this raises an error.

## Related modules

- `src/protobase/flux.py`
