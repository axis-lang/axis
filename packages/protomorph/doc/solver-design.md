# Solver Design — Protomorph Unified Reasoning Core

Manual de diseño e implementación para el sistema de razonamiento unificado
de protomorph. Este documento captura las decisiones de diseño, la taxonomía
de abstracciones, y los detalles de implementación acordados.

## 1. Motivación

Protomorph necesita un core de razonamiento que soporte tres paradigmas
sobre la misma representación y maquinaria:

1. **Álgebra de tipos estilo TypeScript** — subtyping estructural,
   unions/intersections, conditional types, mapped types, `keyof`,
   distribución sobre unions.

2. **Motor lógico estilo Datalog** — hechos, reglas Horn, evaluación
   bottom-up semi-naive, negación estratificada, fixed-point.

3. **Resolución de tipos estilo Rust** — inferencia bidireccional,
   trait resolution con selección de impl, tipos asociados (projections),
   resolución diferida (obligations), backtracking.

Estos tres paradigmas no son stacks independientes. Coexisten y se invocan
mutuamente. Un type checker puede usar Datalog internamente para trait
resolution (como Chalk en Rust). Un motor lógico puede razonar sobre tipos.
La generalización y la coexistencia es el propósito de protomorph.


## 2. Insight fundamental: Rel es Spec

La decisión de diseño más importante: **las relaciones son Specs**.

Un `Spec` ya tiene exactamente el espacio representacional necesario:
un anchor nominal + argumentos posicionales/nombrados, hash-consed,
navegable, sustituible.

```python
# No una jerarquía nueva:
class Eq(Rel):
    left: pm.Type
    right: pm.Type

# Sino la representación existente:
Spec.of("std.rels.Eq", A, B)
Spec.of("std.rels.Sub", T, U)
Spec.of("std.rels.Bound", T, trait)
Spec.of("std.rels.Proj", T, trait, name, result)
Spec.of("std.rels.KeyOf", T, result)

# Un hecho Datalog:
Spec.of("mydb.parent", alice, bob)
Spec.of("mydb.ancestor", X, Y)
```

### Consecuencias

- No se necesita una jerarquía `Rel` separada.
- Un `Judgment` es un Spec con evidencia.
- Un `Rule` es un Spec cuyo schema tiene head + body.
- Las reglas del solver son pattern matching sobre Specs — que es
  exactamente lo que `unify` ya hace.
- `deep_iter`, `deep_map`, `subst`, `wrap` operan directamente sobre
  las relaciones sin adaptadores.
- Las reglas de cada dominio son **datos, no código**.


## 3. Taxonomía unificada

Todo sistema de razonamiento sobre tipos/términos es un solver
paramétrico sobre cinco componentes:

```
Term      —  qué son los términos           →  pm.Type, pm.Carrier
Var       —  qué son las variables          →  pm.Placeholder
Rel       —  qué relaciones existen         →  pm.Spec (con anchor en std.rels.*)
Rules     —  cómo resolver cada relación    →  domain-specific
Strategy  —  en qué orden resolver          →  eager, deferred, stratified
```

### 3.1 Terms y Variables

Ya existen en pm:

- `Type` + `Carrier`: términos con estructura navegable.
- `Placeholder`: variables con identidad por hash-consing `(context, id)`.
- `VaryingType`, `IndexedType`, `UniformType`: formas estructurales.
- `deep_iter`, `deep_map`, `deep_zip`, `subst`: traversal + rewriting.

### 3.2 Relations como Specs

Todas las relaciones en los tres dominios se expresan como Specs:

| Relación | Spec | Uso |
|---|---|---|
| Equality | `std.rels.Eq[A, B]` | Todos |
| Subtyping | `std.rels.Sub[T, U]` | TypeScript, Rust |
| Trait bound | `std.rels.Bound[T, Trait]` | Rust |
| Projection | `std.rels.Proj[T, Trait, Name, R]` | Rust |
| KeyOf | `std.rels.KeyOf[T, R]` | TypeScript |
| MappedOver | `std.rels.MappedOver[T, F, R]` | TypeScript |
| Fact | `{user_ns}.{predicate}[args...]` | Datalog |

A un nivel más fundamental, hay dos operaciones primitivas:

1. **Binding**: un término se relaciona con otro (`Eq`, `Sub`, `Bound`).
2. **Projection**: de un término se extrae otro (`Proj`, `KeyOf`, indexed access).

Y una **Derivation**: "dado que estas Rels se satisfacen, esta otra también".

### 3.3 Rules

```python
Rule = Spec.of("std.logic.Rule",
    head,       # Spec con placeholders — lo que se quiere derivar
    body,       # Tuple de Specs — sub-goals requeridos
)
```

Ejemplos por dominio:

```python
# TypeScript: reflexividad
Rule(
    head = Spec.of("std.rels.Eq", placeholder("T"), placeholder("T")),
    body = ()
)

# TypeScript: subtyping en union
Rule(
    head = Spec.of("std.rels.Sub", placeholder("T"),
                   UnionType(placeholder("*Variants"))),
    body = (Spec.of("std.rels.Sub.Any", placeholder("T"),
                    placeholder("*Variants")),)
)

# TypeScript: keyof
Rule(
    head = Spec.of("std.rels.KeyOf",
                   IndexedType(placeholder("Inner"), placeholder("Idx")),
                   placeholder("R")),
    body = (Spec.of("std.rels.Eq", placeholder("R"),
                    UnionType(idx_keys)),)
)

# Rust: projection de tipo asociado
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

### 3.4 Judgments y Evidence

```python
Judgment = Spec.of("std.logic.Judgment",
    rel,           # lo que se probó
    evidence,      # cómo se derivó
)

Evidence =
  | Spec.of("std.logic.Axiom")
  | Spec.of("std.logic.ByRule", rule_ref, subst_snapshot, sub_judgments)
  | Spec.of("std.logic.ByUnification", subst_snapshot)
```

Al ser Specs, la traza de derivación es navegable con `deep_iter`.
Se pueden unificar dos Judgments para comparar derivaciones.

La evidencia importa porque:
- **TypeScript**: si `T <: U` vía widening o structural, el code path difiere.
- **Rust**: si `T: Display` vía impl directo vs blanket impl, afecta selección.
- **Datalog**: la derivación de un hecho ES la traza de evaluación.


## 4. Arquitectura del solver

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

### 4.1 Capa 0 — Substitution (UnionFind)

**Estado: implementado** (`pm.UnionFind`).

Operaciones:

| Método | Descripción |
|---|---|
| `find(x)` | Representante canónico con path compression |
| `bind(var, term)` | Enlaza variable a término con occurs check |
| `snapshot() → int` | Marca opaca para rollback |
| `rollback(mark)` | Deshace operaciones hasta la marca |
| `reify(carrier)` | Deep-substitution con detección de ciclos |

Detalles de implementación:

- **Path compression**: `find` comprime el camino al root, logueando
  en el trail para rollback.
- **Union by rank**: `_link` balancea el árbol, prefiriendo non-vars
  como root para que `find(var)` retorne el término concreto.
- **Occurs check**: `_occurs(var, term)` busca recursivamente si `var`
  aparece dentro de `term` (resolviendo variables intermedias via `find`).
  Previene tipos infinitos como `$T ≡ List[$T]`.
- **Trail-based rollback**: cada mutación de `_parent` y `_rank` se
  registra en `_trail` como tupla `(tag, node, old_value)`. Rollback
  deshace en orden inverso. Esto soporta snapshot anidados.
- **Reify con cycle detection**: `reify` mantiene un `_seen` set de
  ids de carriers visitados para detectar bindings circulares (posibles
  si `occurs_check=False`).

### 4.2 Capa 1 — Structural Unification

**Estado: implementado** (`pm.unify`).

```python
def unify(a, b, *, is_var=None, subst=None, occurs_check=True)
    → pm.Carrier | None
```

Acepta un `is_var` (crea UF fresh) o un `subst` compartido (acumula
bindings entre llamadas). Esto habilita resolución bidireccional.

Walk stack-based (no recursivo):

1. Pop `(left, right)` del stack.
2. `left = uf.find(left)`, `right = uf.find(right)` — trabaja con
   representantes canónicos.
3. Si `left is right`: skip (ya unificados).
4. Si alguno es var: `bind(var, term)`.
5. Si ambos son leaves no-var: comparar por igualdad.
6. Si ambos son non-leaf: descomponer hijos y push al stack.
7. Si arity mismatch: fail.

**Extension point futuro**: hook `on_mismatch(left, right)` para
inyectar subtyping (TypeScript: `int` contra `int | str`) o trait
checking (Rust) sin modificar el walk core.

### 4.3 Capa 2 — Constraint Solver (obligation loop)

**Estado: por implementar.**

```python
class Solver:
    subst:      UnionFind              # bindings de variables
    rules:      Tuple                  # Tuple de Rules (son Specs)
    known:      set[Spec]              # judgments derivados
    pending:    deque[Spec]            # goals por resolver
    deferred:   list[Spec]             # goals bloqueados

    def step(self, goal: Spec) -> Result:
        # 1. ¿Ya derivado?
        if goal in self.known:
            return Resolved

        # 2. Intentar cada regla
        for rule in self.rules_matching(goal):
            snapshot = self.subst.snapshot()
            head, body = rule.args[0], rule.args[1]

            match = unify(wrap(goal), wrap(head),
                         subst=self.subst)

            if match is None:
                self.subst.rollback(snapshot)
                continue

            if not body:
                return Resolved

            sub_goals = tuple(
                self.subst.reify(wrap(g)).fetch()
                for g in body
            )

            if any(is_blocked(g) for g in sub_goals):
                self.subst.rollback(snapshot)
                return Deferred

            return NewGoals(sub_goals)

        return Failed

    def solve(self):
        while self.pending:
            goal = self.pending.popleft()
            match self.step(goal):
                case Resolved():
                    pass
                case NewGoals(goals):
                    self.pending.extend(goals)
                case Deferred():
                    self.deferred.append(goal)
                case Failed(reason):
                    return Err(reason)

            if not self.pending and self.deferred:
                progress = self._retry_deferred()
                if not progress:
                    return Err(Ambiguous(self.deferred))
```

`rules_matching(goal)` es el principal extension point por dominio:
- Scan lineal (simple).
- Indexado por anchor (eficiente).
- Semi-naive por strata (Datalog).

`step()` retorna uno de cuatro resultados que representan el estado
de progreso de la obligación:

| Result | Significado |
|---|---|
| `Resolved` | Goal satisfecho, binding aplicado |
| `NewGoals(goals)` | Progreso parcial, nuevos sub-goals |
| `Deferred` | Bloqueado, reintentar cuando haya más info |
| `Failed(reason)` | Contradicción, no hay regla aplicable |

### 4.4 Capa 3 — Domain configurations

Cada dominio instancia el solver con sus propias reglas y estrategia.

#### TypeScript

```python
rules = [
    # Eq structural
    Rule(Eq(T, T), []),

    # Sub widening a union
    Rule(Sub(T, UnionType(*V)), [any Sub(T, v_i)]),

    # Sub structural (width + depth)
    Rule(Sub(Indexed(*A, idxA), Indexed(*B, idxB)),
         [Sub(a_i, b_i) for matching keys]),

    # keyof normalization
    Rule(Eq(KeyOf(Indexed(_, idx), R)),
         [Eq(R, Union(idx.keys))]),

    # Conditional type
    Rule(Eq(Conditional(T, test, then, _), R),
         [Sub(T, test), Eq(R, then)]),
    Rule(Eq(Conditional(T, test, _, else_), R),
         [NotSub(T, test), Eq(R, else_)]),
]
```

#### Rust

```python
rules = [
    # Trait bound: buscar impl
    Rule(Bound(T, Trait),
         [match_impl(T, Trait) → impl.where_clauses]),

    # Projection: resolver tipo asociado
    Rule(Eq(Proj(T, Trait, name), R),
         [Bound(T, Trait), Eq(R, selected_impl.assoc[name])]),
]
```

#### Datalog

```python
rules = user_defined_rules
strategy = BottomUp(stratified=True)
```


## 5. Edge cases y términos bloqueados

Los tres dominios comparten un patrón: **términos que no pueden
reducirse todavía porque dependen de información no disponible**.

| Dominio | Término bloqueado | Se desbloquea cuando... |
|---|---|---|
| TypeScript | `keyof T` | `T` se resuelve a un tipo estructural |
| Rust | `T::Item` | Se selecciona el impl `T: Iterator` |
| Datalog | `not reachable(X,Y)` | Estrato `reachable` alcanza fixed-point |

### 5.1 TypeScript: type-level computation

`keyof`, indexed access, mapped types, conditional types con `infer`
son **funciones de tipo a tipo**, no constraints. Se modelan como
relaciones con una regla de normalización:

```
KeyOf(IndexedType(_, idx), R) → R ≡ UnionType(idx.keys)    // resuelve
KeyOf(Placeholder(_), R)      → Deferred                    // espera
```

Distribución sobre unions: `Conditional` se evalúa una vez por
variante de la union, y los resultados se unen.

### 5.2 Rust: projections y selección de impl

`T::Item` es `Proj(T, Iterator, "Item", R)`. Resolver requiere:

1. Conocer `T` concreto.
2. Buscar el impl `T: Iterator`.
3. Leer `type Item = ...` de ese impl.
4. Sustituir.

Si cualquier paso falta información, toda la cadena se difiere.

La selección de impl puede requerir **backtracking**: probar un impl,
si falla rollback y probar otro. El `snapshot/rollback` del UnionFind
soporta esto directamente.

### 5.3 Rust: resolución bidireccional

```rust
let x: Vec<i32> = some_iter.collect();
```

La información de tipo fluye hacia atrás: el tipo esperado `Vec<i32>`
determina qué `FromIterator` impl usar. Esto se soporta con un
`UnionFind` compartido entre múltiples `unify` calls:

```python
uf = UnionFind(is_var)

# Forward: del call site sabemos T = int
unify(Tuple(T, U), Tuple(INT, U), subst=uf)

# Backward: del return type sabemos U = str
unify(LeafCarrier(U), LeafCarrier(STR), subst=uf)

# Ambos resueltos
uf.reify(T)  # → INT
uf.reify(U)  # → STR
```

### 5.4 Datalog: negación y estratificación

La negación rompe monotonía. `not P` no puede evaluarse hasta que
`P` alcance su fixed-point. Esto impone un orden de evaluación parcial
(strata). El solver lo maneja como una variante de deferral: los goals
con negación se difieren hasta que su estrato dependiente esté completo.


## 6. Coexistencia de dominios

El caso real — un type checker que usa Datalog para trait resolution:

```
fn process<T: Serialize + Iterator>(x: T) -> Vec<T::Item> {
    x.collect()
}
```

Genera goals simultáneamente:

```
Bound(T, Serialize)                     → Rust rules
Bound(T, Iterator)                      → Rust rules
Eq(Proj(T, Iterator, "Item"), ?Item)    → Rust rules (projection)
Bound(Vec<?Item>, FromIterator)         → Rust rules
Eq(return_type, Vec<?Item>)             → structural unification
```

Internamente, `Bound(T, Serialize)` se resuelve buscando impls, lo
cual podría ser una query Datalog:

```prolog
impl_exists(T, "Serialize") :- concrete_impl(T, "Serialize").
impl_exists(T, "Serialize") :- blanket_impl(U, "Serialize"), sub(T, U).
```

Un solo solver, un solo `UnionFind`, un solo espacio de Judgments.
Las reglas de diferentes dominios coexisten y se invocan mutuamente.


## 7. Mapa de implementación

### Existente (pm hoy)

| Componente | Módulo | Estado |
|---|---|---|
| Type, Carrier, Placeholder | `type_.py`, `carrier.py` | ✅ |
| deep_iter, deep_map, subst | `carrier.py` | ✅ |
| deep_zip, ZipWalker | `traversal.py` | ✅ |
| Spec, Qual, UnionType, etc | `domain.py` | ✅ |
| Host, NativeHost | `hosted.py`, `native.py` | ✅ |
| UnionFind | `unification.py` | ✅ |
| unify (con UF compartido) | `unification.py` | ✅ |

### Por implementar

| Componente | Prioridad | Descripción |
|---|---|---|
| Solver loop (obligation forest) | Alta | Step/solve con pending/deferred/rollback |
| Rule matching | Alta | Unificar goal contra heads de reglas |
| Rule indexing | Media | Índice por anchor para búsqueda eficiente |
| Strategy trait | Media | Parametrizar orden de evaluación |
| Variance-aware unify | Media | Hook `on_mismatch` para subtyping |
| Evidence tracking | Baja | Judgments con traza de derivación |
| Domain configs (TS/Rust/Datalog) | — | Se construyen incrementalmente |

### Consideraciones de rendimiento

- **Hash-consing y GC**: el `WeakValueDictionary` de Consed podría ser
  bottleneck si el solver produce muchos términos intermedios. Opciones:
  arena temporal para intermedios (solo judgments finales se consean),
  o consing selectivo.

- **`Index.offset_of` es O(n)**: usa `list.index()`. Para schemas
  grandes, mantener un dict invertido `{Id: int}`.

- **`_specialize_schema` es O(n²)**: para cada field type hace
  `deep_iter` + `subst` si no matchea los fast-paths. Considerar
  optimización cuando sea bottleneck medido.

- **Occurs check** es O(size_of_term) por binding. En la práctica los
  árboles de tipos son shallow, pero para Datalog con términos grandes
  podría importar. `occurs_check=False` está disponible como opt-out.
