# Layer 6 — Native Host

`NativeHost` is the default `Host` implementation. It bridges Python's own type annotation system (`typing`, `TypeVar`, standard collections) into the Protomorph type algebra.

It is a useful built-in implementation, not the semantic source of truth for all
hosts. Axis is expected to provide its own semantic implementation during the
clean-cut migration. See [PM / Axis Clean-Cut Roadmap](pm-axis-roadmap.md).

Under the roadmap, `NativeHost` is expected to converge toward `NativeRealm`,
with native/testing overlays used to inject rules, facts, and impls while
reusing native semantics.

---

## How it works

`NativeHost` maintains three registries (all lazily cached via `@flux.property`):

| Registry | Key | Value | Purpose |
|---|---|---|---|
| `all_builtins` | — | `frozenset[type[Builtin]]` | All registered `Builtin` subclasses |
| `native_specs` | `type` | `pm.Spec` | Scalar Python types → spec |
| `python_transforms` | `type` (origin) | `Callable` | Generic origins → type constructors |

---

## Type projection — `project_type`

`NativeHost.project_type(annotation)` converts any Python annotation into a `pm.Type`:

```python
from pm import _project_type

_project_type(int)              # Spec("std.types.Integer")
_project_type(str)              # Spec("std.types.Text")
_project_type(list[int])        # Qual(Integer, List)
_project_type(dict[str, int])   # Qual(Integer, Map(Text))
_project_type(int | str)        # UnionType({Integer, Text})
_project_type(tuple[int, str])  # VaryingType(Integer, Text)
```

Projection is recursive and handles:

- `Union` / PEP 604 `X | Y`
- `Unpack[T]` → project inner type
- `tuple[T, ...]` → `UniformType(T)`
- `tuple[T1, T2, ...]` → `VaryingType(T1, T2, …)`
- `TypeVar` / `TypeVarTuple` → `NativeVar`
- Registered Python origins (dict, list, set, frozenset, tuple)
- `Builtin` subclasses → `Spec` via `spec_name`

---

## Schema specialisation

When a parametric `Spec` is looked up (e.g. `List[int]`), `NativeHost` computes the schema in three steps:

1. **Template** — call `schema_template_for(builtin_cls)` to get the generic schema with `NativeVar` placeholders.
2. **Mapping** — `_mapping_for_spec` pairs `cls.__type_params__` with the spec's `args`.
3. **Specialise** — `_specialize_schema` substitutes placeholders in the template.

```python
# class List[T](Builtin): item: T
# schema_template_for(List) → IndexedType(VaryingType(NativeVar("T")), Index("item"))
# spec = Spec("std.types.List", int_t)
# mapping = {NativeVar("T"): int_t}
# result → IndexedType(VaryingType(int_t), Index("item"))
```

Parameter count is validated before the mapping loop:

- No `TypeVarTuple`: `len(args) == len(cls_params)` (exact match).
- `TypeVarTuple` at position `i`: `len(args) >= i` (variadic tail).

---

## `NativeVar`

A specialised `Var` for TypeVar-originated variables. Carries a `ctx` (the spec anchor of the defining class) and an `id` (the TypeVar name).

```python
from pm.native import NativeVar

v = NativeVar("std.types.List", "T")
print(v.display_label())   # "T"
```

---

## Registering custom types

### Scalar mappings

Map a Python type directly to a `Spec`:

```python
from pm import register_native_spec, Spec

register_native_spec(MyScalar, Spec.of("myapp.MyScalar"))
```

### Generic transforms

Map a generic origin to a type constructor function:

```python
from pm import register_python_transform

def _my_transform(value_type: pm.Type) -> pm.Type:
    return pm.Qual.of(value_type, pm.Spec.of("myapp.MyContainer"))

register_python_transform(MyContainer, _my_transform)
```

After registration, `list[MyScalar]` will project correctly.

---

## `wrap`

`wrap` is the high-level entry point for turning Python values into carriers:

```python
from pm import wrap

wrap(42)           # LeafCarrier(Integer, 42)
wrap(int)          # carries the *type* Integer (meta-carrier)
wrap(list[int])    # carries Qual(Integer, List)
wrap(my_builtin)   # NativeObjectCarrier using projected type
```

It handles:
- Already-a-`Carrier` → returned as-is
- `pm.Type` → wrapped via metatype
- Python `type` → projected then meta-wrapped
- Generic annotation → projected then meta-wrapped
- `Builtin` instance → `descriptor.make(instance)`
- Anything else → `wrap(type(obj)).fetch().make(obj)`

---

## Bootstrap defaults

`_bootstrap_defaults()` is called once at module import time. It registers:

| Python type | `pm` equivalent |
|---|---|
| `int` | `Spec("std.types.Integer")` |
| `str` | `Spec("std.types.Text")` |
| `float` / `Decimal` | `Spec("std.types.Decimal")` |
| `bool` | `Spec("std.types.Boolean")` |
| `NoneType` | `Spec("std.types.Empty")` |
| `Id` | `Spec("std.types.Id")` |
| `dict` | `Qual(value, Map(key))` |
| `list` | `Qual(value, List)` |
| `set` | `Qual(value, Set)` |
| `frozenset` | `Qual(value, FrozenSet)` |
| `tuple` | structural tuple types (`VaryingType` / `UniformType`) |

---

## API reference

::: pm.NativeHost

::: pm.NativeVar

::: pm.wrap

::: pm.register_native_spec

::: pm.register_python_transform
