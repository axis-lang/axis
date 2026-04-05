# Reasoning — Model & Variables

This page covers the data structures that represent the *what* of reasoning: rules, answers, proof terms, and the specialised variable types the engine uses internally.

---

## Rules

### `Rule`

```python
class Rule(Builtin):
    head: pm.Spec
    body: tuple[pm.Spec, ...] = ()
```

A rule states that `head` holds when every goal in `body` holds.

- An empty `body` is a **fact** — it holds unconditionally.
- Negative goals are wrapped with `Spec.of(NEGATION_ANCHOR, goal)`.

```python
from pm.reasoning import Rule, NEGATION_ANCHOR
from pm import Spec, placeholder

x = placeholder("X")

# Fact: parent(alice, bob).
fact = Rule(Spec.of("test.parent", ALICE, BOB), ())

# Rule: safe(X) :- not blocked(X).
safe_rule = Rule(
    Spec.of("test.safe", x),
    (Spec.of(NEGATION_ANCHOR, Spec.of("test.blocked", x)),),
)
```

Convenience properties:

```python
rule.positive_goals   # body goals that are not negated
rule.negative_goals   # body goals after unwrapping negation
```

### Negation helpers

```python
from pm.reasoning import is_negation, unwrap_negation, NEGATION_ANCHOR

is_negation(Spec.of(NEGATION_ANCHOR, g))   # True
unwrap_negation(Spec.of(NEGATION_ANCHOR, g))  # → g
```

---

## Answers and proof terms

### `Answer`

```python
class Answer(Builtin):
    goal:     pm.Spec
    subst:    frozendict[pm.Placeholder, ReasoningValue]
    evidence: pm.Spec | None
    judgment: Judgment | None
```

An `Answer` is one solution to a query goal. `subst` maps query-level placeholders to their resolved values. `judgment` carries the full proof derivation.

### `Judgment`

```python
class Judgment(Builtin):
    rel:          pm.Spec
    evidence:     pm.Spec | None
    subjudgments: tuple[Judgment, ...]
    trace:        CycleTrace | None
```

A `Judgment` is a proof tree. Each node records the relation that was proved, optional evidence (the rule head that matched), and sub-proofs for the body goals.

---

## Deferred goals and blockers

When a goal cannot be resolved immediately, it becomes a `DeferredGoal` paired with a `Blocker` that explains why.

### `Blocker` hierarchy

```
Blocker (abstract)
├── StratumPending       waiting for a lower stratum to close
├── NonGroundNegation    negated goal has unbound variables → cannot decide
├── OperatorPending      logic operator needs more information
├── ProjectionBlocked    type projection needs more input
├── TypeFunctionBlocked  type function needs more input
└── ImplSelectionBlocked trait implementation selection blocked
```

### `WakeCondition` hierarchy

Each blocker has a set of wake conditions — events that may allow it to be retried:

```
WakeCondition (abstract)
├── BindingsChanged      new variable bindings made
├── LocalFactsChanged    new facts added to the session
├── StratumClosed        a stratum completed
└── OperatorRetriable    an operator can be retried
```

`default_wake_on(blocker)` returns the standard wake conditions for each blocker type:

```python
from pm.reasoning import default_wake_on, NonGroundNegation, Spec

blocker = NonGroundNegation(blocked_on=Spec.of("test.p", placeholder("X")))
print(default_wake_on(blocker))
# (BindingsChanged(),)
```

### `DeferredGoal`

```python
class DeferredGoal(Builtin):
    goal:             pm.Spec
    blocker:          Blocker
    evidence:         pm.Spec | None
    wake_on:          tuple[WakeCondition, ...]
    judgment:         Judgment | None
```

---

## Cycle structures

### `CycleMember`

One node in a detected cycle.

```python
class CycleMember(Builtin):
    goal:          pm.Spec
    coinductive:   bool   # is this goal in a coinductive predicate?
    via_negation:  bool   # is the edge to this member a negative dependency?
```

### `CycleTrace`

A full description of a detected cycle.

```python
class CycleTrace(Builtin):
    members:              tuple[CycleMember, ...]
    kind:                 str    # "negative" | "mixed" | ""
    reason:               str
    closes_via_negation:  bool
```

### `CycleIssue`

Abstract base for cycle errors. Two concrete forms:

| Class | Meaning |
|---|---|
| `NegativeCycleIssue` | A predicate depends negatively on itself — unstratifiable |
| `MixedCycleIssue` | A cycle mixes inductive and coinductive goals |

---

## Variables

The engine uses a family of specialised `Var` subclasses to track the *origin* of every variable — which rule it came from, which application of that rule, and so on. This enables precise error messages and prevents variable clashes across rule applications.

### Variable hierarchy

```
pm.Var (abstract)
└── ReasoningVar (abstract)
    ├── QueryVar(ctx: QueryCtx, slot: int)      variables in the user's query
    ├── RuleVar(ctx: RuleCtx, slot: int)        variables in a rule template
    ├── RuleAppVar(ctx: RuleAppCtx, slot: int)  freshened copy per rule application
    ├── GoalVar(ctx: GoalCtx, slot: int)        canonical goal slot parameters
    └── BranchVar(ctx: BranchCtx, slot: int)   deferred branch variables
```

### Context types

| Context | Fields | Purpose |
|---|---|---|
| `QueryCtx` | `skeleton, public_placeholders, source_names` | User-visible query shape |
| `RuleCtx` | `origin_rule, template_key, source_names` | Compiled rule template |
| `RuleAppCtx` | `parent_goal, rule_ctx, app_serial` | One application of a rule |
| `GoalCtx` | `skeleton` | Canonical goal parameter slots |
| `BranchCtx` | `blocked_goal, remaining_goals` | Deferred branch state |

### Why so many variable types?

Different variable types serve different lifetime guarantees:

- `RuleVar` variables exist in the *template* and are **never directly unified**.
- `RuleAppVar` variables are created **fresh per application** (unique `app_serial`) so two applications of the same rule cannot share bindings.
- `QueryVar` variables are the ones the user gets back in `result.subst`.
- `GoalVar` variables canonicalise the parameters of a tabled goal so cache lookups work correctly.

### `EqClassInfo`

Metadata attached to a `UnionFind` equivalence class to track the origins of the variables in that class:

```python
class EqClassInfo(Builtin):
    origins:      frozenset[pm.Var]
    source_names: frozenset[str]
```

---

## API reference

::: pm.reasoning.Rule

::: pm.reasoning.Answer

::: pm.reasoning.Judgment

::: pm.reasoning.Blocker

::: pm.reasoning.StratumPending

::: pm.reasoning.NonGroundNegation

::: pm.reasoning.OperatorPending

::: pm.reasoning.DeferredGoal

::: pm.reasoning.WakeCondition

::: pm.reasoning.default_wake_on

::: pm.reasoning.CycleMember

::: pm.reasoning.CycleTrace

::: pm.reasoning.CycleIssue

::: pm.reasoning.QueryVar

::: pm.reasoning.RuleVar

::: pm.reasoning.RuleAppVar

::: pm.reasoning.EqClassInfo
