# Logic Design

## Purpose

This document defines the logical layer of Axis and its integration with the
entity system. The goal is to unify logical inference, type algebra, and
functional definitions in a single coherent model.


## Core Principles

- An entity acts as a predicate in a logical universe.
- Facts are explicit instances of predicates.
- Rules derive new facts and are expressed through `where`.
- The type algebra (`[]`) doubles as a logical pattern language.
- Queries are expressed by attaching `?` to a pattern.


## Syntax Roles

### Facts (Instances)

Facts are constructed with `()` and represent explicit instances.

```
Person("alice")
Parent("alice", "bob")
```

### Patterns (Type Algebra / Logical Patterns)

Patterns use `[]` and represent logical/type algebra expressions.

```
Parent[A, B]
Array[3] Natural
```

### Queries

Queries attach `?` to a pattern and ask if it is derivable in the current
context.

```
Parent[A, B]?
Add[Natural, Natural] -> Natural?
```

Query modes beyond boolean (ternary, iteration) are pending design.


## Entity Forms and Logical Meaning

### Rule (Intensional)

`def` with `where` and no `takes` defines a logical rule.

```
def grandchild[A, B]
where:
    Parent(A, X)
    Parent(X, B)
```

### Dataclass (Extensional Schema)

`def` with `takes` defines the schema of extensional facts.

```
def Person
takes:
    val name: Text
```

Instances of `Person` are explicit facts.

### Function (Logical Projection)

`def` with `takes` and `returns` defines a functional relation.

```
def Add
takes:
    val a: Number
    val b: Number
returns Number
```

The functional pattern is expressed as:

```
Add[A, B] -> C
```

This pattern is the logical view of the function without expanding arity.

### Injector

`def` with `returns` and no `takes` is an injector-like relation.

```
def Default
returns T
where:
    val T: Type
```


## Functional Projection and Queries

### Canonical Logical Form

Functional signatures normalize to the pattern form:

```
Fn(A, B) -> C
Fn[A, B] -> C
```

Both represent the same logical relation. The `->` remains part of the pattern
so the DSL does not require an explicit `Fn[A,B,C]` syntax.

### Querying Functional Relations

```
Add[Natural, Natural] -> Natural?
```

This query is true if a coherent specification exists (matching overloads and
`returns`), even if no implementation suite is present. Implementation may be
resolved later (synthesis, error, or deferred execution).


## Explicit Facts from Items

Any item may contribute explicit logical facts during collection. These facts
represent semantic relations in the language itself. For example, a future
outline keyword could report facts into a predicate such as `std.extends`.

The exact syntax is not fixed yet; this section is a placeholder for that
class of facts.


## Structural Compatibility

Similarity checks for logical patterns are strict:

- Tuple indexes must match exactly (same keys and order).
- `(x, y)` is not compatible with `(a, b)` if the keys differ.

Assignability and advanced matching are handled later during overload
resolution and are not part of the strict query check.


## Open Decisions

- Boolean vs ternary queries (`?` is boolean for now).
- Iterative queries (variables and result sets).
- Open vs closed world semantics (context dependent).
- Negative logic and stratification.
