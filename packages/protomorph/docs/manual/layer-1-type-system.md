# Layer 1 — Type System

A `Type` is a *descriptor*: it describes the shape of values, tells carriers how to navigate them, and produces new carriers on demand.

---

## The descriptor protocol

`Type[T]` is abstract and sits at the root of the type hierarchy. Its interface has two responsibilities:

### 1. Structure navigation

```
arity       → int | None        number of children (None = unbounded)
item_at(i)  → Item              child by offset
item(id)    → Item              child by name
items()     → Iterator[Item]    all children
```

`Item` is a `NamedTuple(offset, key, value)`. The `key` may be `None` for positional-only fields.

### 2. Carrier production

```python
type.make(data) -> Carrier
```

Looks up the carrier factory registered for this `Type` subclass (via `carrier_factory_for`) and wraps `data`.

```python
import pm

int_type = pm.Spec.of("std.types.Integer")
carrier  = int_type.make(42)
print(carrier.content)   # 42
```

### Metatype bootstrap

`metatype()` returns the type *of* this type — enabling meta-level reflection:

```python
pair_type = pm.VaryingType.of(int_type, int_type)
print(pair_type.metatype())   # VaryingType(metatype(int), metatype(int))
```

Every concrete `Type` subclass must implement `metatype()`. The system bootstraps itself because `Spec.metatype()` returns a `Spec`, not a higher-order type.

---

## Placeholders and variables

`Placeholder` is a special `Type` that acts as a stand-in for unknown values anywhere in a type tree.

```
Type
└── Placeholder   (abstract — behaves as leaf, can appear as type or data)
    └── Var       (abstract — a named logic variable)
        └── SimpleVar(ctx, id)   (the default concrete variable)
```

Key properties of `Placeholder`:

- `metatype()` returns `self` — a placeholder is its own metatype.
- It is always a leaf in traversal: the unifier captures it rather than descending into it.
- It can appear both as a `Type` (unknown type position) and as a value (unknown data).

### Creating variables

```python
from pm import placeholder, placeholder_name, placeholder_label

x = placeholder("X")
print(placeholder_name(x))    # "X"
print(placeholder_label(x))   # "X"
```

`placeholder(id, context=None)` is the canonical factory. It returns a `SimpleVar` with an optional `context` object used to namespace freshened copies.

### Variable identity

Because `SimpleVar` is hash-consed, two calls with the same `ctx` and `id` return the exact same object. Freshening during rule application explicitly creates a *new* context to break this identity:

```python
from pm import placeholder

x1 = placeholder("X")
x2 = placeholder("X")
assert x1 is x2   # same ctx=None, same id

# Different context → different variable
from pm.reasoning import RuleAppCtx
ctx_a = RuleAppCtx(rule=..., application_id=1)
ctx_b = RuleAppCtx(rule=..., application_id=2)
# NativeVar(ctx_a, "X") is not NativeVar(ctx_b, "X")
```

---

## `Field` alias

`Field` is an alias for `Item` re-exported from `pm`. It is used in signatures when the emphasis is on named struct fields rather than generic positional items.

---

## Summary

| Symbol | Role |
|---|---|
| `Type[T]` | Abstract descriptor — structure + carrier factory |
| `Placeholder` | Stand-in for unknown type or value; leaf in traversal |
| `Var` | Named logic variable |
| `SimpleVar(ctx, id)` | Default concrete variable |
| `var(id)` | Factory for `SimpleVar` |
| `placeholder_name/context/slot/label` | Attribute extractors with safe fallbacks |
| `Field` / `Item` | `NamedTuple(offset, key, value)` — one child descriptor |

---

## API reference

- [`protomorph.Type`](../reference/pm.md#protomorph.Type)
- [`protomorph.Placeholder`](../reference/pm.md#protomorph.Placeholder)
- [`protomorph.Var`](../reference/pm.md#protomorph.Var)
- [`protomorph.SimpleVar`](../reference/pm.md#protomorph.SimpleVar)
- [`protomorph.placeholder_name`](../reference/pm.md#protomorph.placeholder_name)
- [`protomorph.placeholder_context`](../reference/pm.md#protomorph.placeholder_context)
- [`protomorph.placeholder_slot`](../reference/pm.md#protomorph.placeholder_slot)
- [`protomorph.placeholder_label`](../reference/pm.md#protomorph.placeholder_label)
