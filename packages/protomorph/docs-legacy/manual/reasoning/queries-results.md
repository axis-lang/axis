# Reasoning — Queries & Results

`Query` and `Result` are the user-facing objects. A `Query` represents a single goal against a session; a `Result` wraps the outcome and the updated session state.

---

## `Query`

```python
query = session.query(Spec.of("test.ancestor", ALICE, placeholder("Q")))
```

`Query` is immutable and memoised. Its `result` property triggers solving on first access.

### Goal canonicalisation

Before solving, the query goal is *canonicalised*: all `Placeholder` instances in the goal are replaced by typed `GoalVar` slots. This normalised form is the key used in the query table cache — two goals that differ only in variable names are considered the same query.

```python
# These two queries hit the same cache entry:
session.query(Spec.of("test.f", placeholder("X")))
session.query(Spec.of("test.f", placeholder("Y")))
```

### Semantic key

`query.semantic_key` returns the canonicalised `Spec` used as the cache key, or `None` if seed bindings conflict.

---

## `Result`

```python
result = query.result
```

| Field | Type | Meaning |
|---|---|---|
| `query` | `Query` | The query that produced this result |
| `outcome` | `SolverResult` | The actual answer (see below) |
| `next_session` | `Session \| None` | Updated session with cached table |
| `continuation` | `Query \| None` | Non-`None` if deferred and resumable |

### Resuming deferred results

```python
if result.can_continue:
    result2 = result.resume()
```

---

## `SolverResult` — the outcome hierarchy

```
SolverResult (abstract, has: goal)
├── Unique          exactly one answer
├── Ambiguous       multiple answers
├── NoSolution      proof failed
├── Deferred        blocked, waiting for more information
├── Floundered      blocked on non-ground negation (can't decide)
├── MixedCycle      cycle mixes inductive and coinductive goals
└── NegativeCycle   predicate depends negatively on itself
```

### `Unique`

```python
class Unique(SolverResult):
    subst:    frozendict[Placeholder, ReasoningValue]
    evidence: pm.Spec | None
    judgment: Judgment | None
```

The most common success case. `subst` maps every placeholder in the original query goal to its resolved value.

```python
q = placeholder("Q")
result = session.solve(Spec.of("test.parent", ALICE, q))

if isinstance(result, Unique):
    print(result.subst[q])   # the value bound to Q
```

### `Ambiguous`

```python
class Ambiguous(SolverResult):
    subst:    frozendict[...]   # bindings shared by ALL answers
    answers:  tuple[Answer, ...]
    judgments: tuple[Judgment, ...]
```

Multiple proofs exist. `subst` contains only the variables that are identical across all answers. Inspect `answers` for the full individual substitutions.

```python
if isinstance(result, Ambiguous):
    for answer in result.answers:
        print(answer.subst[q])
```

### `NoSolution`

```python
class NoSolution(SolverResult):
    reason:   str
    judgment: Judgment | None
```

No proof was found. `judgment` explains the failure tree.

### `Deferred`

```python
class Deferred(SolverResult):
    blocked:  tuple[DeferredGoal, ...]
    answers:  tuple[Answer, ...]   # partial answers so far
    judgments: tuple[Judgment, ...]
```

The query could not be fully resolved — some goals are blocked on unbound variables, pending strata, or unresolvable operators. Partial answers may already be available in `answers`.

Call `result.next_session.retry_deferred()` after adding more information to the session.

### `Floundered`

Same structure as `Deferred`, but specifically caused by a non-ground negation:

```prolog
safe(X) :- not blocked(X).
```

If `X` is unbound when `not blocked(X)` is evaluated, the result cannot be determined. The query flounders.

### `MixedCycle`

```python
class MixedCycle(SolverResult):
    cycle:    tuple[pm.Spec, ...]
    reason:   str
    trace:    CycleTrace | None
    judgment: Judgment | None
```

A cycle was detected that mixes inductive and coinductive predicates. This is typically a logic error in the rule set.

### `NegativeCycle`

A predicate depends negatively on itself — the program is not stratifiable. `cycle` lists the predicates involved.

---

## Extracting substitutions

The `subst` on `Unique` / `Ambiguous` maps the original `Placeholder` instances from the query goal to resolved `ReasoningValue`s.

```python
q = placeholder("Q")
goal = Spec.of("test.ancestor", ALICE, q)

result = session.solve(goal)
match result:
    case Unique(subst=s):
        value = s.get(q)           # ReasoningValue (usually pm.Spec or pm.Builtin)
        print(value)
    case Ambiguous(answers=answers):
        values = [a.subst[q] for a in answers]
```

`ReasoningValue` is a union type:

```python
type ReasoningValue = pm.Carrier | pm.Builtin | tuple | frozenset | bool | int | float | str | bytes | None
```

---

## `QueryTable` — the tabling structure

Each solved query is stored in a `QueryTable`:

```python
class QueryTable:
    key:                pm.Spec           # canonical goal key
    origin:             pm.Spec           # original user goal
    status:             str               # "closed" | "blocked" | "cycle"
    answers:            tuple[StoredAnswer, ...]
    deferred:           tuple[DeferredGoal, ...]
    cycle_issue:        CycleIssue | None
    closed:             bool
    active:             bool
```

Tables are stored in `session.state.tables.query_tables` and reused on subsequent queries to the same goal.

---

## API reference

::: pm.reasoning.Query

::: pm.reasoning.Result

::: pm.reasoning.SolverResult

::: pm.reasoning.Unique

::: pm.reasoning.Ambiguous

::: pm.reasoning.NoSolution

::: pm.reasoning.Deferred

::: pm.reasoning.Floundered

::: pm.reasoning.MixedCycle

::: pm.reasoning.NegativeCycle

::: pm.reasoning.QueryTable
