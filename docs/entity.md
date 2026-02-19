# Entity System

## Purpose

This document specifies the entity system used by Axis for semantic
resolution, evaluation, and logical inference. Entities unify three roles:

- runtime values (first-class and reflectable),
- namespace members (hierarchical references), and
- logical rules (Datalog-style inference).

Entities are referenced by `Ref` and participate in dispatch, overload
resolution, and contextual return selection.


## Core Concepts

### Entity

An entity is a semantic object identified by a `Ref` and composed from
multiple contributions. It supports:

- access (injector-like behavior),
- members (`Entity.child`),
- construction (`Entity(...)`),
- indexation (`Entity[...]`),
- indexation + construction (`Entity[...](...)`),
- logical rules (Datalog facts and rules).

Entities are coherent across contributions: a final entity must not be
ambiguous in any of its behaviors.


### Ref (Generic and Specialized)

`Ref` identifies both generic entities and specialized entities. A specialized
entity such as `Range[Natural]` is a valid `Ref` and can be used as a type
expression. Both generic and specialized forms are first-class.

The `Ref` encoding must remain immutable and canonical. Parameterization is
encoded as primitive data (not as nested `Val` objects).


### Provider (Lazy Instance)

A construction without a specified return type yields a provider, a lazy
value that captures:

- the entity `Ref` (possibly specialized),
- hyperparameters (if already inferred),
- constructor arguments (slots), and
- pending constraints.

Providers are first-class values and are reflectable. They can be passed
around and materialized later when a return type is required.

`Ref` reflection preserves meta information via a parametrized `std.Ref`:

- `Ref.to_val().meta = Type(Nominal(ref=Ref("std.Ref")))` where the `std.Ref`
  reference is parametrized with `(parent_ref, params_type_tuple)`.
- `Ref.to_val().data = (parent_data, member, params_data)`.


## Indexation vs Construction

### Indexation (Hyperparameters)

Indexation selects hyperparameters and restricts the domain of an entity.
It yields a specialized entity.

Example:

- `Range[Natural]` produces a specialized entity whose schema is computed
  by reifying the entity definition with the hyperparameters.

Indexation always validates constraints and returns an entity that is already
specialized and coherent.


### Construction (Slots / Scheme)

Construction assigns runtime parameters to slots and validates constraints.
It does not execute code by default; it behaves like a dataclass constructor.

Example:

- `Range[Natural](0, 100)` assigns `start=0`, `end=100` and validates bounds.

Construction yields a provider unless a return type is requested.


## Return Dispatch (Transformations)

If an entity defines explicit returns (via `->` or `returns`), the provider can
be coerced into a concrete return type by applying a transformation over the
dataclass instance.

The expected type determines which return to apply.

Example:

```
let init = full(15)
let a: Array[3,3] Natural = init
let b: Array[2,2] Real = init
```

`init` is a provider; the expected type selects the appropriate return
implementation to produce the final value.


## Meta Serialization and Reification

Meta is a deserialized structure, while data is its canonical serialized form.
Two operations are defined in `axis.dom`:

- serialize: meta to data (reflection),
- reify: data to meta (deserialization).

Serialization uses the canonical encodings described in the data model
(`Type.to_val()`, `Ref.to_val()`). Reification reconstructs meta structures
from primitive data and may create new meta instances.

Planned API surface in `axis.dom`:

- `Ref.from_val(data)` / `Ref.from_data(data)`
- `Type.from_val(data)` / `Type.from_data(data)`

Reification errors must raise exceptions at the Python level or produce an
`Err` result at the Axis level.


## Overload Resolution Pipeline

Dispatch is resolved in phases:

1) filter by arity and tuple shape,
2) type and constraint checking,
3) infer hyperparameters (indexation constraints),
4) construct the provider (dataclass instance),
5) if an expected type exists, select and apply a return transformation.

Resolution errors are raised when the behavior is ambiguous or inconsistent.


## Entity Consolidation

Entities are built from immutable contributions, enabling incremental
recomputation.

Each item can contribute multiple behaviors, potentially to multiple refs.
Contributions are grouped by `Ref` and consolidated into a final entity.

The consolidation rules require:

- no ambiguity in access, construction, indexation, or returns,
- coherent member sets,
- consistent schema and constraints,
- resolvable overload sets.


## Logical System

Logical inference, facts, rules, and queries are specified in
`docs/logic-design.md`. This document focuses on entity consolidation,
overload resolution, and runtime behavior.


## Examples

### Range

`Range(100)` resolves as:

- infer hyperparameters: `Range[Natural]`
- apply defaults: `Range[Natural](0, 100)`
- produce provider (or materialize if return type is expected)


### Identity

`let a: Array[3,3] = identity` produces a 3x3 identity matrix by
forcing the provider with the expected type.
