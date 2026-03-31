# Layer 3 — Domain Types

Domain types are the concrete `Type` constructors you work with day-to-day. They form an algebraic type language for describing the shape of data.

---

## Type taxonomy

```
Type
├── TupleLikeType          positional collections
│   ├── VaryingType        fixed heterogeneous tuple  (int, str, bool)
│   ├── UniformType        unbounded homogeneous list [int]
│   └── IndexedType        named-field record         {x: int, y: int}
├── UnionType              disjunction                int | str
├── Spec                   nominal / parametric       std.types.List[int]
└── Qual                   qualified type             List int
```

---

## `Spread[V]`

`Spread` is not itself a type constructor — it is a *splice sentinel* used during type construction.

```python
pm.Spread(values=(int_t, str_t))
```

When a `TupleLikeType` calls `splice()`, any `Spread` in its `values` tuple is flattened in-place. This mirrors Python's `*args` unpacking.

```python
spread = pm.Spread((int_t, str_t))
composed = pm.VaryingType((pm.Spec.of("test.a"), spread, pm.Spec.of("test.b")))
print(composed.splice())
# VaryingType(test.a, std.types.Integer, str, test.b)
```

---

## `VaryingType`

Heterogeneous fixed-arity tuple. Think `tuple[int, str, bool]`.

```python
triple = pm.VaryingType.of(int_t, str_t, bool_t)
print(triple.arity)          # 3
print(triple.item_at(1))     # Item(offset=1, key=None, value=str_t)
```

`VaryingType.Empty` is the singleton zero-arity tuple.

**Factory methods:**

| Method | Input | Output |
|---|---|---|
| `VaryingType.of(*types)` | `pm.Type` values | `VaryingType` |
| `VaryingType.new(*carriers, **named)` | `Carrier` values | `pm.Tuple` (a carrier) |

---

## `UniformType`

Homogeneous collection of unbounded length. Think `list[T]`.

```python
int_list = pm.UniformType(int_t)
print(int_list.arity)          # None  (unbounded)
print(int_list.item_at(7))     # Item(7, None, int_t)   — same type at every offset

# unique=True → used for indexed collections (set-like)
int_set = pm.UniformType(int_t, unique=True)
```

---

## `UnionType`

Disjunction of types. Think `int | str`.

```python
u = pm.UnionType.of(int_t, str_t)
print(u.variants)    # frozenset({int_t, str_t})
```

`UnionType.of` automatically flattens nested unions:

```python
u1 = pm.UnionType.of(int_t, str_t)
u2 = pm.UnionType.of(u1, bool_t)
print(u2.variants)   # frozenset({int_t, str_t, bool_t})
```

If only one variant remains after flattening, `of` returns that single type directly — no wrapper created.

`UnionType` is a **leaf in traversal**: carrier dispatch happens at runtime, not statically.

---

## `IndexedType`

A `VaryingType` augmented with an `Index` — a key-to-offset mapping. This is how named fields (records / structs) are represented.

```python
rec = pm.IndexedType.of(x=int_t, y=str_t)
print(rec.item(pm.Id("x")))    # Item(0, 'x', int_t)
print(rec.item_at(1))          # Item(1, 'y', str_t)
```

You can mix positional and named fields:

```python
mixed = pm.IndexedType.of(int_t, str_t, label=bool_t)
# offset 0 → positional int
# offset 1 → positional str
# offset 2 → named "label" bool
```

---

## `Spec`

Nominal (anchored) types — the main way to reference library-defined or user-defined types. A `Spec` has:

- `anchor: str` — a dotted qualified name, e.g. `"std.types.List"`.
- `args: pm.Tuple` — type arguments (the parameters of the specialisation).

```python
list_of_int = pm.Spec.of("std.types.List", int_t)
print(list_of_int.anchor)         # "std.types.List"
print(list_of_int.args.content)   # (int_t,)
```

`Spec` delegates `arity`, `item_at`, and `item` to the schema returned by the active `Host`. If no schema is registered, `arity = 0` and the spec behaves as a leaf.

**Creating specs:**

```python
pm.Spec.of("test.pair", int_t, str_t)           # positional args
pm.Spec.of("test.point", x=int_t, y=int_t)      # named args
```

---

## `Qual`

A qualified type wraps an underlying type with one or more qualifier specs. Think `list[int]` as `Qual(int_t, List)` or `dict[str, int]` as `Qual(int_t, Map(str_t))`.

```python
list_int = pm.Qual.of(int_t, pm.Spec.of("std.qualifiers.List"))
print(list_int.underlying)     # std.types.Integer
print(list_int.qualifiers)     # (std.qualifiers.List,)
```

`Qual.of` automatically flattens nested qualifiers:

```python
q1 = pm.Qual.of(int_t, pm.Spec.of("std.qualifiers.List"))
q2 = pm.Qual.of(q1,    pm.Spec.of("std.qualifiers.Optional"))
# q2.underlying = int_t
# q2.qualifiers = (std.qualifiers.List, std.qualifiers.Optional)
```

`Qual` delegates `arity`, `item_at`, and `item` to its `underlying` type.

---

## Putting it together — Python type projection

`NativeHost.project_type` converts Python annotations into the corresponding `pm.Type`:

| Python annotation | `pm.Type` |
|---|---|
| `int` | `Spec("std.types.Integer")` |
| `str` | `Spec("std.types.Text")` |
| `list[int]` | `Qual(int_t, Spec("std.qualifiers.List"))` |
| `dict[str, int]` | `Qual(int_t, Spec("std.qualifiers.Map", str_t))` |
| `tuple[int, str]` | `Spec("std.types.Tuple", int_t, str_t)` |
| `int \| str` | `UnionType({int_t, str_t})` |
| `TypeVar("T")` | `NativeVar(ctx, "T")` |

---

## API reference

::: pm.Spread

::: pm.TupleLikeType

::: pm.VaryingType

::: pm.UniformType

::: pm.UnionType

::: pm.IndexedType

::: pm.Spec

::: pm.Qual
