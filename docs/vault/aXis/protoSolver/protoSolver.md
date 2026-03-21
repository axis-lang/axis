_\<Thinking\>_
Now I have a very clear picture of:

1. **protomorph**: The algebra layer with `Subst`, `unify`, `satisfies`, `Var`, `Type`, `MatchTree`, `MatchEnv`, etc.
2. **axis.sem**: The semantic layer with `Constraint`, `Entity`, `OverloadIndex`, `SpecVar`, `ParamVar`, claims, etc.
3. **What's missing**: Regional inference, shared substitution, deferred obligations, candidate sets, bidirectional propagation.

Now I need to design the protosolver package. The key design decisions:

1. **No dependencies** for now -- must be self-contained. Later can depend on protomorph.
2. It should implement the core solver concepts from the document:
   - Inference variables (meta-variables)
   - Shared substitution store (mutable/incremental, unlike protomorph's immutable `Subst`)
   - Constraints that can `solve(value, subst) -> subst*`
   - Candidate sets
   - Worklist / deferred obligations
   - InferRegion

Since we're building without dependencies, I need to think about what the core abstractions look like independent of protomorph's type system.

Let me design the plan:

### Core abstractions for protosolver

The solver is essentially a constraint propagation engine. The key abstractions:

1. **InferVar** -- An inference/meta variable. Has an identity, optional bounds, and a current state (unresolved, resolved to a value, etc.)

2. **Substitution** -- A mutable (or persistent) mapping from InferVar to values. Uses union-find for efficient resolution chains.

3. **Constraint** -- An obligation that can be:
   - Solved immediately (reducing the substitution)
   - Deferred (when not enough info yet)
   - Failed (incompatible)

4. **CandidateSet** -- For a call site, the set of live candidates. Each candidate has constraints that may eliminate it.

5. **InferRegion** -- The top-level container: vars, substitution, constraints worklist, candidate sets, diagnostics.

6. **Solver loop** -- Worklist-based: pick a constraint, try to solve it, propagate new info, repeat until fixpoint or failure.

Since we're dependency-free, I need to think about what "values" and "types" look like. The solver should be parametric over the actual type/value representation -- it just needs to know how to unify things.

Let me think about this more concretely...

### Design approach

The solver should be **generic** over the domain. It needs:
- A way to create inference variables
- A way to unify two terms (producing bindings)
- A way to apply substitutions
- A way to check if a constraint is satisfiable

This suggests the solver should define:

1. **Term algebra** -- A minimal term representation (or a protocol that external types can implement)
2. **Union-Find substitution** -- Efficient, mutable
3. **Constraint types** -- Eq, Conforms, Choice (disjunction for overloads)
4. **Propagation engine** -- Worklist-based

Actually, looking at the document again, the solver needs to be quite specific to the domain. Let me re-read the key parts...

The document says:
- Move from `constraint.satisfies(value) -> bool` to `constraint.solve(value, subst) -> subst*`
- The solver works on inference variables (`?T`, `?K`, `?V`)
- It manages candidate sets (overload choices)
- It has a worklist for deferred constraints

I think the right approach is:

1. **A minimal term/type representation** -- just enough to represent variables, constructors with args, and ground types. This can later be mapped to/from protomorph's `Val`/`Type`.

2. **Union-Find based substitution** -- mutable, supports path compression, occurrence checks.

3. **Constraint types**:
   - `Unify(a, b)` -- unify two terms
   - `Conforms(actual, expected)` -- satisfiability check
   - `Choice(var, candidates)` -- overload selection, where each candidate is a set of constraints
   - `Deferred(constraint, deps)` -- wait until deps are resolved

4. **InferRegion** -- the orchestrator

Let me propose a more concrete module structure:

```
src/protosolver/
├── __init__.py
├── term.py          # Term algebra: Var, App, Ground
├── subst.py         # Union-Find substitution store
├── constraint.py    # Constraint types: Eq, Conforms, Choice
├── region.py        # InferRegion: the solver context
├── solver.py        # Worklist-based solving loop
└── diagnostic.py    # Error/ambiguity reporting
```

Actually, let me think about whether we need our own term algebra or if we should be parametric...

Given the goal of "sin dependencias por ahora, luego depender de protomorph", I think we should:

1. Define a minimal, self-contained term algebra that mirrors the key concepts (variables, application/construction, ground values)
2. Make the solver work on this algebra
3. Later, either bridge to protomorph or replace the term representation

Let me think about the module breakdown more carefully:

### Modules

1. **`term.py`** -- The term language
   - `Term` -- base
   - `MetaVar` -- inference variable (has identity, level/scope)
   - `Constructor(name, args: tuple[Term, ...])` -- type constructor application (like `HashMap[K, V]`)
   - `Ground(value)` -- concrete type/value with no variables

2. **`subst.py`** -- Substitution store
   - `SubstStore` -- mutable union-find mapping MetaVar -> Term
   - `walk(term)` -- chase bindings to canonical form
   - `unify(a, b)` -- first-order unification, returns success/failure
   - `occurs_in(var, term)` -- occurs check

3. **`constraint.py`** -- Constraint definitions
   - `Constraint` -- base
   - `Eq(left, right)` -- unification constraint
   - `Conforms(actual, expected)` -- satisfiability (for now same as Eq, extensible)
   - `Overload(target, candidates)` -- disjunctive choice

4. **`candidate.py`** -- Candidate representation
   - `Candidate` -- a partially resolved overload candidate
   - `CandidateSet` -- live candidates for a call site

5. **`region.py`** -- The inference region
   - `InferRegion` -- top-level container
   - Fresh var generation
   - Constraint registration
   - Candidate set management

6. **`solver.py`** -- The solving engine
   - Worklist loop
   - Propagation
   - Fixpoint detection
   - Commitment

7. **`diagnostic.py`** -- Error types
   - `SolverError`
   - `Ambiguity`
   - `Unsatisfiable`

Hmm, this is getting complex. Let me simplify based on the document's "first scope":

> La primera version del solver regional no necesita resolver todo.
> Debe cubrir primero:
> - especializacion inferida desde argumentos de llamada
> - reutilizacion de sustituciones entre constraints de un mismo overload
> - propagacion simple desde resultado esperado
> - defaults diferidos en contextos cerrados y locales

So the first version needs:
1. Inference vars
2. Unification
3. Shared substitution
4. Constraints that produce new bindings (not just bool)
5. Basic worklist for deferred constraints
6. Candidate sets (basic overload tracking)

Let me design a plan that's pragmatic. I'll propose the architecture to the user.

Let me think about the question of "generic vs specific"...

I think the right approach is to make the solver work with an abstract `Term` protocol, so it's independent of protomorph but can be easily adapted. The term algebra should be:

- **Minimal**: just what the solver needs
- **Hashable and immutable**: for use as dict keys and in sets  
- **Structural**: supports recursive traversal

Actually, for a constraint solver that's independent, I think we should go with a concrete but simple term representation. Using dataclasses or similar lightweight Python classes. No need for protobase's Inmutable/Consed machinery since we're dependency-free.

Let me draft the plan now.

### Plan

```
packages/protosolver/
├── src/protosolver/
│   ├── __init__.py      # Public API re-exports
│   ├── term.py          # Term algebra
│   ├── unify.py         # Unification + substitution store  
│   ├── constraint.py    # Constraint types
│   ├── candidate.py     # Candidate sets for overload selection
│   ├── region.py        # InferRegion
│   └── solver.py        # Worklist-based solving loop
└── tests/
    ├── test_term.py
    ├── test_unify.py
    ├── test_constraint.py
    ├── test_candidate.py
    └── test_solver.py     # Integration: regional solving
```

Let me present this to the user for discussion.

Actually, I should think more carefully about what the term representation looks like. The document talks about:
- Types like `HashMap[K, Vec[V]]`, `MutRef[Vec[T]]`, `Entry[K, V]`, `Text`, `Sym`, `Unit`, `Key`
- Inference variables `?K`, `?V`, `?T_seed`, etc.
- Ground types like `Text`, `Sym`

So the term algebra needs:
- **MetaVar**: `?K`, `?V`, etc. -- unification variables
- **Con(name, args)**: type constructor application, e.g. `HashMap(?K, Vec(?V))`
- Constants are just `Con(name, ())` with no args

This is essentially first-order terms, which is the classic unification domain.

For the substitution store, union-find is the standard approach. We need:
- `fresh()` -- create new metavar
- `bind(var, term)` -- add binding
- `walk(term)` -- resolve to canonical form
- `unify(a, b)` -- Robinson's algorithm with occurs check
- `apply(term)` -- deep substitution (walk + recursive apply on args)

For constraints:
- `Eq(a, b)` -- `a` must unify with `b`
- `Conforms(actual, expected)` -- for now equivalent to Eq, but extensible for subtyping later
- `Overload(result_var, candidates)` -- each candidate is a list of constraints + a result term. The solver must pick exactly one candidate whose constraints are all satisfiable.

For the worklist:
- Pending constraints that become solvable when their variables get bound
- Variable watchers: when a var gets bound, re-enqueue constraints that mention it

OK, I think I have a solid plan. Let me present it.

Wait, let me also think about whether to use union-find or persistent/immutable substitutions...

The document's examples suggest backtracking might be needed (trying different overload candidates). Union-find is great for forward propagation but awkward for backtracking. An immutable substitution (like protomorph's `Subst`) is better for backtracking but slower for large chains.

Options:
1. **Mutable union-find** with a trail for undo (classic Prolog approach)
2. **Immutable/persistent substitution** (functional approach, like protomorph's `Subst`)
3. **Hybrid**: union-find for the main store, snapshot/restore for backtracking

For the first implementation, I think **immutable substitution with trail** or a simple **dict-based substitution** with copy-on-backtrack is fine. Performance isn't the concern yet -- correctness and clarity are.

Actually, I think the simplest correct approach is:
- Use a plain `dict[MetaVar, Term]` as the substitution
- `walk` chases chains
- For overload resolution, try each candidate with a copy of the substitution and see which ones succeed
- Use occurrence-based watchlists for the worklist

Let me finalize the plan.

I also want to think about the Candidate/CandidateSet design more carefully.

From the document:
> Cada candidata necesita, al menos:
> - contribution objetivo
> - entorno capturado por MatchTree
> - sustitucion local/compartida actual
> - especializacion parcial inferida
> - constraints pendientes propias

In our dependency-free version, a Candidate would be:
```python
@dataclass
class Candidate:
    id: str                          # label/name for debugging
    constraints: list[Constraint]    # what must hold for this candidate
    bindings: dict[str, Term]        # captured env (from MatchTree equivalent)
    result: Term                     # the result term if this candidate is chosen
```

A CandidateSet:
```python
@dataclass 
class CandidateSet:
    target: MetaVar                  # the variable that gets bound to the chosen result
    candidates: list[Candidate]      # alive candidates
```

When a candidate's constraints all succeed, we commit to it and unify `target` with its `result`.

When some constraints fail, we prune that candidate.

When only one candidate survives, we commit.

When zero survive, error.

When multiple survive and no more propagation is possible, ambiguity.

OK, I think the plan is solid. Let me present it to the user.

Let me think about one more thing: the solver loop.

```
1. Initialize region with all call sites and their candidate sets
2. Seed constraints from annotations and argument types
3. While worklist is not empty:
   a. Pick a constraint
   b. Try to solve it:
      - Eq(a, b): unify a and b, propagate new bindings
      - Overload(target, candidates): 
        - For each alive candidate, check if its constraints are now satisfiable/unsatisfiable
        - Prune impossible candidates
        - If one remains, commit
   c. If new bindings were produced, re-enqueue constraints watching those variables
4. Check for unsolved variables / ambiguities
5. Return the final substitution + overload commitments
```

OK, I think I have enough to present a comprehensive plan. Let me write it up.
</thinking>

Excelente. Tengo una imagen completa del estado actual y del gap. Voy a proponer un plan concreto para la implementación.

---

## Plan: `protosolver` -- Constraint solver regional autocontenido

### Premisa

Un solver de constraints de primer orden con soporte para variables de inferencia, unificación, candidate sets (para overloads), y un worklist de obligaciones diferidas. Sin dependencias externas. Luego se puede bridgear a protomorph reemplazando la representación de términos.

### Módulos propuestos

```
src/protosolver/
├── __init__.py        # API pública
├── term.py            # Álgebra de términos
├── unify.py           # Unificación + store de sustituciones
├── constraint.py      # Tipos de constraint
├── candidate.py       # Candidate sets para overload selection
├── region.py          # InferRegion: contexto regional
└── solver.py          # Loop de resolución (worklist)
```

### 1. `term.py` -- Álgebra de términos

Términos de primer orden, inmutables y hashables:

- **`Term`** -- base abstracta
- **`Var(id)`** -- metavariable de inferencia (identity-based: cada `fresh()` produce una única)
- **`Con(name, args)`** -- constructor de tipo con argumentos posicionales
  - `Con("HashMap", (Var(?K), Con("Vec", (Var(?V),))))` = `HashMap[?K, Vec[?V]]`
  - Los ground types son `Con(name, ())` -- e.g. `Con("Text", ())`
- **`Err(reason)`** -- término envenenado para propagar errores sin crashear

El mapping futuro a protomorph es directo: `Con` -> `Spec`/`NominalType`, `Var` -> `pm.Var` con un `VarType` de inferencia.

### 2. `unify.py` -- Unificación + substitución

Substitución basada en `dict[Var, Term]` con walk de cadenas:

- **`Subst`** -- clase mutable con las operaciones:
  - `fresh(name?) -> Var` -- genera metavariable fresca
  - `walk(term) -> Term` -- resuelve cadenas de bindings hasta forma canónica
  - `apply(term) -> Term` -- walk profundo recursivo (sustituye en todo el árbol)
  - `unify(a, b) -> bool` -- Robinson con occurs check, muta la store
  - `occurs_in(var, term) -> bool`
  - `snapshot() -> SubstSnapshot` -- para backtracking en candidate pruning
  - `restore(snapshot)` -- deshace bindings hasta un punto

`snapshot`/`restore` usa un trail (lista de bindings añadidos desde el snapshot) en lugar de copiar el dict entero. Esto permite probar candidatos sin coste de copia.

### 3. `constraint.py` -- Tipos de constraint

- **`Constraint`** -- base con `vars() -> set[Var]` (variables que menciona)
- **`Eq(left: Term, right: Term)`** -- unificación directa
- **`Conforms(actual: Term, expected: Term)`** -- por ahora equivalente a `Eq`, extensible para subtyping
- **`Choice(target: Var, options: list[CandidateOption])`** -- disyunción por overloads. Cada opción tiene sus propias constraints; exactamente una debe sobrevivir
- **`Deferred(constraint: Constraint, blocking: set[Var])`** -- wrapper que indica "re-evaluar cuando alguna de `blocking` sea resuelta"

### 4. `candidate.py` -- Candidate sets

```python
@dataclass
class CandidateOption:
    label: str                        # nombre/debug del overload
    premises: tuple[Constraint, ...]  # constraints que deben cumplirse
    result: Term                      # término resultado si se elige esta candidata
    bindings: dict[str, Term]         # env capturado (futuro: del MatchEnv)
    alive: bool = True                # eliminada por pruning?
```

La `Choice` constraint referencia estas opciones. El solver las prueba con snapshot/restore: para cada opción viva, toma un snapshot, intenta satisfacer sus premises, y marca como muerta las que fallan.

### 5. `region.py` -- InferRegion

```python
class InferRegion:
    subst: Subst                              # store compartido
    pending: deque[Constraint]                # worklist
    watchers: dict[Var, list[Constraint]]     # var -> constraints que la mencionan
    choices: list[Choice]                     # candidate sets activos
    committed: dict[Choice, CandidateOption]  # decisiones finales
    errors: list[SolverError]                 # diagnósticos
```

API:
- `fresh(name?) -> Var`
- `add_constraint(constraint)` -- añade al worklist y registra watchers
- `add_choice(target, candidates)` -- registra un candidate set
- `solve() -> SolveResult` -- ejecuta el solver loop

### 6. `solver.py` -- Loop de resolución

```
while pending:
    constraint = pending.popleft()
    
    match constraint:
        case Eq(a, b):
            if subst.unify(a, b):
                wake_watchers(newly_bound_vars)
            else:
                emit_error(...)
                
        case Conforms(actual, expected):
            # por ahora, mismo camino que Eq
            handle_eq(actual, expected)
            
        case Choice(target, options):
            alive = [o for o in options if o.alive]
            
            for option in alive:
                snap = subst.snapshot()
                ok = try_all_premises(option.premises)
                subst.restore(snap)
                if not ok:
                    option.alive = False
            
            alive = [o for o in options if o.alive]
            if len(alive) == 0:
                emit_error("no viable candidate")
            elif len(alive) == 1:
                commit(target, alive[0])  # unify target=result, add premises
            else:
                defer(constraint)  # re-check when more info available
                
        case Deferred(inner, blocking):
            if any(subst.is_bound(v) for v in blocking):
                pending.append(inner)  # promote back
            else:
                defer(constraint)  # still blocked
```

El loop itera hasta que el worklist se vacía. Si quedan choices no resueltos y variables no ligadas, se reporta ambigüedad.

### 7. Tests

```
tests/
├── test_term.py           # construcción, igualdad, hashing
├── test_unify.py          # unificación, occurs check, snapshot/restore
├── test_constraint.py     # constraint solving individual
├── test_candidate.py      # candidate pruning
└── test_solver.py         # escenarios regionales del documento
```

El test más importante es `test_solver.py`, que codifica los ejemplos del documento:
- El ejemplo simple (`search[T](container, content)`)
- El ejemplo de HashMap con múltiples call sites y defaults
- El ejemplo con overloads competidores (`entry<K,V>` vs `entry<V>`)

### Decisiones de diseño abiertas

Hay un par de puntos donde me gustaría tu opinión: