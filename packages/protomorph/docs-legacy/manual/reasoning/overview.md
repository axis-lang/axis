# Reasoning — Overview

The `pm.reasoning` module is a full logic programming engine built on top of Protomorph's type algebra. It extends the basic unification layer with:

- **Datalog-style stratification** — correct semantics for negation-as-failure.
- **Tabling / memoisation** — answers to goals are cached; recursive queries terminate.
- **Coinduction** — rules may be declared coinductive, enabling circular proofs.
- **Evidence tracking** — every answer carries a `Judgment` explaining how it was derived.
- **Cycle detection** — mixed and negative cycles are reported, not silently looped.

---

## Conceptual model

The reasoning engine is modelled after **SLD resolution** (the basis of Prolog) extended with Datalog-like strata and tabling from **XSB** / **SLG resolution** (Swift & Warren, 2012)[^1].

[^1]: T. Swift and D. S. Warren, "XSB: Extending Prolog with Tabled Logic Programming", *TPLP* 12(1-2), 2012.

### Facts and rules

A **fact** is a rule with an empty body — it holds unconditionally:

```python
from pm.reasoning import Rule
from pm import Spec

Rule(Spec.of("test.parent", ALICE, BOB), ())   # parent(alice, bob).
```

A **rule** has a head and a body — the head holds when all body goals hold:

```python
x, y, z = placeholder("X"), placeholder("Y"), placeholder("Z")

Rule(
    Spec.of("test.ancestor", x, y),        # ancestor(X, Y) :-
    (
        Spec.of("test.parent", x, z),       #   parent(X, Z),
        Spec.of("test.ancestor", z, y),     #   ancestor(Z, Y).
    ),
)
```

Negation is expressed by wrapping a goal in `std.logic.Not`:

```python
from pm.reasoning import is_negation, NEGATION_ANCHOR

not_blocked = Spec.of(NEGATION_ANCHOR, Spec.of("test.blocked", x))
```

### Stratification

Stratification partitions predicates into ordered *strata* such that no predicate depends negatively on itself (directly or transitively). This ensures that negation-as-failure has a well-defined meaning.

```
stratum 0: parent, blocked     (base facts, no negative deps)
stratum 1: safe                (depends negatively on blocked → resolved after stratum 0)
```

The engine computes strata via strongly connected component analysis on the dependency graph. A **negative cycle** (predicate depends negatively on itself) is a hard error.

### Tabling

Tabling stores intermediate answers so that recursive queries do not loop. When a goal is encountered that is already being computed (an active goal), the engine returns the answers accumulated so far and schedules a wake-up when new answers arrive.

This implements the **SLG** semantics: complete for all Datalog programs and for many Prolog programs.

### Coinduction

Some predicates model infinite structures (streams, corecursive types). Marking a predicate as *coinductive* allows a cycle to be treated as a successful proof rather than an error:

```python
from pm.reasoning import RuleSetDatabase

db = RuleSetDatabase(rules, coinductive_anchors=frozenset({"test.stream"}))
```

---

## Architecture

```
Engine          ← static: database + stratification plan + tabling config
  └── Session   ← per-query state: bindings, local facts, epoch counter
        └── Query    ← single goal execution
              └── QueryCore / SessionSolveCore / EngineSolveCore
```

A single `Engine` is shared across many `Session`s. A `Session` is lightweight and can be created per request.

---

## Quick example

```python
from pm import Spec, placeholder
from pm.reasoning import Rule, Engine, Session, RuleSetDatabase, Unique, Ambiguous

ALICE = Spec.of("test.alice")
BOB   = Spec.of("test.bob")
CAROL = Spec.of("test.carol")
x, y  = placeholder("X"), placeholder("Y")

rules = (
    Rule(Spec.of("test.parent", ALICE, BOB),   ()),
    Rule(Spec.of("test.parent", BOB,   CAROL), ()),
    Rule(
        Spec.of("test.ancestor", x, y),
        (Spec.of("test.parent", x, y),),
    ),
    Rule(
        Spec.of("test.ancestor", x, y),
        (Spec.of("test.parent", x, placeholder("Z")),
         Spec.of("test.ancestor", placeholder("Z"), y)),
    ),
)

engine  = Engine(RuleSetDatabase(rules))
session = Session(engine)

q = placeholder("Q")
result = session.solve(Spec.of("test.ancestor", ALICE, q))

match result:
    case Unique(subst=s):
        print(s[q])    # test.carol  (transitive ancestor)
    case Ambiguous(answers=ans):
        print([a.subst[q] for a in ans])
```

---

## Section map

| Page | Contents |
|---|---|
| [Model & Variables](model-vars.md) | `Rule`, `Answer`, `Judgment`, variable types |
| [Database & Rules](database-rules.md) | `Database`, `RuleSetDatabase`, stratification |
| [Engine & Session](engine-session.md) | `Engine`, `Session`, tabling, coinduction |
| [Queries & Results](queries-results.md) | `Query`, result types, substitution extraction |
