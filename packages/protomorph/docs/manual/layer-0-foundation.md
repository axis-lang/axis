# Layer 0 — Foundation

The foundation layer defines the three primitives that everything else is built on: two identifier newtype aliases and the base class for all registered types.

---

## `Id` and `Anchor`

```python
Id     = NewType("Id",     str)   # field / key name
Anchor = NewType("Anchor", str)   # qualified dotted name, e.g. "std.types.Integer"
```

Both are thin `NewType` wrappers around `str`. They carry no runtime overhead but make intent explicit in type signatures.

| Alias | Used for |
|---|---|
| `Id` | Field names in `Index`, keys in `IndexedType` |
| `Anchor` | Nominal type identifiers in `Spec` |

```python
from protomorph import Id, Anchor

field = Id("name")
spec_name = Anchor("std.types.Integer")
```

---

## `Builtin`

`Builtin` is the abstract base class for every concrete entity in Protomorph — types, carriers, rules, answers, and more.

It extends `protobase.Consed`, which provides:

- **Hash-consing** — equal instances are the same object (structural identity = physical identity).
- **Immutability** — instances are frozen on construction.
- **Declarative fields** — subclasses declare attributes as class-level annotations; `Consed` generates `__init__`, `__eq__`, and `__hash__` automatically.

```python
from protomorph import Builtin, Spec

# Two calls with the same arguments return the *same* object
a = Spec.of("std.types.Integer")
b = Spec.of("std.types.Integer")
assert a is b   # hash-consed
```

### Auto-registration

Every non-abstract `Builtin` subclass registers itself in `ALL_BUILTINS` the moment the class is defined:

```python
class Builtin(Consed, abstract=True):
    def __init_subclass__(cls, abstract: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)
        if not abstract:
            ALL_BUILTINS.add(cls)
            # also invalidates NativeHost cache
```

`NativeHost` uses `ALL_BUILTINS` to discover the full schema of every registered type at runtime.

### Repr delegation

`Builtin.__repr__` delegates to `display.repr_any`, the unified pretty-printer, so all types and carriers display consistently throughout the REPL and log output.

---

## Design note: Consed and structural equality

Hash-consing is unusual outside of functional languages; in Python it has important consequences:

- **Safe as dict keys and set members** without custom `__hash__`.
- **`is` implies `==`** — equality checks on types are pointer comparisons after the first construction.
- **Efficient memoization** in caches like `NativeHost`'s `@flux.method` results.

This is the reason `Type` instances can be used directly as mapping keys in `UnionFind` and `_mapping_for_spec`.

---

## API reference

- [`protomorph.Id`](../reference/pm.md#protomorph.Id)
- [`protomorph.Anchor`](../reference/pm.md#protomorph.Anchor)
- [`protomorph.Builtin`](../reference/pm.md#protomorph.Builtin)
