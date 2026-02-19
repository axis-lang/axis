# Data Model

## Purpose

This document specifies the domain data model used by Axis during parsing,
partial evaluation, type resolution, and final evaluation.

The core idea is a strict separation between:
- the descriptor of a datum (`Meta`), and
- the datum itself (`Data`).

All values in the language flow as `Val`, even in partial and lazy phases.


## Core Concepts

### Value

`Val` represents a value in the language. It is immutable and hash-consed.

- `meta`: a descriptor that defines the shape/meaning of the value.
- `data`: the underlying datum (always primitive).

`Val` is the only container used across evaluation phases.

Concrete variants:
- `Const`: a known value with concrete data.
- `Var`: a placeholder value with stable identity.


### Const and Var

`Const` and `Var` are the two concrete forms of `Val`.

- `Const` always contains concrete, immutable data.
- `Var` represents an unknown value that is still well-typed.

`Var` is used for generics and placeholders. It does not carry AST or runtime
environments.

Canonical encoding for `Var` data:

- `Var` stores its identity as a tagged tuple: `( "var", id )`.
- `id` is a stable, interned identifier.
- This encoding is used whenever a variable value must be embedded inside
  another data structure.

Type-level vs value-level placeholders:

- `Type.Var("T")` is a type-level placeholder.
- `Var(meta=Type(form=Var("T")), data=("var", "T"))` is a value placeholder
  typed by that `Type.Var`.

Var and context:

- `Var` remains pure and canonical; it does not embed AST or env.
- If a phase needs origin context, it should be stored in a side table
  keyed by the variable id (e.g. `var_origin[id] = (ast, env, constraints)`).


### Data

`Data` is a primitive, structural representation. It does not encode meaning.
The meaning is entirely in `Meta`.

Base forms:
- `Atom`: `int | float | str | bool | None`
- `tuple`
- `frozenset`
- `frozendict`

Default encoding preference:
- Use low-level `tuple` for canonical encodings and discriminated unions.
- Use `frozendict` when JSON-like key/value shape is required.

`Data` does not include executable structures.


### Meta

`Meta` is univocal and represented by a single class: `Type`.
All descriptors in the system are instances of `Type`.

`Type` is immutable, hash-consed, and independent of runtime values or AST.


#### Meta Principles

- Canonical and hash-consed: equal metas are a single shared instance.
- Context-free: a meta does not depend on runtime values or AST nodes.
- Descriptive only: meta defines the domain and invariants of `data`.
- Stable across phases: meta can be used for dispatch, unification, and
  constraint solving independently of evaluation phase.


#### Meta and Val

- `Val` carries one `meta` and one `data`.
- `meta` is created once; many values share it.
- `data` is shaped by `meta` but does not carry meaning by itself.


#### Type and TypeForm

`Type` is the single meta class. It is parameterized by:
- `qualifiers: tuple[Type, ...]` (ordered, can repeat)
- `form: TypeForm`

`std.Type` reflects the same model as `axis.dom.Type`.

Standard nominal types:

- `std.Type` has no parameters.
- Its `params` value is the empty struct: `Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=())`.
- Its `schema` is `None` (opaque by default).
- This keeps reflection simple and avoids universe levels for now.

`TypeForm` is a closed family of variants that describes the structure
of the type:

- `Nominal(ref, params, schema)`
- `Struct(fields)`
- `Function(args, ret)`
- `Union(members)`
- `Literal(value)`
- `Var(id)`

Only these variants define the meaning of `Type`.

Shorthand:

- `Ref("X")` stands for `Ref(segments=("X",))`.
- `Type(Nominal(Ref("X")))` stands for a nominal type with empty params:
  `Type(Nominal(ref=Ref("X"), params=Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=()), schema=None))`.


#### TypeForm: Struct

Descriptor for structural tuples/records.

Shape:
- `fields: Tuple[str, Type]` where the `Tuple` is aligned to an `Index`.
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
  `fields.values=(Type(Nominal(Ref("Natural"))), Type(Nominal(Ref("Text"))))`


#### TypeForm: Nominal

Descriptor for nominal types with parameters.

Shape:
- `ref: Ref` is a stable, interned nominal reference (e.g. `std.Natural`).
- `params` represents the parameter list of the nominal reference.
- `schema` is the structural description of the nominal type, or `None` if opaque.

Canonical representation (decision):
- `params` is a `Const` whose `meta` is `Type` with `form=Struct` and whose
  `data` is the canonical parameter tuple.
- This keeps all phases using `Val` while preserving the `meta`/`data`
  separation.

Why this form:
- Supports positional and nominal parameters via `Struct.fields.index`.
- Keeps `Data` primitive; no `Val` is embedded inside `data`.
- Avoids `Meta` containing non-primitive data directly.

Invariants:
- `ref` is interned and canonical.
- `params.meta` must be `Type(form=Struct)`.
- `params.data` length matches `params.meta.form.fields.arity`.
- `params.data` is a primitive tuple; unknowns use the `Var` encoding.
- `params` is always a `Const`; unknowns are encoded inside `params.data`.
- `schema` may be `None` to represent an opaque nominal type.
- A ref may appear with different schemas (e.g. visibility, specialization, or
  opacification rules).

Type parameters that are themselves types:
- The parameter meta should be `std.Type`.
- The parameter data stores `Type.to_val().data` for that type.

Example:
- `Array[3]` =>
  `Type(Nominal(ref=Ref("Array"), params=Const(meta=Type(Struct(...)), data=(3,)), schema=<Type or None>))`
- `Array[W]` =>
  `Type(Nominal(ref=Ref("Array"), params=Const(meta=Type(Struct(...)), data=(("var", "W"),)), schema=<Type or None>))`
- `Map[Id]` =>
  `Type(Nominal(ref=Ref("Map"), params=Const(meta=Type(Struct(...)), data=(Type(Nominal(Ref("Id"))).to_val().data,)), schema=<Type or None>))`
- `Person` =>
  `Type(Nominal(ref=Ref("Person"), params=Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=()), schema=<Struct ...>))`


#### TypeForm: Qualified Types

Qualification is not a separate meta class. It is represented directly
by `Type.qualifiers`.

Interpretation:
- Qualifiers are ordered and can repeat.
- The `base` is the `form` in `Type`, qualifiers apply to it.

Invariants:
- Each qualifier must be a type value (not an arbitrary value).
- No reordering or deduplication of qualifiers.

Examples:
- `Array[3] Natural` =>
  `Type(qualifiers=(Type(Nominal(Ref("Array")), params=Const(...)),), form=Nominal(Ref("Natural")))`
- `Map[Id] (name: Text, age: Natural)` =>
  `Type(qualifiers=(Type(Nominal(Ref("Map")), params=Const(...)),), form=Struct(...))`


## Structural Data (Tuple/Index/Shape)

`Tuple`, `Index`, and `Shape` are canonical structural representations.

- `Index` stores positional/nominal keys.
- `Tuple` stores values aligned with an `Index`.
- `Shape` describes arity and keyed positions.

These structures define local invariants and are reused as descriptors
inside `TypeForm.Struct`.


## Ref (Nominal Reference)

`Ref` is the canonical, interned representation of a nominal reference.
It replaces the generic notion of “Symbol” and is used by `Type`.

### Shape

`Ref` is a path with ordered segments:

- `segments: tuple[str, ...]`

### Examples

- `std.Array` =>
  `Ref(segments=("std", "Array"))`
- `std.Map` =>
  `Ref(segments=("std", "Map"))`


## Ref Reflection

`Ref` can be reflected into a value for metaprogramming:

- `Ref.to_val()` returns `Val` with:
  - `meta = Type(form=Nominal(ref=Ref("std.Ref"), params=Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=()), schema=None))`
  - `data = segments` (a `tuple[str, ...]`)

The encoding is deterministic and should be cached for performance.


## Partial Evaluation (Lazy Values)

Partial evaluation normalizes AST into canonical DOM structures and
propagates constants. Unresolved values are represented as `Var`.

Key properties:
- No new AST node types are introduced.
- The same `Val` container is used in all phases.
- `meta` must always be valid even when the value is a `Var`.


## Validation and Constraints

Validation is separated from construction:
- First, build canonical structures (`Type`, `Ref`, `Struct`, etc.).
- Then, validate invariants and type constraints.

Examples:
- `Array[3]` validates that `3` is a `Natural`.
- `Struct` validates positional-before-nominal ordering.


## Types as Values

The system may represent types as values by using `Meta` as data
descriptors. A meta can be converted into a `Val` if needed.

This conversion must produce:
- a concrete `meta` for the resulting value, and
- a primitive `data` representation (not the meta itself).


## Type Reflection (Canonical Encoding)

`Type.to_val()` produces a `Val` whose data is a canonical encoding.
Discriminated unions are encoded as a tuple `(tag, data)` for performance.

Top-level encoding:
- `Type.to_val().meta = Type(form=Nominal(ref=Ref("std.Type"), params=Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=()), schema=None))`
- `Type.to_val().data = ("type", (qualifiers_data, form_data))`

Where:
- `qualifiers_data = tuple(q.to_val().data for q in qualifiers)`
- `form_data = (tag_data, payload)` following the union encoding

Tag encoding:

- `tag_data` is always a primitive `Data` value.
- Each `TypeForm` tag is represented by a `Ref` and encoded as `Ref.to_val().data`.
- Current tag refs:
  - `std.Type.Nominal`
  - `std.Type.Struct`
  - `std.Type.Function`
  - `std.Type.Union`
  - `std.Type.Literal`
  - `std.Type.Var`

TypeForm encodings:

- `Nominal(ref, params, schema)` => `( Ref("std.Type.Nominal").to_val().data, (ref.to_val().data, params.data, schema_data) )`
- `Struct(fields)` => `( Ref("std.Type.Struct").to_val().data, (index_data, fields_data) )`
- `Function(args, ret)` => `( Ref("std.Type.Function").to_val().data, (args_data, ret_data) )`
- `Union(members)` => `( Ref("std.Type.Union").to_val().data, (members_data,) )`
- `Literal(value)` => `( Ref("std.Type.Literal").to_val().data, value )`
- `Var(id)` => `( Ref("std.Type.Var").to_val().data, id )`

Where:
- `index_data = tuple(index.keys)`
- `fields_data = tuple(t.to_val().data for t in fields.values)`
- `args_data = tuple(t.to_val().data for t in args)`
- `ret_data = ret.to_val().data`
- `members_data = tuple(t.to_val().data for t in members)`
- `schema_data = None` if `schema` is `None`, otherwise `schema.to_val().data`


## Compact Examples

Nominal (no params, opaque):

- `Type(Nominal(ref=Ref("std.Text"), params=Const(meta=Type(Struct(fields=Tuple.EMPTY)), data=()), schema=None))`

Nominal (with params and schema):

- `Array[3]` =>
  `Type(Nominal(ref=Ref("Array"), params=Const(meta=Type(Struct(...)), data=(3,)), schema=<Struct ...>))`

Struct (record):

- `(name: Text, age: Natural)` =>
  `Type(Struct(fields=Tuple(Index(("name", "age")), (Type(Nominal(Ref("std.Text"))), Type(Nominal(Ref("std.Natural")))))))`

Function:

- `(Natural, Natural) -> Natural` =>
  `Type(Function(args=(Type(Nominal(Ref("std.Natural"))), Type(Nominal(Ref("std.Natural")))), ret=Type(Nominal(Ref("std.Natural")))))`

Union:

- `Natural | Text` =>
  `Type(Union(members=(Type(Nominal(Ref("std.Natural"))), Type(Nominal(Ref("std.Text"))))))`

Literal type:

- `Literal(3)` =>
  `Type(Literal(3))`

Type variable:

- `Type.Var("T")` =>
  `Type(Var("T"))`

Qualified:

- `Array[3] Natural` =>
  `Type(qualifiers=(Type(Nominal(Ref("Array")), params=Const(...), schema=<Type or None>),), form=Nominal(ref=Ref("std.Natural"), params=Const(...), schema=None))`

Value (nominal instance):

- `Person("john", 33)` =>
  `Const(meta=Type(Nominal(ref=Ref("Person"), params=Const(...), schema=<Struct ...>)), data=("john", 33))`

Ref:

- `Ref("std.Array")` => `Ref(segments=("std", "Array"))`

## Evaluation Phases

Phase 1: Parse

- Build the AST from source. No DOM objects are created yet.
- Example: `Array[3]` is parsed as an index/symbol expression in the AST.

Phase 2: Elaboration and Normalization

- Convert AST into canonical `Val` forms (`Const` or `Var`).
- Build `Type` and `Ref` objects.
- Attach `schema` inside `TypeForm.Nominal` (or `None` for opaque types).
- Build `Type.Nominal.params` as `Const(meta=Type(Struct), data=<primitive tuple>)`.
- Validate structural invariants (Index uniqueness, positional before nominal).
- Example: `Array[3]` becomes `Type(Nominal(ref=Ref("Array"), params=Const(...), schema=<Type or None>))`.
- Example: `Person("john", 33)` becomes `Const(meta=Type(Nominal(ref=Ref("Person"), params=Const(...), schema=<Struct ...>)), data=("john", 33))`.

Phase 3: Type Resolution and Constraints

- Resolve `Type.Var` and `Var` placeholders using constraints.
- Specialize schemas using parameter values.
- Validate qualifiers and enforce type constraints.
- Resolve overloads/dispatch using the resolved types.
- Example: `Array[W]` with `W` inferred as `3` yields a specialized schema.

Phase 4: Final Evaluation

- Evaluate runtime semantics using resolved types and schemas.
- Produce `Const` results when possible; leave residual `Var` only for
  runtime-dependent values.
- Example: arithmetic with known literals reduces to a `Const` value.

Reflection is available in any phase via `Type.to_val()` and `Ref.to_val()`.


## Open Decisions (To Iterate)

None.
