# Reasoning — Engine & Session

`Engine` and `Session` are the two runtime objects. `Engine` is static and shared; `Session` is lightweight and carries mutable state as an immutable snapshot.

---

## `Engine`

An `Engine` wraps a `Database` and pre-computes all the static information needed for reasoning:

| Property | Type | Content |
|---|---|---|
| `anchors` | `frozenset[str]` | All known predicate names |
| `rules_by_anchor` | `frozendict` | Rules indexed by head anchor |
| `facts_by_anchor` | `frozendict` | Ground facts indexed by anchor |
| `dependency_graph` | `DependencyGraph` | Positive/negative dep edges |
| `sccs` | `tuple[Scc, ...]` | Strongly connected components |
| `strata` | `StratificationPlan` | Stratum assignment per anchor |
| `global_tables` | `EngineTables` | Pre-solved stratum-0 facts |

All properties are memoised via `@flux.property` — computed once, then cached.

```python
from pm.reasoning import Engine, RuleSetDatabase

engine = Engine(RuleSetDatabase(rules))

print(engine.strata.stratum_of("test.ancestor"))   # 0 or higher
print(engine.anchors)                               # all predicate names
```

### Global tables

`engine.global_tables` pre-runs the engine on all ground facts, propagating them through stratum 0. This amortises the cost of repeated queries that share the same base facts.

### Creating sessions

```python
session = engine.session()                    # fresh session
session = engine.session(context=my_ctx)      # with custom SolveContext
```

Or directly:

```python
from pm.reasoning import Session
session = Session(engine)
```

---

## `Session`

A `Session` holds the current reasoning state: bindings, local facts, deferred goals, and query tables. It is **immutable** — every mutation returns a new `Session` instance.

```python
class Session(Consed):
    engine:  Engine
    context: SolveContext
    state:   SessionState
```

### `SessionState`

The state snapshot:

| Field | Type | Meaning |
|---|---|---|
| `bindings` | `BindingSnapshot` | Committed variable bindings |
| `local_facts` | `tuple[Spec, ...]` | Session-local ground facts |
| `deferred` | `tuple[DeferredGoal, ...]` | Blocked goals pending retry |
| `tables` | `SessionTables` | Cached query results |
| `epoch` | `int` | Monotonic change counter |
| `binding_epoch` | `int` | Counts binding changes only |
| `local_facts_epoch` | `int` | Counts local fact additions |

### Solving a goal

```python
result = session.solve(Spec.of("test.ancestor", ALICE, q))
# returns a SolverResult (Unique, Ambiguous, NoSolution, ...)
```

`solve` is equivalent to `session.query(goal).result.outcome`.

### Session mutations

All mutations return a **new** `Session`; the original is unchanged (persistent data structures):

```python
# Add bindings discovered by previous queries
session2 = session.with_bindings({q: CAROL})

# Add session-local facts (not in the database)
session3 = session.with_local_facts(Spec.of("test.extra", ALICE))

# Add deferred goals to retry later
session4 = session.with_deferred(deferred_goals)

# Retry all deferred goals (wake conditions permitting)
session5 = session.retry_deferred()

# Remove a cached query (forces re-evaluation)
session6 = session.without_goal(goal_key)
```

### Tabling and query caching

When `session.query(goal)` is called, the engine checks the session's `QueryTable` cache first. If a table for the canonicalised goal exists, its stored answers are returned immediately without re-running the solver.

A table is **closed** when all answers have been found. It stays **open** (active) if deferred goals are pending — these are retried on wake conditions.

---

## Coinduction in practice

Marking a predicate as coinductive allows cyclic proofs:

```python
from pm.reasoning import Rule, Engine, Session, RuleSetDatabase, Unique, MixedCycle
from pm import Spec, placeholder

x = placeholder("X")

# A stream is infinite: stream(X) :- stream(X).
rules = (
    Rule(Spec.of("test.stream", x), (Spec.of("test.stream", x),)),
)

db_normal = RuleSetDatabase(rules)
db_co     = RuleSetDatabase(rules, coinductive_anchors=frozenset({"test.stream"}))

A = Spec.of("test.a")

# Without coinduction: cycle is an error
result_normal = Session(Engine(db_normal)).solve(Spec.of("test.stream", A))
print(type(result_normal).__name__)    # MixedCycle or NoSolution

# With coinduction: cycle succeeds
result_co = Session(Engine(db_co)).solve(Spec.of("test.stream", A))
print(type(result_co).__name__)        # Unique
```

---

## Multi-step query workflow

For complex queries that may defer, the recommended pattern is:

```python
query  = session.query(goal)
result = query.result

match result.outcome:
    case Unique(subst=s):
        print("solved:", s)
    case Deferred():
        # Add new information and retry
        updated_session = result.next_session.with_local_facts(new_fact)
        result2 = updated_session.query(goal).result
    case NoSolution():
        print("no solution")
```

`result.next_session` always carries the updated session (with the query table stored). `result.continuation` is set when a deferred result may be resumable.

---

## API reference

::: pm.reasoning.Engine

::: pm.reasoning.Session

::: pm.reasoning.SessionState

::: pm.reasoning.SolveContext
