# Quick Start

This page walks through three self-contained examples that cover the core ideas of Protomorph: defining types, wrapping values into carriers, unifying terms, and querying a rule set.

## 1 — Types and carriers

Every value in Protomorph is held in a *carrier* — a typed wrapper produced by a `Type` descriptor.

```python
import pm

# A nominal type: integer
int_type = pm.Spec.of("std.types.Integer")

# A heterogeneous tuple type: (int, int)
pair_type = pm.VaryingType.of(int_type, int_type)

# Wrap a concrete pair
carrier = pair_type.make((3, 5))

print(list(carrier))           # [<LeafCarrier 3>, <LeafCarrier 5>]
print(carrier[0].content)      # 3
```

## 2 — Unification

`unify` performs structural Robinson unification on two carrier trees.
Variables (`Placeholder`) get bound; concrete values must match.

```python
from pm import placeholder, unify, wrap, Spec

# Two logic variables
x = placeholder("X")
y = placeholder("Y")

# Goal: unify f(X, b) with f(a, Y)
f_xy = Spec.of("test.f", x, y)
f_ab = Spec.of("test.f", Spec.of("test.a"), Spec.of("test.b"))

result = unify(
    wrap(f_xy),
    wrap(f_ab),
    is_var=lambda c: isinstance(c.content, pm.Placeholder),
)

print(result)   # test.f(test.a, test.b)  — X→a, Y→b substituted
```

## 3 — Reasoning engine

Define rules, build a `Session`, and query it.

```python
from pm import Spec, placeholder
from pm.reasoning import Rule, Engine, Session, RuleSetDatabase, Unique

ALICE = Spec.of("test.alice")
BOB   = Spec.of("test.bob")
X     = placeholder("X")
Y     = placeholder("Y")

rules = (
    # parent(alice, bob).
    Rule(Spec.of("test.parent", ALICE, BOB), ()),
    # ancestor(X, Y) :- parent(X, Y).
    Rule(Spec.of("test.ancestor", X, Y), (Spec.of("test.parent", X, Y),)),
    # ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
    Rule(
        Spec.of("test.ancestor", X, Y),
        (
            Spec.of("test.parent", X, placeholder("Z")),
            Spec.of("test.ancestor", placeholder("Z"), Y),
        ),
    ),
)

engine  = Engine(RuleSetDatabase(rules))
session = Session(engine)

q = placeholder("Q")
result = session.solve(Spec.of("test.ancestor", ALICE, q))

print(type(result).__name__)    # Unique  (or Ambiguous if multiple answers)
if isinstance(result, Unique):
    print(result.subst[q])      # test.bob
```

## What's next?

- Read the [Manual](../manual/layer-0-foundation.md) to understand each layer in depth.
- Explore the [Notebooks](../notebooks/types-and-carriers.html) for interactive examples.
- Consult the [API Reference](../reference/pm.md) for every public symbol.
