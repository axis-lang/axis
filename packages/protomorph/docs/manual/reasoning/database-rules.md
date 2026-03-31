# Reasoning — Database & Rules

The `Database` is the knowledge source for the reasoning engine. It answers three questions: what rules exist for a given predicate, what ground facts exist, and whether a predicate is coinductive.

---

## `Database`

Abstract base class. All methods are memoised via `@flux.method` / `@flux.property` from `protobase`.

```python
class Database(Consed, abstract=True):
    anchors: frozenset[str]                              # all known predicate names
    rules_for_anchor(anchor) -> tuple[Rule, ...]         # rules whose head matches
    facts_by_anchor(anchor) -> tuple[pm.Spec, ...]       # ground facts
    is_coinductive_anchor(anchor) -> bool
    schema_for(spec) -> pm.TupleLikeType | None
    eval_logic_op(operator, *, goal, session) -> LogicOpStep | None
```

---

## `RuleSetDatabase`

The standard concrete implementation.

```python
from pm.reasoning import Rule, RuleSetDatabase
from pm import Spec, placeholder

x = placeholder("X")
y = placeholder("Y")

db = RuleSetDatabase(
    rules=(
        Rule(Spec.of("test.parent", ALICE, BOB), ()),
        Rule(Spec.of("test.ancestor", x, y), (Spec.of("test.parent", x, y),)),
        Rule(
            Spec.of("test.ancestor", x, y),
            (Spec.of("test.parent", x, placeholder("Z")),
             Spec.of("test.ancestor", placeholder("Z"), y)),
        ),
    ),
    facts=(),                                     # ground specs not wrapped in Rule
    coinductive_anchors=frozenset(),
)
```

Rules are indexed by their head anchor on construction. Lookup is O(1) for the common case.

### Coinductive predicates

```python
db = RuleSetDatabase(
    rules=stream_rules,
    coinductive_anchors=frozenset({"test.stream", "test.infinite"}),
)
```

A coinductive predicate allows its proof to be circular — a cycle is treated as a successful proof rather than an error. This enables reasoning about infinite structures.

### Logic operator evaluation

`eval_logic_op` handles two built-in operators when invoked through `RuleSetDatabase`:

| Operator | Semantics |
|---|---|
| `KeyOfOperator` | Bind result variable to the keys of a hosted spec's schema |
| `ProjectionOperator` | Bind result variable to the type of one named field |

Both defer (return `OpDeferred`) when the target contains unbound goal slots, and fail with `OpFailed` for invalid inputs.

---

## Stratification

### Why stratification?

Without stratification, negation-as-failure can be ambiguous or circular. Consider:

```prolog
p :- not q.
q :- not p.
```

Neither `p` nor `q` can be decided independently. Stratification prevents this by requiring that every negative dependency crosses a stratum boundary — lower strata are fully computed before higher strata that depend on them negatively.

### Algorithm: Tarjan's SCC + stratum assignment

**Step 1 — Dependency graph** (`build_dependency_graph`):

Scan all rules and collect positive and negative dependencies per anchor:

```
parent  →  (positive: {}, negative: {})
safe    →  (positive: {}, negative: {blocked})
blocked →  (positive: {}, negative: {})
```

**Step 2 — Strongly connected components** (`compute_sccs`):

Tarjan's algorithm[^1] identifies predicates that are mutually recursive. Each SCC becomes one node in the stratum graph.

[^1]: R. Tarjan, "Depth-first search and linear graph algorithms", *SIAM J. Comput.* 1(2), 1972.

```python
from pm.reasoning.stratify import build_dependency_graph, compute_sccs

graph = build_dependency_graph(rules)
sccs  = compute_sccs(graph)
```

**Step 3 — Stratum assignment** (`compute_stratification`):

Assign stratum 0 to all SCCs with no dependencies. For each SCC:

- Positive dependency on SCC `d` → same stratum as `d`.
- Negative dependency on SCC `d` → stratum of `d` + 1.

A **negative cycle** (negative self-dependency within an SCC) is flagged in `negative_cycle_components`.

```
parent:  stratum 0
blocked: stratum 0
safe:    stratum 1   (negatively depends on blocked at stratum 0)
```

### `StratificationPlan`

The result of stratification:

```python
from pm.reasoning import StratificationPlan

plan.stratum_of("test.safe")          # 1
plan.has_negative_cycle("test.bad")   # True if unstratifiable
plan.negative_cycle_trace("test.bad") # CycleTrace with members
```

---

## Example: querying stratified rules

```python
from pm import Spec, placeholder
from pm.reasoning import Rule, Engine, Session, RuleSetDatabase, Unique, NoSolution
from pm.reasoning import NEGATION_ANCHOR

ALICE = Spec.of("test.alice")
x     = placeholder("X")

rules = (
    Rule(Spec.of("test.blocked", ALICE), ()),
    Rule(
        Spec.of("test.safe", x),
        (Spec.of(NEGATION_ANCHOR, Spec.of("test.blocked", x)),),
    ),
)

db      = RuleSetDatabase(rules)
engine  = Engine(db)
session = Session(engine)

print(session.solve(Spec.of("test.safe", ALICE)))
# NoSolution — alice is blocked, so safe(alice) fails
```

---

## API reference

::: pm.reasoning.Database

::: pm.reasoning.RuleSetDatabase

::: pm.reasoning.DependencyGraph

::: pm.reasoning.Scc

::: pm.reasoning.StratificationPlan
