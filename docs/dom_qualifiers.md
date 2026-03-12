# DOM Qualifiers and Type-Value Algebra

## Purpose

This document specifies the formal role of DOM qualifiers, the status of types
as first-class values, and the contract between the DOM layer and the semantic
layer for projection, lifting, and type combination.

The goal is to make operations over values and operations over types share the
same algebraic surface, while keeping domain-specific semantic rules outside of
DOM itself.

## Scope

This document covers:

- the representation of qualified types such as `Map[str] T`, `Array[S] T`, or
  `Future T`
- the interpretation of `dom.Type` as a first-class value
- the laws that relate value-level operations and type-level operations
- the role of `Introspector` as the semantic interface used by DOM

This document does not define:

- the complete operational semantics of `Apply`, `Member`, or binary operators
- array broadcasting rules
- overload resolution
- runtime evaluation strategy for asynchronous, container, or collection values

Those concerns belong to the semantic layer. DOM only provides the common
surface needed to express them uniformly over values and over types.

## Core Model

### Values

`dom.Val` is the canonical zipper pair:

- `type: dom.Type`
- `data: dom.Data`

All DOM values, including type values, inhabit this shape.

### Types as Values

A type is a first-class value when it appears in the data position of a DOM
value.

Formally, a type value is a value `v: dom.Val` such that:

- `v.type.is_meta` is `True`
- `v.data` is, or decodes to, a `dom.Type`

Examples:

- `dom.val(int)`
- `dom.val(Person)`
- `dom.val(frozendict[str, str])`

The API `Val.wrap(data)` is defined precisely for this case. It interprets the
receiver as a type value and delegates to the wrapped `dom.Type`.

### Qualifiers

A qualifier is a type constructor of the form `Q[T]` that preserves an
underlying type `T` while adding structure, context, or interpretation.

In DOM, the canonical representation is `dom.Qualifier`, with
`dom.NominalQualifier` as the concrete nominal form:

- `spec_ref`: qualifier metadata such as `Map[K=Text]`
- `underlying`: the wrapped type

Examples:

- `Map[str] Integer`
- `Array[2, 2] Integer`
- `Future T`

DOM does not assign concrete semantic rules to a qualifier anchor. It only
represents the qualified type.

## Separation of Concerns

### DOM Responsibilities

DOM is responsible for:

- representing values and types uniformly
- exposing first-class type values
- supporting structural inspection primitives
- delegating semantic qualifier behavior through `Introspector`

DOM is not responsible for:

- deciding array broadcasting
- choosing overloads
- deciding whether a qualifier supports projection, lifting, or combination
- defining arithmetic or callable semantics for specific language constructs

### Semantic Layer Responsibilities

The semantic layer is responsible for:

- deciding whether an expression is valid
- computing result types of projections, function application, and operators
- defining qualifier-specific laws such as broadcasting or shape compatibility
- installing an `Introspector` implementation that DOM can query

## Introspector as Semantic Interface

`Introspector` is the formal boundary between DOM and semantic interpretation.

In addition to structural introspection already present in DOM, the interface is
expected to grow with type-level operations such as:

- `project(type, key) -> type`
- `lift(qualifier, result) -> type`
- `combine(left, right, op) -> type`

The intended meaning is the following.

### `project`

`project(T, k)` returns the type of member or component `k` projected from `T`.

Examples:

- `project(Person[bytes], "name") = Text`
- `project(Map[str] Person[bytes], "name") = Map[str] Text`
- `project(Map[str] Person[bytes], "items") = Map[str] Map[str] bytes`

### `lift`

`lift(Q[T], R)` lifts a result type `R` through a qualifier context `Q`.

Examples:

- `lift(Map[str] _, (str, str)) = Map[str] (str, str)`
- `lift(Future _, Number) = Future Number`

### `combine`

`combine(A, B, op)` returns the result type of a binary combination performed
at the type level.

DOM does not define the semantic rules of combination. For example, the
semantic layer may decide that:

- `combine(Array[A] Integer, Array[B] Integer, "*")` applies broadcasting and
  returns another qualified type
- `combine(Map[K] Integer, Map[K] Integer, "+")` preserves `Map[K]`

The DOM contract is only that such a result can be represented as a `dom.Type`
and lifted back into a value when needed.

## Value-Level and Type-Level Correspondence

The guiding principle is that DOM should support the same algebraic surface on
values and on types-as-values.

Let `op` be an operation that is semantically defined both over values and over
types. Then the expected correspondence law is:

```text
type_of(op(val(a), val(b))) = op(type_of(val(a)), type_of(val(b)))
```

Equivalently, when types are lifted into values:

```text
val(type_of(a)) op val(type_of(b)) = type_of(val(a) op val(b))
```

This law is the reason DOM must support first-class type values and why the
semantic surface is expressed through `Introspector` rather than through
ad-hoc special cases.

## Projection Law for Qualifiers

If a qualifier `Q` supports transitive structural projection, the expected law
is:

```text
project(Q[T], k) = lift(Q[T], project(T, k))
```

This law captures expressions such as:

```python
class Person[T](Builtin):
    name: str
    items: frozendict[str, T]
```

For:

```text
collection: Map[str] Person[bytes]
```

the following projections hold:

- `collection.name : Map[str] str`
- `collection.items : Map[str] Map[str] bytes`

The qualifier remains outside the projected member type.

## Lifting Law for Functions

If a qualifier `Q` supports transitive function lifting, then for a function
`f: T -> R` the expected law is:

```text
f(Q[T]) : Q[R]
```

Equivalently in type-level form:

```text
lift(Q[T], R) = Q[R]
```

Example:

```text
splitname: str -> (str, str)
splitname(collection.name) : Map[str] (str, str)
```

DOM does not prove or enforce the validity of the call. It only requires that
the semantic layer be able to map the result type through the qualifier.

## Combination Law for Qualified Operands

If a qualifier supports binary combination, the semantic layer may define a law
of the form:

```text
combine(Q[T], Q[U], op) = Q[R]
```

where `R` is the semantic result of combining `T` and `U` under `op`.

For example:

```text
a: Array[2,2] Integer
b: Array[2,2] Integer
```

may satisfy:

- `a + b : Array[2,2] Integer`
- `a * b : Array[2,2] Integer`

However, the broadcasting rule that makes this valid is not part of DOM. The
semantic layer computes the resulting type. DOM only needs to represent it.

## Meta-Types and Qualifier Propagation

DOM supports type values through meta-types.

A value is a valid type value when its outer type is meta and its data resolves
to a `dom.Type`.

For qualifiers, meta-ness propagates through the underlying type:

```text
is_meta(Q[T]) = is_meta(T)
```

This allows constructions such as:

- `dom.val(frozendict[str, str]).wrap(...)`
- `dom.val(Future[Person]).wrap(...)`

provided that the wrapped data is a semantic inhabitant of the underlying
qualified type.

## Consequences for DOM API Design

The DOM API should expose operations that work uniformly for:

- ordinary values
- type values

This suggests public helpers that can operate on `dom.Val` while consulting the
active `Introspector` for type-level meaning.

Typical examples are:

- value projection
- result lifting
- binary combination

These helpers should not encode language-specific semantics directly. Their role
is to bridge:

- `dom.Val` and `dom.Type`
- value plane and type plane
- DOM structure and semantic interpretation

## Non-Goals

This model does not imply that every qualifier supports every operation.

In particular:

- some qualifiers may support projection but not binary combination
- some qualifiers may support lifting but not structural projection
- some qualifiers may require semantic side conditions that DOM does not know

The `Introspector` implementation decides which operations are valid and which
must fail with an explicit error.

## Summary

The intended architecture is:

- DOM represents values, types, and qualifiers uniformly
- types are first-class values in DOM
- DOM does not encode semantic rules such as broadcasting
- `Introspector` is the formal semantic interface used by DOM
- projection, lifting, and combination are defined first in the type plane
- value-level operations should correspond to type-level operations under
  `type_of`

This gives Axis a single algebraic framework for values and types while keeping
semantic policy outside of DOM itself.
