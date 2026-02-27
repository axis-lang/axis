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

## Mutation helper

`mutate(record, **attrs)` creates a new record by copying the current state and
overriding the provided attributes. This is convenient for persistent-style
updates.

## Related modules

- `src/protobase/object.py`
- `src/protobase/record.py`
