# Layer 5 — Host Interface

The **host** is the extension point that makes Protomorph host-agnostic. It decouples the core type algebra from any specific runtime environment by providing a pluggable strategy for:

- schema lookup (what are the fields of a `Spec`?)
- custom carrier behaviour for opaque values
- logic operator evaluation

For the clean-cut Axis migration plan and the future division of responsibility
between `pm.Host`, `pm.reasoning.Database`, `pm.Realm`, `NativeRealm`, and the
reasoning engine, see [PM / Axis Clean-Cut Roadmap](pm-axis-roadmap.md).

This page documents the current `Host` interface. Under the roadmap, `Host` is
expected to become a temporary alias toward the canonical `Realm` abstraction.

---

## `Host`

`Host` is an abstract base class (extending `Builtin`) that defines the interface all host implementations must satisfy.

```python
class Host(Builtin):
    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None: ...
    def val_is_leaf(self, meta: pm.Type, data: Any) -> bool: ...
    def val_children(self, meta: pm.Type, data: Any) -> tuple[pm.Carrier, ...]: ...
    def val_reconstruct(self, meta: pm.Type, children: tuple[pm.Carrier, ...]) -> Any: ...
    def eval_logic_op(self, operator, *, goal, session) -> Any | None: ...
```

### `schema_for(spec)`

Returns the `TupleLikeType` that describes the fields of `spec`, or `None` if the spec is opaque (leaf). This drives `Spec.arity`, `Spec.item_at`, and `Spec.item`.

```python
schema = host.schema_for(pm.Spec.of("std.types.Integer"))
# → None  (Integer is a leaf — no fields)

schema = host.schema_for(pm.Spec.of("myapp.Point"))
# → IndexedType(VaryingType(int_t, int_t), Index(Id("x"), Id("y")))
```

### `val_is_leaf / val_children / val_reconstruct`

These three methods allow hosts to handle values whose structure is not captured by the `pm.Type` hierarchy alone. For example, a host bridging a database ORM may need to traverse related objects.

| Method | Purpose |
|---|---|
| `val_is_leaf(meta, data)` | Can this value be traversed? Default: `True` |
| `val_children(meta, data)` | Return child carriers. Default: `()` |
| `val_reconstruct(meta, children)` | Rebuild value from modified children |

!!! warning
    `val_reconstruct` raises `NotImplementedError` in the base class. Hosts that support mutable traversal must override it.

### `eval_logic_op`

Called by the reasoning engine when a goal contains a logic operator (a `Placeholder` in the head position). Returns a result or `None` to signal that the operator cannot be evaluated yet.

---

## `current_host()`

Returns the active host from the `HOST` context variable:

```python
from pm import current_host, HOST

host = current_host()     # equivalent to pm.HOST.get()
```

`HOST` is a `ContextVar[Host]` with `NativeHost()` as the default. You can override it for the duration of a `with` block:

```python
token = pm.HOST.set(my_custom_host)
try:
    # all type operations use my_custom_host
    ...
finally:
    pm.HOST.reset(token)
```

`pm.HOST` currently controls ordinary host-sensitive type operations.

Under the roadmap, this context model is expected to collapse into a single
tracked semantic context (`REALM`) shared by type, qualifier, and reasoning
operations.

---

## Implementing a custom host

```python
import pm
from pm import Host

class MyHost(Host, pm.Builtin):
    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        if spec.anchor == "myapp.Point":
            return pm.IndexedType.of(x=pm.Spec.of("std.types.Integer"),
                                     y=pm.Spec.of("std.types.Integer"))
        return None

# Register as the active host
pm.HOST.set(MyHost())
```

---

## API reference

::: pm.Host

::: pm.current_host
