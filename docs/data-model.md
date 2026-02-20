# Data Model

## Purpose

This document specifies the domain data model used by Axis during parsing,
partial evaluation, type resolution, and final evaluation.

The core idea is a strict separation between:
- the descriptor of a datum (`Type`), and
- the datum itself (`Data`).

All values in the language flow as `Val`, even in partial and lazy phases.


## Core Concepts

### Value

`ValueBase` represents a value in the language. It is immutable and hash-consed.

- `type`: a descriptor that defines the shape/meaning of the value.
- `data`: the underlying datum (only present on concrete values).

`ValueBase` is the only container used across evaluation phases. `Val` is the
general-purpose concrete value type.

Serialization principle:

- `data` is the serialized, canonical form.
- `type` is the deserialized, structural form.

Concrete variants:
- `Const`: a known value with concrete data (abstract base).
- `Val`: literal/general-purpose value.
- `Meta`: literal value representing a `Type` directly.
- `Var`: a placeholder value with stable identity.


### Const and Var

`Const` and `Var` are concrete forms of `ValueBase` (with `Const` as an
abstract base and `Val`/`Meta` as concrete implementations).

`Const` always contains concrete, immutable data.
`Var` represents an unknown value that is still well-typed.

`Var` is used for generics and placeholders. It does not carry AST or runtime
environments.

Canonical encoding for `Var` data:

- `Var` stores its identity as a tagged tuple: `( "var", id )`.
- `id` is a stable, interned identifier.
- This encoding is used whenever a variable value must be embedded inside
  another data structure.

Type-level vs value-level placeholders:

- `Type.var("T")` is a type-level placeholder.
- `Var(type=VarType("T"), data=("var", "T"))` is a value placeholder
  typed by that `Type.var`.

Var and context:

- `Var` remains pure and canonical; it does not embed AST or env.
- If a phase needs origin context, it should be stored in a side table
  keyed by the variable id (e.g. `var_origin[id] = (ast, env, constraints)`).


### Data

`Data` is a primitive, structural representation. It does not encode meaning.
The meaning is entirely in `Type`.

Base forms:
- `Atom`: `int | float | Decimal | str | bool | None`
- `tuple`
- `frozenset`
- `frozendict`

Default encoding preference:
- Use low-level `tuple` for canonical encodings and discriminated unions.
- Use `frozendict` when JSON-like key/value shape is required.

`Data` does not include executable structures.


### Type

`Type` is the descriptor class for values. All descriptors in the system are
instances of a closed set of `Type` variants.

`Type` is immutable, hash-consed, and independent of runtime values or AST.


#### Type Principles

- Canonical and hash-consed: equal types are a single shared instance.
- Context-free: a type does not depend on runtime values or AST nodes.
- Descriptive only: type defines the domain and invariants of `data`.
- Stable across phases: type can be used for dispatch, unification, and
  constraint solving independently of evaluation phase.


#### Qualifiers

A qualifier is a `Type` that wraps an underlying type. It is used to express
qualified values while keeping the type system explicit.

- `Qualifier(underlying)` is an abstract base.
- `NominalQualifier(ref, underlying)` is the concrete qualifier used today.


#### Type and Values

- `ValueBase` carries one `type`.
- `Const` is an abstract literal base; concrete literal values (`Val`, `Ref`) carry `data`.
- `Meta` is a literal value with no data; it represents a `Type` as a value.
- `Var` is a non-literal value used in patterns and bounds.
- `type` is created once; many values share it.
- `data` is shaped by `type` but does not carry meaning by itself.


#### Type and Variants

`Type` is the single descriptor class. It is abstract and specialized by
variants.

`std.Type` reflects the same model as `axis.dom.Type`.

Variants:

- `NominalType(ref)`
- `StructType(fields)`
- `FnType(args, ret)`
- `UnionType(members)`
- `VarType(id)`
- `RefType(parent, params)`
- `Qualifier(underlying)`
- `NominalQualifier(ref, underlying)`

Only these variants define the meaning of `Type`.

Shorthand:

- `Ref("X")` stands for `Ref(parent=None, member="X")`.
- `NominalType(ref=Ref("X"))` stands for a nominal type identified by `Ref("X")`.


#### StructType

Descriptor for structural tuples/records.

Shape:
- `fields: Tuple[str | None, Type]` where the `Tuple` is aligned to an `Index`.
- Positional elements are represented with `None` keys in the `Index`.
- Nominal elements carry their key as the `Index` entry.

Data representation:
- `data` is a plain `tuple` of values aligned to `fields.index`.
- The key space is carried by the `Index`, not by `data`.

Invariants:
- Index keys are unique and arity matches the value count.
- Positional elements must appear before nominal elements.
- `fields.values` are types for each position.

Example:
- `(x: Natural, y: Text)` =>
  `Index(keys=("x", "y"))` and
  `fields.values=(NominalType(ref=Ref("Natural")), NominalType(ref=Ref("Text")))`


#### NominalType

Descriptor for nominal types.

Shape:
- `ref: Ref` is a stable, interned nominal reference (e.g. `std.Natural`).
- The `ref` may carry hyperparameters; specialization lives in `Ref`.
- The structural description of the nominal type is computed from the `Ref`.

Invariants:
- `ref` is interned and canonical.
- Hyperparameters are encoded in `ref.params` (value-level) and serialized in
  `ref.data`.

Example:
- `Array[3]` =>
  `NominalType(ref=Ref(parent=Ref("Array"), member="[...]" ) ...))`
- `Person` =>
  `NominalType(ref=Ref("Person"))`


## Structural Data (Tuple/Index/Shape)

`Tuple`, `Index`, and `Shape` are canonical structural representations.

- `Index` stores positional/nominal keys.
- `Tuple` stores values aligned with an `Index`.
- `Shape` describes arity and keyed positions.

These structures define local invariants and are reused as descriptors
inside `StructType`.


## Ref (Nominal Reference)

`Ref` is the canonical, interned representation of a nominal reference.
It is a concrete value: `Ref` is `Const[RefType, RefData]`.

### Shape

`Ref` is a path with explicit structure and optional parameters:

- `parent: Ref | None`
- `member: str`
- `params: Tuple[str | None, Const]`

`RefType` describes the structural type of a reference:

- `parent: RefType | None`
- `params: Tuple[str | None, Const]`

`segments` is a derived view of the full path.

### Examples

- `std.Array` =>
  `Ref(parent=None, member="std").member_ref("Array")`
- `std.Map` =>
  `Ref(parent=None, member="std").member_ref("Map")`


## Partial Evaluation (Lazy Values)

Partial evaluation normalizes AST into canonical DOM structures and
propagates constants. Unresolved values are represented as `Var`.

Key properties:
- No new AST node types are introduced.
- The same `Val` container is used in all phases.
- `type` must always be valid even when the value is a `Var`.


## Validation and Constraints

Validation is separated from construction:
- First, build canonical structures (`Type`, `Ref`, `StructType`, etc.).
- Then, validate invariants and type constraints.

Examples:
- `Array[3]` validates that `3` is a `Natural`.
- `StructType` validates positional-before-nominal ordering.


## Types as Values

The system may represent types as values by using `Meta`, which is a literal
value that carries only a `type` (no `data`). This avoids serialization or
reflection mechanisms while preserving expressiveness.


## Compact Examples

Nominal (no params):

- `NominalType(ref=Ref("std.Text"))`

Nominal (with params in Ref):

- `Array[3]` =>
  `NominalType(ref=<Ref("Array") with param 3>)`

Struct (record):

- `(name: Text, age: Natural)` =>
  `StructType(fields=Tuple(Index(("name", "age")), (NominalType(ref=Ref("std.Text")), NominalType(ref=Ref("std.Natural")))))`

Function:

- `(Natural, Natural) -> Natural` =>
  `FnType(args=(NominalType(ref=Ref("std.Natural")), NominalType(ref=Ref("std.Natural"))), ret=NominalType(ref=Ref("std.Natural")))`

Union:

- `Natural | Text` =>
  `UnionType(members=(NominalType(ref=Ref("std.Natural")), NominalType(ref=Ref("std.Text"))))`

Literal type:

- `Val(type=NominalType(ref=Ref("std.Integer")), data=3)`

Type variable:

- `Type.var("T")` =>
  `VarType("T")`

Value (nominal instance):

- `Person("john", 33)` =>
  `Val(type=NominalType(ref=Ref("Person")), data=("john", 33))`

Ref:

- `Ref("std.Array")` => `Ref(parent=None, member="std").member_ref("Array")`

## Evaluation Phases

Phase 1: Parse

- Build the AST from source. No DOM objects are created yet.
- Example: `Array[3]` is parsed as an index/symbol expression in the AST.

Phase 2: Elaboration and Normalization

- Convert AST into canonical `ValueBase` forms (`Const` or `Var`).
- Build `Type` and `Ref` objects.
- Encode hyperparameters into `Ref.params` when specializing entities.
- Validate structural invariants (Index uniqueness, positional before nominal).
- Example: `Array[3]` becomes `NominalType(ref=<Ref("Array") with param 3>)`.
- Example: `Person("john", 33)` becomes `Val(type=NominalType(ref=Ref("Person")), data=("john", 33))`.

Phase 3: Type Resolution and Constraints

- Resolve `Type.var` and `Var` placeholders using constraints.
- Specialize schemas using parameter values.
- Validate qualifiers and enforce type constraints.
- Resolve overloads/dispatch using the resolved types.
- Example: `Array[W]` with `W` inferred as `3` yields a specialized schema.

Phase 4: Final Evaluation

- Evaluate runtime semantics using resolved types and schemas.
- Produce `Const` results when possible; leave residual `Var` only for
  runtime-dependent values.
- Example: arithmetic with known literals reduces to a `Const` value.

Reflection is intentionally omitted from the core model.


## Open Decisions (To Iterate)

None.
