# Layer 4 — Traversal & Unification

This layer provides two fundamental algorithms: **paired tree traversal** (`deep_zip`) and **structural unification** (`unify` + `UnionFind`). Together they form the computational core that the reasoning engine is built on.

---

## Traversal — `deep_zip`

`deep_zip` walks two carrier trees in lock-step, yielding paired nodes at each level.

```python
from pm import deep_zip, ZipWalker

for left, right in deep_zip(carrier_a, carrier_b):
    print(left.fetch(), right.fetch())
```

The walker raises `_ZipMismatch` (internally) when the trees diverge structurally — different arities or leaf/non-leaf mismatch. Unification catches this to signal failure.

`ZipWalker` supports `skip()`: call it on the walker to prevent descending into the current node's subtrees. This is used by unification when a variable is encountered — the variable is bound rather than traversed.

---

## Unification

### Background — Robinson unification

**Unification** (Robinson, 1965)[^1] is the process of finding a substitution $\sigma$ such that $\sigma(t_1) = \sigma(t_2)$ for two terms $t_1$ and $t_2$.

For two terms $f(X, b)$ and $f(a, Y)$:

$$\sigma = \{X \mapsto a,\ Y \mapsto b\}$$

The algorithm works structurally:

1. If both terms are the same variable, succeed with empty substitution.
2. If one is a variable, bind it to the other (occurs check first).
3. If both are function symbols with the same head, unify children pairwise.
4. Otherwise, fail.

**Occurs check**: before binding $X \mapsto t$, verify $X \notin t$. Without it, binding $X \mapsto f(X)$ would create a cyclic term.

[^1]: J. A. Robinson, "A Machine-Oriented Logic Based on the Resolution Principle", *JACM* 12(1), 1965.

---

### `UnionFind` — the substitution environment

Rather than building a substitution as a plain `dict`, Protomorph uses a **Union-Find** (disjoint-set) structure. This gives:

- **O(α(n)) amortised** find operations via path compression.
- **Structural sharing** — no need to deep-copy substitutions.
- **Rollback** via a trail — operations are logged and can be undone.

#### Core operations

```python
from pm import UnionFind, placeholder, wrap

is_var = lambda c: isinstance(c.fetch(), pm.Placeholder)
uf = UnionFind(is_var)

x_carrier = wrap(placeholder("X"))
a_carrier  = wrap(pm.Spec.of("test.a"))

uf.bind(x_carrier, a_carrier)

root = uf.find(x_carrier)
print(root.fetch())    # test.a  — X is now bound to a
```

#### Path compression

`find(x)` follows the parent chain to the canonical root, then rewrites every pointer on the path to point directly to the root. This flattens the tree over time.

```
Before: X → Y → Z (root)
After:  X → Z, Y → Z  (all point to root)
```

#### Rank heuristic — `_link`

When merging two equivalence classes, `_link` attaches the shallower tree under the deeper one. Non-variable nodes are preferred as roots (a ground term is a better representative than a variable).

#### Rollback

Every mutation to `_parent` and `_rank` is logged to `_trail`. A snapshot marks the current trail length; rollback replays the log in reverse.

```python
snap = uf.snapshot()
uf.bind(x_carrier, a_carrier)   # tentative binding
# ... try something ...
uf.rollback(snap)               # undo the binding
```

!!! note "Assertion"
    `rollback(mark)` asserts `0 <= mark <= len(trail)`. Passing a stale mark from a previous UnionFind instance raises `AssertionError` immediately.

#### Class info

Each equivalence class can carry an arbitrary `info` value (used by the reasoning engine to attach constraint metadata). Info is merged on union via a user-supplied `merge_info` callback.

---

### `unify`

The public entry point combines tree traversal with `UnionFind` binding:

```python
from pm import unify, placeholder, wrap, Spec

x = placeholder("X")
result = unify(
    wrap(Spec.of("test.f", x, Spec.of("test.b"))),
    wrap(Spec.of("test.f", Spec.of("test.a"), placeholder("Y"))),
    is_var=lambda c: isinstance(c.fetch(), pm.Placeholder),
)
# result = test.f(test.a, test.b)  — reified
```

**Signature:**

```python
def unify(
    a: Carrier,
    b: Carrier,
    *,
    is_var: Callable[[Carrier], bool] | None = None,
    subst:  UnionFind | None = None,
    occurs_check: bool = True,
) -> Carrier | None
```

Either `is_var` (creates a fresh `UnionFind`) or `subst` (accumulates into an existing one) must be provided. Pass `subst` when you need bindings to persist across multiple `unify` calls.

Returns the reified result rooted at `a`, or `None` on failure.

#### Walk algorithm

```python
stack = [(a, b)]
while stack:
    left, right = stack.pop()
    left, right = uf.find(left), uf.find(right)

    if left is right: continue          # already equal

    if l_var or r_var:
        uf.bind(var, term)              # bind variable
        continue

    # both non-var
    if left.is_leaf and right.is_leaf:
        if left != right: return False  # ground mismatch

    stack.extend(zip(children(left), children(right)))   # recurse
```

The iterative stack replaces recursion — safe for deeply nested types.

---

## Example: shared substitution across two goals

```python
import pm
from pm import UnionFind, unify, placeholder, wrap, Spec

is_var = lambda c: isinstance(c.fetch(), pm.Placeholder)
subst  = UnionFind(is_var)

x = placeholder("X")
y = placeholder("Y")

# Goal 1: f(X, b) = f(a, Y)  → X=a, Y=b
unify(wrap(Spec.of("f", x, Spec.of("b"))),
      wrap(Spec.of("f", Spec.of("a"), y)),
      subst=subst)

# Goal 2: g(Y) = g(b)   — Y is already b, should succeed
result = unify(wrap(Spec.of("g", y)),
               wrap(Spec.of("g", Spec.of("b"))),
               subst=subst)

print(result)   # g(b)
```

---

## API reference

::: pm.deep_zip

::: pm.ZipWalker

::: pm.UnionFind

::: pm.unify
