# Immutability

`Inmutable` is a `Record` that enforces deep immutability and structural hashing.
It is designed for stable, canonical data where identity follows structure.

## What is enforced

- Attribute assignment is blocked after construction.
- Attribute types are validated against a known set of immutable types.
- The structural hash is cached and stable across the object's lifetime.

## Type checks

`check_inmutable` validates attribute types. It accepts:

- Built-in immutable types (int, str, tuple, frozenset, etc.)
- A whitelist of known immutable classes
- Unions composed only of immutable types
- TypeVars whose bounds or constraints are immutable

You can extend the registry:

```python
from protobase.inmutable import register_inmutable

class MyValue:
    ...

register_inmutable(MyValue)
```

## Frozen assignment and descriptors

Regular attribute assignment is blocked, but descriptors with explicit setters
are still honored. This enables patterns like `@flux.input` while keeping the
record itself immutable.

## Hashing and copy behavior

- `Inmutable` computes a structural hash and caches it on first use.
- `__copy__` and `__deepcopy__` return `self` because the object is immutable.

## Related modules

- `src/protobase/inmutable.py`
