\# Protobase

Protobase is a small Python runtime that provides a custom class system for
immutable, slot-based records with derived methods, structural hashing,
hash-consing, and dependency-tracked computed properties (flux). It is intended
as a foundational layer for graph-structured domain models where values are
canonical, comparable, and efficiently recomputed.

\## Philosophy

- Model domain data as immutable, canonical objects with explicit slots.
- Prefer structural equality and hashing over identity-based semantics.
- Generate boilerplate via a metaclass and derived methods to keep semantics
  consistent and predictable.
- Treat computed properties as pure functions of the reachable graph.
- Track dependencies to enable incremental recomputation instead of full
  recompute.

\## Formal formulation (light)

\### Definitions

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

\### Invariants

- Immutability: once constructed, attributes are not mutated; object state is
  stable over time.
- Structural determinism: `S(o)` uniquely determines `o`'s equality and hash.
- Graph purity: a computed property depends only on reachable data in `G(o)`.
- Acyclic evaluation: dependency cycles in `D` are detected and rejected.

\### Consequences

- Safe memoization: results are cached by structural state and/or identity.
- Subproblem reuse: shared subgraphs correspond to shared subproblem results.
- Incremental recomputation: only affected queries are invalidated and
  recomputed when dependencies change.
- Flux queries must return concrete values; generators and awaitables are not supported.

\## Dynamic programming and DAGs

Protobase treats immutable object graphs as DAGs, and computed properties as
solutions to subproblems defined over those DAGs. This directly mirrors dynamic
programming: each node is solved once, results are reused by dependents, and
the evaluation order follows the dependency structure. Flux adds runtime
dependency tracking, turning classic memoization into incremental, self-
adjusting recomputation.

\## Paradigm map

| Paradigm | Correspondence in protobase | Benefit | Example |
| --- | --- | --- | --- |
| Dynamic programming on DAGs | objects as nodes, properties as subproblems | reuse results, avoid recomputation | compute types from AST nodes |
| Functional programming | immutability and pure derived functions | referential transparency, cache safety | structural hash + equality |
| Dataflow / reactive systems | dependency graph + invalidation | incremental recompute | `flux.invalidate_for(obj)` |
| Self-adjusting computation | dynamic dependency tracking | minimal recompute | recompute only affected queries |
| Persistent data structures | structural sharing | memory/time efficiency | shared sub-records |
| Hash-consing / canonicalization | deduplicate equal structures | single-instance reuse | `Consed` base class |

\## Use cases

- Language implementations: AST, IR, semantic graphs, and analysis results.
- Incremental compilation and linting pipelines with cached analyses.
- Configuration and schema graphs with canonical nodes.
- Dependency graphs for build systems or evaluation engines.
- Any domain model where identity should follow structure, not allocation.

\## Terminology

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

\## Default values and deepcopy

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

\## Documentation

Extended documentation lives in `docs/README.md` and includes guides for the
class system, immutability, hash-consing, and flux.

\## Key components

- `src/protobase/type.py` - metaclass and class construction
- `src/protobase/object.py` - slots, init, and attribute collection
- `src/protobase/record.py` - Record base class and mutation helper
- `src/protobase/derived.py` - derived method generation
- `src/protobase/flux.py` - dependency-tracked memoization
- `src/protobase/inmutable.py` - Inmutable base class and immutability checks
- `src/protobase/consed.py` - hash-consed immutable base class

\## Requirements

- Python 3.13+ (see `pyproject.toml`)
