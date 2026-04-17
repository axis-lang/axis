# Layer 2 — Carriers

A **carrier** is a typed wrapper around a runtime value. Where a `Type` describes *shape*, a carrier holds *data* under that shape — and knows how to traverse, map, and reconstruct it.

---

## `Carrier[T]`

The abstract base for all carriers. Every carrier has two core attributes:

| Attribute | Type | Meaning |
|---|---|---|
| `descriptor` | `Type` | The type that describes this value |
| `content` | `T` | The raw runtime data |

### Tree navigation

Carriers form a tree. Navigation mirrors the descriptor's structure:

```python
carrier[0]            # child at offset 0 → Carrier
carrier[id]           # child by name → Carrier
len(carrier)          # arity (raises TypeError if unbounded)
iter(carrier)         # iterate children

carrier.is_leaf       # True if no children
carrier.content       # extract content
```

### Deep operations

```python
carrier.iter()               # depth-first pre-order iterator over every node
carrier.iter_leafs()         # filter of .iter(): only leaves
carrier.iter_branches()      # filter of .iter(): only containers (non-leaves)
carrier.deep_map(fn)         # map fn over every leaf, return rebuilt carrier
carrier.search(pred)         # first leaf matching predicate
carrier.subst(mapping)       # replace specific sub-carriers by identity
carrier.reconstruct(children)  # build a new carrier from modified children
```

`subst` uses object identity (`is`) to match keys, not equality. This matters because `Builtin` hash-consing makes `==` and `is` equivalent for most types, but substitution targets may be carriers, not raw values.

---

## Concrete carrier types

### `LeafCarrier[T]`

Wraps an atomic value with no children.

```python
from pm import LeafCarrier, Spec

leaf = LeafCarrier(Spec.of("std.types.Integer"), 42)
print(leaf.is_leaf)      # True
print(leaf.content)      # 42
```

### `NativeObjectCarrier[T]`

Wraps a `Builtin` object; children are the object's declared fields as resolved by the descriptor.

```python
# Given a Builtin with fields (x: int, y: int):
carrier = pm.wrap(some_point_instance)
carrier["x"].content    # value of field x
```

### `Tuple`

Wraps tuple data for `TupleLikeType` descriptors (`VaryingType`, `UniformType`, `IndexedType`).

```python
pair_type = pm.VaryingType.of(int_t, int_t)
t = pm.Tuple(pair_type, (pm.LeafCarrier(int_t, 1), pm.LeafCarrier(int_t, 2)))
print(t[0].content)   # 1
print(t.head.content) # 1
print(t.tail)         # Tuple with (2,)
```

`Tuple` also exposes:

- `splice()` — flatten nested `Spread` entries.
- `extends(other)` — concatenate two tuples.

### `Index`

An `Index` is a specialised `Tuple` that maps `Id` keys to offsets. It enforces uniqueness of keys and is used by `IndexedType` to support both positional and named field access.

```python
idx = pm.Index.of(pm.Id("x"), pm.Id("y"), None)
# None = positional-only slot
print(idx.offset_of(pm.Id("x")))  # 0
print(idx.key_at(2))              # None
```

---

## Carrier factories

`Type.make(data)` delegates to a registered carrier factory. The factory registry lives in `pm.__init__` and maps `Type` subclasses to factory callables:

| `Type` subclass | Factory |
|---|---|
| `Placeholder` | `LeafCarrier` |
| `UnionType` | `LeafCarrier` |
| `VaryingType` | `Tuple` |
| `UniformType` (non-unique) | `Tuple` |
| `UniformType` (unique) | `Index` |
| `IndexedType` | `Tuple` |
| `Spec` | `NativeObjectCarrier` or `LeafCarrier` depending on schema |
| `Qual` | delegates to `underlying.make(data)`, except `Result[...]` uses the specialized `Result` carrier |

---

## Example: deep traversal and substitution

```python
import pm

int_t = pm.Spec.of("std.types.Integer")
x     = pm.placeholder("X")

# A pair where the second element is a variable
pair = pm.VaryingType.of(int_t, x).make((pm.LeafCarrier(int_t, 1), pm.LeafCarrier(x, x)))

leaves = list(pair.iter_leafs())
print([l.content for l in leaves])   # [1, SimpleVar(None, 'X')]

# Substitute X → 99
replacement = pm.LeafCarrier(int_t, 99)
subst_map   = {leaves[1]: replacement}
new_pair    = pair.subst(subst_map)
print([c.content for c in new_pair.iter_leafs()])  # [1, 99]
```

---

## API reference

- [`protomorph.LeafCarrier`](../reference/pm.md#protomorph.LeafCarrier)
- [`protomorph.NativeObjectCarrier`](../reference/pm.md#protomorph.NativeObjectCarrier)
- [`protomorph.Tuple`](../reference/pm.md#protomorph.Tuple)
- [`protomorph.Index`](../reference/pm.md#protomorph.Index)
