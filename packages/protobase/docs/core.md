# Core class system

This section describes the core class system that powers Protobase records.
The key components are `Type`, `Object`, and `Record`.

## Object model

- `Type` is the metaclass that builds classes and records metadata.
- `Object` is the base class for all protobase types.
- `Record` extends `Object` with derived methods and record semantics.

### Attributes and slots

Attributes are defined through type annotations. During class construction:

- Attributes are collected from `__annotations__`.
- `__slots__` is generated to include all attribute names.
- `__weakref__` is automatically added if missing.

This keeps instances compact and enforces a predictable attribute set.

## Initialization and defaults

`Record` has a derived `__init__` that follows these rules:

- Positional attributes are passed explicitly and assigned directly.
- Nominal attributes (those with defaults) can be omitted.
- When omitted, a *deep copy* of the default value is used.

This avoids shared mutable defaults:

```python
class Bag(Record):
    items: list[int] = []

first = Bag()
second = Bag()
first.items.append(1)
assert second.items == []
```

If you want to reuse a shared instance, pass it explicitly during construction.

### Missing sentinel for LSP ordering

Static checkers such as Pyright enforce dataclass-style ordering: fields without
defaults cannot appear after fields with defaults. Protobase allows that order at
runtime, so you can use a sentinel to keep the field required while satisfying
the checker:

```python
from protobase import Object, _


class Config(Object):
    x: int = 5
    y: int = _
```

`_` is an alias of `Missing` typed as `Any`. During class construction, values
equal to `Missing` are treated as "no default", so `y` remains required in the
derived `__init__`.

## Mutation helper

`mutate(record, **attrs)` creates a new record by copying the current state and
overriding the provided attributes. This is convenient for persistent-style
updates.

## Related modules

- `src/protobase/object.py`
- `src/protobase/record.py`
