# Protobase

Protobase is a small Python runtime that provides a custom class system for
immutable, slot-based records with derived methods, structural hashing,
hash-consing, and dependency-tracked computed properties (flux). It is intended
as a foundational layer for graph-structured domain models where values are
canonical, comparable, and efficiently recomputed.

## Quickstart

### Immutable records and defaults

```python
from protobase import Inmutable

class Point(Inmutable):
    x: int
    y: int = 0

p1 = Point(1)
p2 = Point(1)
print(p1 == p2)  # True (structural equality)
print(p1 is p2)  # False (unless using Consed)
```

Defaults are deep-copied on init to avoid shared mutable state.

### Persistent updates with mutate

```python
from protobase import Inmutable, mutate

class Box(Inmutable):
    value: int

box = Box(1)
updated = mutate(box, value=2)
print(box.value)     # 1
print(updated.value) # 2
```

### Hash-consing (canonicalization)

```python
from protobase import Consed

class Symbol(Consed):
    name: str

a = Symbol("x")
b = Symbol("x")
print(a is b)  # True
```

### Flux inputs and computed properties

```python
from protobase import flux

class Config:
    __slots__ = ("__weakref__",)

    @flux.input
    def value(self) -> int:
        raise NotImplementedError

    @flux.property
    def doubled(self) -> int:
        return self.value * 2

cfg = Config()
cfg.value = 3
print(cfg.doubled)  # 6
cfg.value = 4       # invalidates lazily
print(cfg.doubled)  # 8
```

### Flux invalidation and stats

```python
from protobase import flux

class Counter:
    __slots__ = ("value", "__weakref__")

    def __init__(self, value: int) -> None:
        self.value = value

    @flux.method
    def add(self, delta: int) -> int:
        return self.value + delta

counter = Counter(1)
counter.add(2)
counter.add(2)
print(Counter.add.stats())
Counter.add.invalidate_for(counter)  # force recompute on next access
counter.add(2)
```

## Philosophy

- Model domain data as immutable, canonical objects with explicit slots.
- Prefer structural equality and hashing over identity-based semantics.
- Generate boilerplate via a metaclass and derived methods to keep semantics
  consistent and predictable.
- Treat computed properties as pure functions of the reachable graph.
- Track dependencies to enable incremental recomputation instead of full
  recompute.

## Flux runtime (overview)

Flux memoizes query results, records dependencies during evaluation, and uses
pull-based invalidation to decide when recomputation is required.

Core concepts:

- Key: a unique invocation identity (function id, instance weakref, args/kwargs)
- Memo: cached value plus timestamps, deps, and emits
- Dep: edge to another Key with the revision it was seen at
- revision: a global counter advanced on input set/invalidate or explicit invalidation

Execution flow (simplified):

```
fetch(query, obj, args, kwargs)
  -> build Key
  -> memo hit? verify deps
      -> return cached value
  -> enter query context
      -> run function
      -> record deps/emits
      -> store Memo
      -> return value
```

Cycles are detected by tracking the active Key stack and raise a CycleError.

## Limitations and gotchas

- Queries must return concrete values; generators/async/awaitables are rejected.
- Instances used with `flux.method`/`flux.property` must be weakrefable
  (`Record`/`Inmutable` add `__weakref__` automatically; plain classes must include it).
- Args and kwargs must be hashable (they are part of the cache key).
- Do not mutate inputs during query execution.
- `flux.input` values live in the runtime, not on the object itself.

## Formal formulation (light)

### Definitions

1. Canonical immutable object: An instance `o` whose attributes are restricted
   to immutable or protobase records. Its structural state is the ordered tuple
   of attribute values `S(o)`. A structural hash `h(o) = hash(S(o))` is stable
   across program execution. If hash-consing is enabled, any two objects with
   equal structural state are represented by a single canonical instance.
2. Reachable subgraph: The directed acyclic graph `G(o)` formed by recursively
   following record-valued attributes from `o`. The DAG is well-formed because
   objects are immutable and references are stable; cycles are disallowed during
   computed-property evaluation (and are detected if present).
3. Computed property (flux): A function `p` bound to a class such that
   `p(o)` is a deterministic function of `G(o)` and is memoized. A query records
   dynamic dependencies during execution, producing a dependency graph `D`.

### Invariants

- Immutability: once constructed, attributes are not mutated; object state is
  stable over time.
- Structural determinism: `S(o)` uniquely determines `o`'s equality and hash.
- Graph purity: a computed property depends only on reachable data in `G(o)`.
- Acyclic evaluation: dependency cycles in `D` are detected and rejected.

### Consequences

- Safe memoization: results are cached by structural state and/or identity.
- Subproblem reuse: shared subgraphs correspond to shared subproblem results.
- Incremental recomputation: only affected queries are invalidated and
  recomputed when dependencies change.
- Flux queries must return concrete values; generators and awaitables are not supported.

## Dynamic programming and DAGs

Protobase treats immutable object graphs as DAGs, and computed properties as
solutions to subproblems defined over those DAGs. This directly mirrors dynamic
programming: each node is solved once, results are reused by dependents, and
the evaluation order follows the dependency structure. Flux adds runtime
dependency tracking, turning classic memoization into incremental, self-
adjusting recomputation.

## Performance and model of computation

- Treat the object graph as a DAG; each query is a subproblem over that DAG.
- Dependency tracking enables incremental recomputation proportional to use.
- Hash-consing increases structural sharing and makes equality cheaper.
- Costs include hashing and dependency bookkeeping; best for stable graphs
  with significant reuse.

## Paradigm map

| Paradigm | Correspondence in protobase | Benefit | Example |
| --- | --- | --- | --- |
| Dynamic programming on DAGs | objects as nodes, properties as subproblems | reuse results, avoid recomputation | compute types from AST nodes |
| Functional programming | immutability and pure derived functions | referential transparency, cache safety | structural hash + equality |
| Dataflow / reactive systems | dependency graph + invalidation | incremental recompute | `flux.invalidate_for(obj)` |
| Self-adjusting computation | dynamic dependency tracking | minimal recompute | recompute only affected queries |
| Persistent data structures | structural sharing | memory/time efficiency | shared sub-records |
| Hash-consing / canonicalization | deduplicate equal structures | single-instance reuse | `Consed` base class |

## Use cases

- Language implementations: AST, IR, semantic graphs, and analysis results.
- Incremental compilation and linting pipelines with cached analyses.
- Configuration and schema graphs with canonical nodes.
- Dependency graphs for build systems or evaluation engines.
- Any domain model where identity should follow structure, not allocation.

## Terminology

- Record: a slot-based object with derived init/eq/repr and explicit attributes.
- Inmutable: a Record that enforces deep immutability and structural hashing.
- Consed: an Inmutable that applies hash-consing (canonicalization).
- Structural state: ordered tuple of attribute values used for equality/hash.
- Reachable subgraph: the transitive closure of record references from `self`.
- Computed property: `flux.property` result, memoized and dependency-tracked.
- Query: `flux.method` result, memoized and dependency-tracked.
- Dependency graph: runtime graph of query dependencies used for invalidation.
- Incremental invalidation: selective recomputation based on dependency edges.
- Emit/collect: a mechanism to gather derived items from query execution.

## Default values and deepcopy

Protobase treats attribute defaults as *template values* rather than shared
instances. During initialization, any attribute with a default value is
assigned by **deep-copying** that default. This prevents mutable defaults
(lists, dicts, nested records) from being shared across instances.

Behavioral summary:

- Positional attributes are assigned directly from constructor arguments.
- Nominal attributes (with defaults) use the provided argument if present.
- If a nominal attribute is omitted, its default is **deep-copied** and stored
  in the instance.

Implications:

- Each instance gets an independent copy of mutable defaults.
- Defaults that are already immutable (numbers, strings, tuples, records) are
  safe; deepcopy is still applied but cheap.

## LSP-friendly required fields

Pyright enforces that non-default fields cannot follow default fields. If you
want to keep a field required while placing it after defaults, use the `Missing`
sentinel via the `_` alias:

```python
from protobase import Object, _


class Config(Object):
    x: int = 5
    y: int = _
```

`_` is typed as `Any`, and is normalized to "no default" during class build, so
the derived `__init__` still requires `y`.

## Documentation

Extended documentation lives in `docs/README.md` and includes guides for the
class system, immutability, hash-consing, and flux.
Examples live in `examples/`.

## Architecture at a glance

- `src/protobase/type.py` - metaclass builder pipeline and metadata
- `src/protobase/object.py` - attribute collection, slots, defaults, state
- `src/protobase/record.py` - Record base class, derived repr/eq/order, mutate
- `src/protobase/inmutable.py` - deep immutability checks and structural hash
- `src/protobase/consed.py` - hash-consing and canonicalization
- `src/protobase/flux.py` - dependency-tracked memoization runtime
- `src/protobase/derived.py` - derived method descriptor
- `src/protobase/cached_property.py` - cached and slot-backed cached properties
- `src/protobase/metadata.py` - metadata tagging for objects
- `src/protobase/frozendict.py` - immutable dictionary helper

## Requirements

- Python 3.13+ (see `pyproject.toml`)
