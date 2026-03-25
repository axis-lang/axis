## Lo que implica resolución estilo Rust

El caso canónico:

```rust
let x: Vec<i32> = some_iter.collect();
//     ^^^^^^^^                ^^^^^^^
//     expectation fluye →→→→→ HACIA ATRÁS a través de .collect()
//     para resolver qué impl de FromIterator usar
```

Esto es **bidirectional inference con trait resolution**. La información de tipo fluye en ambas direcciones a través de un grafo de llamadas. Es fundamentalmente más exigente porque:

1. **Flujo hacia adelante (síntesis)**: `1 + 2` → `int`
2. **Flujo hacia atrás (checking)**: `let x: f64 = expr` → expr debe ser `f64`  
3. **Flujo lateral (obligations)**: resolver un constraint genera nuevos constraints
4. **Resolución diferida**: no puedes resolver `collect()` hasta que llegue información del contexto

### Comparación de los tres dominios

```
              TypeScript        Datalog           Rust-style
─────────────────────────────────────────────────────────────
Constraint    T <: U            T ≡ U             T ≡ U + T: Trait
Dirección     forward +         bottom-up         fully bidirectional
              contextual
Resolución    diferida          inmediata/        diferida +
                                semi-naive        obligations
Variables     type vars         logic vars        type vars +
              con bounds                          associated types
Extra         conditional       negation,         trait dispatch,
              types             stratification    impl selection
```

## Lo que cambia en la arquitectura

El requerimiento de Rust pone presión sobre la capa 2 (constraint solver). Ya no basta con "recolectar y resolver" — necesitas un **obligation loop** donde resolver un constraint genera nuevos constraints, y algunos constraints deben esperar a que otros se resuelvan primero.

Esto es esencialmente lo que rustc llama el **obligation forest**:

```
                    ┌──────────────────────┐
                    │  solve(obligation)   │
                    └──────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
          Resolved    Deferred         NewObligations
          (done)      (wait, retry     (push children,
                       when more        continue loop)
                       info arrives)
```

Propongo que la arquitectura sea entonces:

```
┌─────────────────────────────────────────────┐
│  Domain layers                              │
│  ┌───────────┐ ┌────────┐ ┌──────────────┐  │
│  │ Type      │ │ Datalog│ │ Rust-style   │  │
│  │ Algebra   │ │ Engine │ │ Resolver     │  │
│  └─────┬─────┘ └───┬────┘ └──────┬───────┘  │
├────────┼───────────┼─────────────┼──────────┤
│  Constraint Solver                          │
│  ┌──────────────────────────────────────┐   │
│  │ Obligation loop                      │   │
│  │  - pending queue                     │   │
│  │  - solve_step() → Result             │   │
│  │  - propagation + deferral            │   │
│  │  - fixed-point detection             │   │
│  │  - rollback (for impl selection)     │   │
│  └──────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  Unification Core                           │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │ Substitution │  │ Structural Unify   │   │
│  │ (union-find) │  │ (occurs check,     │   │
│  │              │  │  variance-aware)   │   │
│  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Las piezas del core

### Capa 0 — Substitution (Union-Find)

```
Subst:
  find(var)  → Term           # con path compression
  unify(a, b) → ok | fail     # merge dos variables
  snapshot() → SavePoint      # para rollback
  rollback(SavePoint)         # deshacer unificaciones
```

Rollback es crítico: Rust lo necesita para probar impls alternativos ("¿este impl satisface? no → rollback, probar otro"). Datalog lo necesita si se hace top-down con backtracking.

### Capa 1 — Structural Unification

```
unify(a, b, subst, config) → ok | fail

config:
  occurs_check: bool
  variance: (position) → co | contra | in | bi
  on_mismatch: (a, b) → UnifyResult   # hook para subtyping
```

El hook `on_mismatch` es donde TypeScript inyecta subtyping (`int` contra `int | str` no falla — widening) y Rust inyecta trait checking.

### Capa 2 — Constraints + Obligations

```python
# Lenguaje de constraints extensible
Constraint = 
  | Eq(T, U)                    # T ≡ U
  | Sub(T, U)                   # T <: U  
  | HasTrait(T, Trait, assoc)   # T: Trait<Assoc = U>
  | Member(T, Set)              # para Datalog
  | Cond(test, then, else_)     # conditional types

Obligation = Constraint + provenance + state(pending|deferred|resolved|failed)
```

```python
# Solver loop
class Solver:
    subst: Subst
    pending: deque[Obligation]
    deferred: list[Obligation]
    
    def step(self, obligation) -> Resolved | Deferred | NewObligations | Failed
    
    def solve(self):
        while self.pending:
            ob = self.pending.pop()
            match self.step(ob):
                case Resolved():       pass
                case Deferred():       self.deferred.append(ob)
                case NewObligations(new):  self.pending.extend(new)
                case Failed(reason):   return Err(reason)
            
            if not self.pending and self.deferred:
                # retry deferred — si ninguno progresa, es ambiguity error
                progress = self._retry_deferred()
                if not progress:
                    return Err(Ambiguous(self.deferred))
```

Lo clave: `step()` es el **extension point**. Cada dominio implementa su propia estrategia:
- TypeScript: `Sub(int, int|str)` → Resolved (widening)
- Datalog: `Eq(X, term)` → Resolved + bind
- Rust: `HasTrait(Vec<i32>, FromIterator)` → buscar impl → NewObligations

---

Lo más delicado en este diseño es la interacción entre **deferral** y **rollback**. Rust lo necesita para:

```rust
// Ambiguo hasta que se conozca el tipo del receiver:
x.into()  // ¿qué impl Into? → defer
// Más adelante:
let y: String = x.into()  // ahora sabemos → retry deferred
```
---

## Edge cases que estresan el diseño

### TypeScript: type-level computation

```typescript
// keyof: extrae las claves de un tipo estructural
type K = keyof {x: int, y: str}    // → "x" | "y"

// Indexed access: proyecta un campo por tipo literal
type V = {x: int, y: str}["x"]    // → int

// Mapped type: transforma estructura campo a campo
type Readonly<T> = { readonly [K in keyof T]: T[K] }

// Conditional + infer: pattern match a nivel de tipos
type Elem<T> = T extends Array<infer U> ? U : never

// Distribución: conditional se distribuye sobre unions
type Elem<int[] | str[]>  // → int | str  (no (int | str))
```

Esto no son constraints — son **funciones de tipo a tipo**. `keyof T` no dice "T debe ser algo", sino "dame un nuevo tipo computado a partir de T". Es un **sistema de rewriting a nivel de tipos**.

El problema: `keyof T` cuando `T` es una variable aún no resuelta. No puedes computar el resultado, pero tampoco puedes descartarlo. Necesitas **normalización diferida** — una expresión que se reduce cuando su input se resuelve.

### Rust: proyecciones asociadas y selección de impl

```rust
trait Iterator {
    type Item;                              // tipo asociado
    fn next(&mut self) -> Option<Self::Item>;
}

// Proyección: <Vec<i32> as Iterator>::Item ≡ i32
// Pero solo se puede resolver DESPUÉS de encontrar el impl correcto

// Caso difícil: el impl depende de constraints no resueltos
fn foo<T: Iterator>(x: T) -> T::Item { ... }
// T::Item es opaco hasta que se conozca T concreto

// Aun peor: impls que se solapan
impl<T: Display> ToString for T { ... }
impl ToString for str { ... }  // specialization
```

El problema: `T::Item` es un **término bloqueado** — structuralmente presente, semánticamente opaco. Resolver `T::Item` requiere:
1. Conocer `T` concreto
2. Buscar el impl `T: Iterator`
3. Leer `type Item = ...` de ese impl
4. Sustituir

Si cualquier paso falta información, toda la cadena se difiere.

### Datalog: negación y recursión

```prolog
% Regla recursiva con negación estratificada
reachable(X, Y) :- edge(X, Y).
reachable(X, Y) :- edge(X, Z), reachable(Z, Y).
unreachable(X, Y) :- node(X), node(Y), not reachable(X, Y).
%                                       ^^^
% La negación requiere que reachable esté COMPLETAMENTE computado
% antes de evaluar unreachable (estratificación)
```

El problema: la negación rompe la monotonía. No puedes evaluar `not P` hasta que `P` alcance su punto fijo. Esto impone un **orden de evaluación parcial** entre strata.

## El patrón común

Los tres edge cases son instancias del mismo fenómeno:

> **Un término que no puede reducirse todavía porque depende de información que aún no está disponible.**

| Dominio | Término bloqueado | Se desbloquea cuando... |
|---|---|---|
| TypeScript | `keyof T` | `T` se resuelve a un tipo estructural |
| Rust | `T::Item` | se selecciona el impl `T: Iterator` |
| Datalog | `not reachable(X,Y)` | estrato `reachable` alcanza fixed-point |

Esto me lleva a la generalización.

## Taxonomía unificada

La abstracción más profunda es: **todos estos sistemas son razonamiento relacional sobre términos, con normalización**.

```
Term  ──  la cosa sobre la que se razona
          (tipos, hechos, valores)
          Ya existe: Type + Carrier en pm

Var   ──  un agujero en un término
          Ya existe: Placeholder

Rel   ──  una afirmación sobre términos
          (binaria, pero generalizable)

Norm  ──  una transformación Term → Term 
          que puede estar bloqueada
          
Solver──  encuentra asignaciones de Vars 
          que satisfacen todas las Rels,
          aplicando Norms cuando se desbloquean
```

### El insight: todo es una Relation

Incluso las computaciones de tipo son relaciones si las modelas como tal:

```
Eq(T, U)                      T ≡ U
Sub(T, U)                     T <: U
Bound(T, Trait)               T : Trait
Proj(T, Trait, Name, R)       <T as Trait>::Name ≡ R
KeyOf(T, R)                   keyof T ≡ R
MappedOver(T, F, R)           {[K in keyof T]: F(K)} ≡ R  
Fact(name, args...)           name(args...) holds
```

`keyof` deja de ser una "función mágica" y se convierte en una relación `KeyOf(T, R)` con una regla de resolución:

```
KeyOf(IndexedType(inner, index), R)  →  
    R ≡ UnionType(index.keys)         // resuelve
    
KeyOf(Placeholder(_), R)             →  
    Deferred                           // espera
```

`T::Item` es `Proj(T, Iterator, "Item", R)`:

```
Proj(ConcreteType, Iterator, "Item", R)  →  
    lookup impl → R ≡ impl.assoc["Item"]   // resuelve

Proj(Placeholder(_), _, _, R)            →  
    Deferred                                // espera
```

### El solver unificado

```
Solver[Domain]:
    subst:      UnionFind[Var, Term]
    pending:    Queue[Obligation]
    deferred:   List[Obligation]
    
    # Lo que varía por dominio:
    axioms:     Domain.axioms          # hechos, impls, type defs
    rules:      Domain.rules           # cómo resolver cada Rel
    strategy:   Domain.strategy        # eager vs deferred, order
    
    solve_step(obligation) →
        match rules.resolve(obligation, subst, axioms):
            Resolved(new_subst)       → apply, done
            NewObligations(obs)       → push all
            Deferred                  → park, retry later
            Failed(reason)            → report
            Alternatives(branches)    → snapshot + try each (backtrack)
```

La clave es que `rules.resolve` es el **único extension point que importa**. Todo lo demás (el loop, el deferral, el backtracking) es infraestructura compartida.

### Cómo se instancia cada dominio

**TypeScript algebra:**
```python
rules.resolve(Sub(T, UnionType(variants))) →
    if T in variants: Resolved
    else: check each variant...

rules.resolve(KeyOf(IndexedType(_, idx), R)) →
    NewObligations([Eq(R, UnionType(idx.keys))])

rules.resolve(Conditional(T, test, then, else_)) →
    if known(T): 
        if sub(T, test): NewObligations([Eq(result, then)])
        else: NewObligations([Eq(result, else_)])
    else: Deferred
```

**Rust resolver:**
```python
rules.resolve(Bound(T, Trait)) →
    impls = lookup_impls(T, Trait)
    if len(impls) == 1: 
        NewObligations(impl.where_clauses)
    if len(impls) > 1:
        if T is concrete: Alternatives(impls)  # try each
        else: Deferred
    if len(impls) == 0: Failed

rules.resolve(Proj(T, Trait, name, R)) →
    match resolve(Bound(T, Trait)):
        Resolved → Eq(R, selected_impl.assoc[name])
        Deferred → Deferred  # can't project yet
```

**Datalog engine:**
```python
rules.resolve(Fact(name, args)) →
    # Semi-naive: check known facts, then try rules
    for fact in axioms.facts_matching(name):
        if unify(args, fact.args): Resolved
    for rule in axioms.rules_for(name):
        NewObligations(rule.body)  # with fresh vars

strategy = BottomUp(stratified=True)
# Overrides: compute stratum by stratum to fixed point
```

---

La uniformidad taxonómica es entonces:

```
Todo sistema de razonamiento sobre tipos/términos es un
Solver paramétrico sobre:

  1. Term    — qué son los términos          (pm.Type, pm.Carrier)
  2. Var     — qué son las variables         (pm.Placeholder)
  3. Rel     — qué relaciones existen        (Eq, Sub, Bound, Fact, ...)
  4. Rules   — cómo resolver cada relación   (domain-specific)
  5. Strategy— en qué orden resolver         (eager, deferred, stratified)
```



Entonces el diseño debe ser **un solo solver que habla un lenguaje relacional universal**, donde TypeScript, Rust y Datalog son configuraciones del mismo motor, no stacks separados.

## La representación unificada

Partamos de lo que ya existe en pm y veamos qué falta.

### Lo que pm ya tiene bien

```
Term    →  Type, Carrier       (términos con estructura navegable)
Var     →  Placeholder         (variables con identidad por hash-consing)
Struct  →  VaryingType, IndexedType, UniformType  (formas estructurales)
Walk    →  deep_iter, deep_map, deep_zip, subst   (traversal + rewriting)
```

Esto cubre **Term** y **Var**. Lo que falta completamente es **Rel**, **Rules** y **Strategy**.

### Lo que falta: Relation como ciudadano de primera clase

Una relación es un término más. No es metadata, no es un efecto lateral del solver — es un `Builtin` que vive en el mismo universo que los tipos:

```
Rel(kind, args...)  es un  Builtin

donde kind identifica la naturaleza de la relación
y args son los términos relacionados
```

¿Por qué debe ser un Builtin? Porque así:
- Tiene identidad estructural (hash-consing gratis)
- Es navegable (deep_iter, deep_zip funcionan sobre él)
- Es sustituible (subst puede reemplazar placeholders dentro de una Rel)
- Puede ser argumento de otra Rel (meta-razonamiento)
- Se puede unificar contra otra Rel (pattern matching de reglas)

Esto es exactamente lo que hace Datalog — los hechos son términos como cualquier otro. Y lo que hace Chalk (el trait solver de Rust) — las obligations son términos lógicos.

### Taxonomía de relaciones

Todas las relaciones en los tres dominios se reducen a combinaciones de pocas primitivas:

```
                        Rel
                         │
          ┌──────────────┼──────────────────┐
          │              │                  │
       Assertion      Query             Derivation
    "esto es así"   "¿es esto así?"    "esto implica esto"
          │              │                  │
     ┌────┴────┐    ┌────┴────┐        ┌────┴────┐
     │         │    │         │        │         │
    Eq       Sub  Check    Proj      Rule    Normalize
   T ≡ U   T<:U  T:Tr   T::A≡R   H:-B    keyof T≡R
```

Pero a un nivel más fundamental, hay solo **dos operaciones primitivas**:

1. **Binding**: un término se relaciona con otro (`T ≡ U`, `T <: U`, `T : Trait`)
2. **Projection**: de un término se extrae otro (`T::Item`, `keyof T`, `T["x"]`)

Y una **Derivation** es: "dado que estas Rels se satisfacen, esta otra Rel también".

```
Binding(mode, left, right)
    mode: Eq | Sub | Bound | Member | Custom(...)

Projection(source, path, result)
    source: Term
    path:   cómo proyectar (field, associated type, keyof, ...)
    result: Var que recibirá el resultado

Rule(head: Rel, body: [Rel])
    "head holds if all body rels hold"
```

### La pieza que unifica todo: Judgment

En la teoría de tipos se llama **judgment** — una afirmación sobre términos que puede ser verificada o derivada. Es la unidad atómica del razonamiento:

```
Judgment = Rel + Evidence

"no solo afirmo que T <: U, sino que tengo una derivación que lo prueba"
```

¿Por qué importa la evidencia? Porque:
- **TypeScript**: si `T <: U` vía widening a union, el code path es diferente que si es por structural subtyping
- **Rust**: si `T: Display` vía impl directo vs blanket impl, afecta la selección
- **Datalog**: la derivación de un hecho ES la traza de evaluación

En pm, un Judgment sería:

```
Judgment(Builtin):
    rel:      Rel           # la afirmación
    evidence: Evidence      # cómo se derivó (o None si es axioma)
    
Evidence = 
    | Axiom                 # dado como hecho
    | ByRule(rule, subst, sub_judgments)  # derivado
    | ByUnification(subst)  # por unificación directa
```

### El solver como motor de derivación de Judgments

```
Solver:
    known:     Set[Judgment]          # lo que se sabe
    pending:   Queue[Goal]            # lo que se quiere saber
    subst:     UnionFind              # bindings de variables
    
    Goal = Rel que queremos derivar
    
    step(goal: Rel) →
        # 1. ¿Ya lo sabemos?
        if goal in known: Resolved(known[goal])
        
        # 2. ¿Podemos derivarlo?
        for rule in rules_for(goal):
            match try_rule(rule, goal):
                Success(judgment):    return Resolved(judgment)
                NeedsMore(subgoals): return NewGoals(subgoals)
                Blocked(on_var):     return Deferred(on_var)
        
        # 3. No hay reglas aplicables
        return Failed
```

La diferencia entre los dominios es solo **qué reglas se cargan**:

```
TypeScript config:
    rules = [
        # Eq por structural match
        Rule(Eq(T, T), []),                          # reflexividad
        Rule(Eq(Varying(..A), Varying(..B)), 
             [Eq(A_i, B_i) for i]),                  # structural
        
        # Subtyping
        Rule(Sub(T, UnionType(..V)), [any Sub(T, V_i)]),
        Rule(Sub(IndexedType(..A, idxA), IndexedType(..B, idxB)),
             [Sub(A_i, B_i) for matching keys]),     # width+depth
        
        # Normalization
        Rule(Eq(KeyOf(IndexedType(_, idx)), R),
             [Eq(R, UnionType(idx.keys))]),
        
        # Conditional
        Rule(Eq(Conditional(T, test, then, _), R),
             [Sub(T, test), Eq(R, then)]),
        Rule(Eq(Conditional(T, test, _, else_), R),
             [NotSub(T, test), Eq(R, else_)]),
    ]

Rust config:
    rules = [
        # Trait resolution: buscar impl
        Rule(Bound(T, Trait),
             [match_impl(T, Trait) → impl.where_clauses]),
        
        # Projection: resolver tipo asociado
        Rule(Eq(Proj(T, Trait, name), R),
             [Bound(T, Trait), 
              Eq(R, selected_impl.assoc[name])]),
    ]

Datalog config:
    rules = user_defined_rules
    strategy = BottomUp(stratified=True)
```

### Cómo coexisten

El caso real — un type checker que usa Datalog para trait resolution:

```
# Un programa que type-checkea:
fn process<T: Serialize + Iterator>(x: T) -> Vec<T::Item> {
    x.collect()
}

# Genera estas goals simultáneamente:

Bound(T, Serialize)                    # → Rust rules
Bound(T, Iterator)                     # → Rust rules  
Eq(Proj(T, Iterator, "Item"), ?Item)   # → Rust rules (projection)
Bound(Vec<?Item>, FromIterator)        # → Rust rules
Eq(return_type, Vec<?Item>)            # → structural unification

# Internamente, Bound(T, Serialize) se resuelve buscando impls,
# que podría ser una query Datalog:

impl_exists(T, "Serialize") :- 
    concrete_impl(T, "Serialize").
impl_exists(T, "Serialize") :- 
    blanket_impl(U, "Serialize"), sub(T, U).
```

Un solo solver, un solo subst, un solo espacio de Judgments. Las reglas de diferentes dominios coexisten y se invocan mutuamente.

### Representación en pm

Todo lo anterior mapeado a la estructura actual:

```python
# Rel, Judgment, Evidence son Builtins — 
# hash-consed, navegables, sustituibles

class Rel(Builtin, abstract=True):
    """Una afirmación sobre términos."""

class Eq(Rel):
    left: pm.Type
    right: pm.Type

class Sub(Rel):
    sub: pm.Type
    super_: pm.Type

class Bound(Rel):
    target: pm.Type
    trait_: pm.Spec     # un trait es un Spec

class Projection(Rel):
    source: pm.Type
    trait_: pm.Spec
    name: str
    result: pm.Type     # típicamente un Placeholder

class Fact(Rel):
    predicate: str
    args: pm.Tuple

class Judgment(Builtin):
    rel: Rel
    evidence: pm.Carrier   # Evidence tree, o LeafCarrier para axiomas

class Rule(Builtin):
    head: Rel               # pattern con Placeholders
    body: pm.Tuple[Rel]     # sub-goals
```

Al ser Builtins, deep_iter sobre un `Rule` encuentra los Placeholders en su head y body. `subst` sobre una `Rel` sustituye variables. `unify` entre dos `Rel` hace pattern matching. **Toda la maquinaria de traversal existente funciona gratis sobre el sistema lógico.**

### Lo que hay que construir sobre pm

```
Existente (pm hoy)          Necesario (nuevo)
─────────────────────────    ──────────────────────────
Type, Carrier, Placeholder   Rel, Judgment, Evidence
deep_iter, deep_map, subst   UnionFind (reemplaza subst simple)
deep_zip                     Solver loop (obligation forest)
                             Rule matching (unify Rel contra Rel)
                             Strategy (eager/deferred/stratified)
                             Domain configs (TS/Rust/Datalog rules)
```

El punto crítico de validación: ¿los Builtins actuales (Consed, hash-consing, `__invariants__`) soportan la carga de tener miles de Judgments vivos simultáneamente en un solve? El WeakValueDictionary de Consed podría ser un bottleneck si el solver produce y descarta muchos términos intermedios.


Exacto. Esa es la simplificación correcta.

## Rel es Spec

Si `Eq(A, B)` es `Spec.of("std.rels.Eq", A, B)`, entonces:

- No necesitas una jerarquía `Rel` nueva — ya la tienes
- Un `Judgment` es un `Spec` con evidencia
- Un `Rule` es un `Spec` cuyo schema tiene head + body
- Las reglas del solver son pattern matching sobre Specs — que es exactamente lo que `unify` ya hace

```python
# No esto:
class Eq(Rel):
    left: pm.Type
    right: pm.Type

# Sino esto:
Spec.of("std.rels.Eq", A, B)
Spec.of("std.rels.Sub", T, U)
Spec.of("std.rels.Bound", T, trait)
Spec.of("std.rels.Proj", T, trait, name, result)
Spec.of("std.rels.KeyOf", T, result)

# Un hecho Datalog:
Spec.of("mydb.parent", alice, bob)
Spec.of("mydb.reachable", X, Y)
```

Todo vive en el mismo espacio nominal (`anchor` + `args`). El solver no necesita saber que `std.rels.Eq` es "especial" a nivel de representación — solo necesita reglas que lo resuelvan.

## Lo que esto implica

### El solver opera sobre Specs puros

```python
# Una regla es:
Rule = Spec.of("std.logic.Rule",
    head,       # Spec con placeholders
    body,       # Tuple de Specs (sub-goals)
)

# Un goal es un Spec que queremos derivar
goal = Spec.of("std.rels.Eq", placeholder("T"), INT)

# Resolver = unificar goal contra heads de reglas disponibles
for rule in rules:
    match = unify(wrap(goal), wrap(rule.head), is_var=is_var)
    if match is not None:
        # aplicar sustitución al body → nuevos sub-goals
```

Toda la maquinaria existente — `unify`, `subst`, `deep_iter`, `wrap` — opera directamente sobre las relaciones sin ningún adaptador.

### Las reglas de cada dominio son datos, no código

```python
# TypeScript: reflexividad de Eq
Rule(
    head = Spec.of("std.rels.Eq", placeholder("T"), placeholder("T")),
    body = ()  # axioma
)

# TypeScript: subtyping en union — T <: U|V si T <: U ó T <: V
Rule(
    head = Spec.of("std.rels.Sub", placeholder("T"), 
                   UnionType(placeholder("*Variants"))),
    body = (Spec.of("std.rels.Sub.Any", placeholder("T"), 
                    placeholder("*Variants")),)
)

# Rust: projection — T::Item ≡ R si T: Iterator y el impl dice Item = R
Rule(
    head = Spec.of("std.rels.Proj", placeholder("T"), 
                   Spec.of("Iterator"), "Item", placeholder("R")),
    body = (
        Spec.of("std.rels.Bound", placeholder("T"), Spec.of("Iterator")),
        Spec.of("std.rels.ImplAssoc", placeholder("T"), 
                Spec.of("Iterator"), "Item", placeholder("R")),
    )
)

# Datalog: regla de usuario
# ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
Rule(
    head = Spec.of("mydb.ancestor", placeholder("X"), placeholder("Y")),
    body = (
        Spec.of("mydb.parent", placeholder("X"), placeholder("Z")),
        Spec.of("mydb.ancestor", placeholder("Z"), placeholder("Y")),
    )
)
```

Todas tienen la misma forma. El solver no distingue entre ellas.

### Judgment = Spec + evidencia

```python
# Un judgment derivado:
Spec.of("std.logic.Judgment",
    Spec.of("std.rels.Eq", INT, INT),           # lo que se probó
    Spec.of("std.logic.ByRule",                  # cómo
        rule_ref,
        subst_snapshot,
        sub_judgments,                           # Tuple de Judgments hijos
    ),
)
```

También es un Spec. La traza de derivación es navegable con `deep_iter`. Podrías unificar dos Judgments para comparar derivaciones. Todo gratis.

## El solver loop simplificado

```python
class Solver:
    subst: UnionFind           # bindings de variables
    rules: Tuple               # Tuple de Rules (son Specs)
    known: set[Spec]           # judgments derivados
    pending: deque[Spec]       # goals por resolver
    deferred: list[Spec]       # goals bloqueados
    
    def step(self, goal: Spec) -> Result:
        # 1. ¿Ya derivado?
        if goal in self.known:
            return Resolved
        
        # 2. Intentar cada regla
        for rule in self.rules_matching(goal):
            snapshot = self.subst.snapshot()
            head, body = rule.args[0], rule.args[1]
            
            match = unify(wrap(goal), wrap(head), 
                         is_var=is_var, subst=self.subst)
            
            if match is None:
                self.subst.rollback(snapshot)
                continue
            
            if not body:
                return Resolved
            
            # Aplicar sustitución actual al body
            sub_goals = tuple(
                self.subst.apply(g) for g in body
            )
            
            # ¿Algún sub-goal tiene variables sin resolver?
            if any(is_blocked(g) for g in sub_goals):
                self.subst.rollback(snapshot)
                return Deferred
            
            return NewGoals(sub_goals)
        
        return Failed
```

`rules_matching(goal)` es donde entra la estrategia: puede ser lineal scan (simple), indexado por anchor (eficiente), o semi-naive por strata (Datalog).

## Lo que cambia en pm

### Necesario nuevo

1. **UnionFind** — reemplaza el dict simple de `_capture`. Con snapshot/rollback.

2. **`unify` que opera sobre subst compartida** — la actual crea bindings fresh cada vez. Necesita aceptar un `UnionFind` externo y mutar.

3. **Rule indexing** — un índice de reglas por anchor del head, para no escanear todas las reglas en cada step.

4. **Strategy trait** — cómo se priorizan goals y cuándo se re-evalúan deferred.

### No necesario (ya existe)

- Representación de relaciones → **Spec**
- Representación de reglas → **Spec con schema head+body**
- Pattern matching → **unify**
- Sustitución → **subst** (el mecanismo, no la estructura)
- Traversal de derivaciones → **deep_iter**
- Identidad estructural → **hash-consing de Consed**

### La pregunta de rendimiento

El hash-consing de Consed usa `WeakValueDictionary`. Durante un solve intenso (miles de goals, unificaciones intermedias), esto implica muchas lookups y posible GC pressure. Dos opciones:

- **Arena temporal**: los términos intermedios del solver viven en un scope que se descarta al terminar, sin pasar por consing. Solo los Judgments finales se consean.
- **Consing selectivo**: los Specs que son relaciones/goals se consean (porque se comparan por identidad frecuentemente), los intermedios de sustitución no.

Esto es una decisión de implementación, no de diseño. El modelo `Rel = Spec` es correcto independientemente.

---

El siguiente paso natural sería implementar UnionFind sobre pm y refactorizar `unify` para que acepte un subst externo. Eso solo ya desbloquea los tres dominios. ¿Avanzamos ahí?