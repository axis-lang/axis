# `pm.reasoning` Public API

Este documento define la API publica actual de `pm.reasoning` tal como se
reexporta desde `packages/protomorph/src/pm/reasoning/__init__.py`.

Su objetivo es practico:

- describir que nombres forman parte de la superficie publica
- explicar como se usan en codigo cliente
- distinguir la API comun de la API avanzada de introspeccion/extensibilidad

No reemplaza `packages/protomorph/doc/urs-design.md`.

- `urs-design.md` define la arquitectura objetivo
- `urs-closure-roadmap.md` describe el estado de cierre e iteraciones
- este documento describe la superficie publica actual que ya se puede importar


## 1. Import recomendado

La forma recomendada de consumir la API es:

```python
from pm.reasoning import Engine, Rule, RuleSetDatabase
```

Para exploracion mas rica o extension semantica:

```python
from pm.reasoning import (
    Database,
    Engine,
    Session,
    Query,
    Result,
    Unique,
    Ambiguous,
    NoSolution,
    Deferred,
    Floundered,
    MixedCycle,
    NegativeCycle,
)
```


## 2. Flujo de uso principal

La API publica esta organizada alrededor de esta cadena:

```text
Database -> Engine -> Session -> Query -> Result
```

### Ejemplo minimo

```python
import pm
from pm.reasoning import Engine, RuleSetDatabase


db = RuleSetDatabase(
    facts=(
        pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")),
    )
)

engine = Engine(db)
session = engine.session()
query = session.query(pm.Spec.of("test.parent", pm.Spec.of("test.alice"), pm.placeholder("Q")))
result = query.result

match result.outcome:
    case pm.reasoning.Unique(subst=subst):
        print(subst)
```


## 3. API comun

Esta es la parte de la API que deberia cubrir la mayoria de los usos normales.


## 3.1 `Database`

Clase abstracta que representa la fuente semantica de verdad.

Metodos/propiedades publicos:

- `anchors -> frozenset[str]`
- `rules_for_anchor(anchor: str) -> tuple[Rule, ...]`
- `facts_by_anchor(anchor: str) -> tuple[pm.Spec, ...]`
- `is_coinductive_anchor(anchor: str) -> bool`
- `schema_for(spec: pm.Spec) -> pm.TupleLikeType | None`
- `eval_logic_op(operator, *, goal, session) -> object | None`

Uso recomendado:

- subclassing cuando se quiere un backend propio
- no almacenar estado derivado mutable en la instancia


## 3.2 `RuleSetDatabase`

Implementacion concreta y simple de `Database` basada en reglas y hechos en
memoria.

Campos publicos:

- `rules: tuple[Rule, ...]`
- `facts: tuple[pm.Spec, ...]`
- `coinductive_anchors: frozenset[str]`
- `host: pm.hosted.Host`

Uso recomendado:

- tests
- ejemplos
- motores pequeños en memoria


## 3.3 `Engine`

Fachada global inmutable derivada sobre `Database`.

Propiedades publicas:

- `db: Database`
- `anchors -> frozenset[str]`
- `rules_by_anchor -> frozendict[str, tuple[Rule, ...]]`
- `facts_by_anchor -> frozendict[str, tuple[pm.Spec, ...]]`
- `all_rules -> tuple[Rule, ...]`
- `dependency_graph -> DependencyGraph`
- `sccs -> tuple[Scc, ...]`
- `strata -> StratificationPlan`
- `global_tables -> EngineTables`

Metodos publicos:

- `rules_for_anchor(anchor: str) -> tuple[Rule, ...]`
- `facts_for_anchor(anchor: str) -> tuple[pm.Spec, ...]`
- `facts_for_component(component_id: int) -> tuple[pm.Spec, ...]`
- `derived_facts_for_component(component_id: int) -> tuple[pm.Spec, ...]`
- `session(context=None, state=None) -> Session`

Uso recomendado:

- crear una sola vez por `Database`
- reutilizarlo para muchas `Session`


## 3.4 `Session`

Snapshot contextual de razonamiento local.

Campos publicos:

- `engine: Engine`
- `context: SolveContext`
- `state: SessionState`

Metodos publicos:

- `query(goal: pm.Spec) -> Query`
- `solve(goal: pm.Spec) -> SolverResult`
- `with_bindings(bindings) -> Session`
- `with_deferred(deferred) -> Session`
- `clear_deferred() -> Session`
- `with_query_table(key, table) -> Session`
- `without_goal(key) -> Session`
- `with_local_facts(*facts) -> Session`
- `retry_deferred() -> Session`
- `resume_open_queries() -> Session`

Uso recomendado:

- representar bindings compartidos por contexto local
- reintentar obligaciones diferidas sin mutar en sitio


## 3.5 `SessionState`

Estado persistido de una `Session`.

Campos publicos:

- `bindings: BindingSnapshot`
- `local_facts: tuple[pm.Spec, ...]`
- `deferred: tuple[DeferredGoal, ...]`
- `tables: SessionTables`
- `epoch: int`
- `binding_epoch: int`
- `local_facts_epoch: int`
- `recent_binding_updates: tuple[pm.Placeholder, ...]`
- `recent_local_fact_anchors: tuple[str, ...]`


## 3.6 `SolveContext`

Contexto liviano asociado a una `Session`.

Campos publicos actuales:

- `label: str`

Hoy es minimo. Se puede usar para etiquetar o distinguir sesiones.


## 3.7 `Query`

Consulta raiz dentro de una `Session`.

Campos publicos:

- `session: Session`
- `goal: pm.Spec`

Propiedades publicas:

- `semantic_goal`
- `query_placeholders -> tuple[pm.Placeholder, ...]`
- `semantic_key -> pm.Spec | None`
- `table -> QueryTable`
- `result -> Result`
- `public_answers -> tuple[Answer, ...]`

Uso recomendado:

- inspeccionar resultados canonicos o publicos de una consulta concreta


## 3.8 `Result`

Wrapper publico de una `Query` evaluada.

Campos publicos:

- `query: Query`
- `outcome: SolverResult`
- `next_session: Session | None`
- `continuation: Query | None`

Metodos/propiedades publicos:

- `can_continue -> bool`
- `resume() -> Result`

Uso recomendado:

- leer `outcome`
- si `can_continue` es `True`, usar `resume()` o `next_session.retry_deferred()`


## 3.9 Algebra de resultados

`SolverResult` es la superclase abstracta.

### `Unique`

Campos:

- `goal`
- `subst`
- `evidence`
- `judgment`

Representa una sola respuesta publica observable.

### `Ambiguous`

Campos:

- `goal`
- `subst`
- `evidence`
- `answers`
- `judgments`
- `reason`

Representa multiples respuestas concretas observables.

### `NoSolution`

Campos:

- `goal`
- `reason`
- `judgment`
- `trace`

Representa ausencia de prueba. Cuando hay fracaso estructurado conocido, expone
`judgment`.

### `Deferred`

Campos:

- `goal`
- `blocked`
- `answers`
- `judgments`
- `reason`

Representa bloqueo reintentable.

### `Floundered`

Campos:

- `goal`
- `blocked`
- `answers`
- `judgments`
- `reason`

Representa falta de instanciacion suficiente para proceder correctamente.

### `MixedCycle`

Campos:

- `goal`
- `cycle`
- `reason`
- `trace`
- `judgment`

Representa un ciclo inductivo/coinductivo mixto.

### `NegativeCycle`

Campos:

- `goal`
- `cycle`
- `reason`
- `trace`
- `judgment`

Representa un ciclo negativo no estratificable.


## 3.10 Modelo declarativo

### `Rule`

Campos:

- `head: pm.Spec`
- `body: tuple[pm.Spec, ...]`

Helpers:

- `positive_goals`
- `negative_goals`

### `Answer`

Campos:

- `goal`
- `subst`
- `evidence`
- `judgment`

Es la forma publica de una respuesta concreta.

### `Judgment`

Campos:

- `rel`
- `evidence`
- `subjudgments`
- `trace`

Es la unidad publica de derivacion/evidence.

### `ReasoningValue`

Alias de tipos permitidos dentro de sustituciones/respuestas publicas.


## 3.11 Negacion y helpers

- `NEGATION_ANCHOR = "std.logic.Not"`
- `is_negation(goal: pm.Spec) -> bool`
- `unwrap_negation(goal: pm.Spec) -> pm.Spec`


## 3.12 Blockers, deferreds y wakes

### `DeferredGoal`

Campos:

- `goal`
- `blocker`
- `evidence`
- `wake_on`
- `judgment`

### `Blocker`

Superclase abstracta.

Subtipos publicos:

- `StratumPending(target_stratum, blocked_on)`
- `NonGroundNegation(blocked_on)`
- `OperatorPending(blocked_on, operator)`
- `ProjectionBlocked(blocked_on, projection)`
- `TypeFunctionBlocked(blocked_on, operation)`
- `ImplSelectionBlocked(blocked_on, trait)`

### `WakeCondition`

Superclase abstracta.

Subtipos publicos:

- `BindingsChanged(placeholders=())`
- `LocalFactsChanged(anchors=())`
- `StratumClosed(target_stratum)`
- `OperatorRetriable(operator)`

Helper:

- `default_wake_on(blocker) -> tuple[WakeCondition, ...]`


## 3.13 Ciclos y trazas

### `CycleMember`

Campos:

- `goal`
- `coinductive`
- `via_negation`

### `CycleTrace`

Campos:

- `members`
- `kind`
- `reason`
- `closes_via_negation`

### `CycleIssue`

Campos:

- `cycle`
- `reason`
- `trace`

Helpers:

- `kind`
- `is_negative`

Subtipos publicos:

- `MixedCycleIssue`
- `NegativeCycleIssue`


## 4. API avanzada de introspeccion

Estas piezas son publicas pero no suelen ser necesarias para uso diario.


## 4.1 Tablas y snapshots

### `StoredAnswer`

Forma almacenada de una answer dentro de `QueryTable`.

Campos:

- `subst`
- `evidence`
- `judgment`

### `QueryTable`

Snapshot tabulado de una query concreta.

Campos publicos:

- `key`
- `origin`
- `query_slot_indices`
- `status`
- `answers`
- `failures`
- `deferred`
- `cycle_issue`
- `frontier`
- `continuation_state`
- `active`
- `closed`
- `binding_epoch`
- `local_facts_epoch`
- `placeholders`

Helpers publicos:

- `has_failures`
- `is_cycle`
- `is_blocked`

### `SessionTables`

Indices persistidos a nivel de sesion.

Campos:

- `query_tables`
- `answers_by_anchor`
- `deferred_by_anchor`
- `deferred_by_placeholder`

### `EngineTables`

Indices y cierres globales reusables.

Campos:

- `facts_by_anchor`
- `derived_facts_by_anchor`
- `facts_by_component`
- `derived_facts_by_component`
- `rules_by_anchor`
- `closed_components`
- `closed_strata`

Helpers:

- `facts_of_component(component_id)`
- `derived_facts_of_component(component_id)`
- `is_component_closed(component_id)`


## 4.2 Grafo de dependencias y estratificacion

### `DependencyGraph`

Campos:

- `anchors`
- `positive`
- `negative`

Helpers:

- `positive_of(anchor)`
- `negative_of(anchor)`
- `all_of(anchor)`

### `Scc`

Campos:

- `id`
- `anchors`

### `StratificationPlan`

Campos:

- `graph`
- `components`
- `component_by_anchor`
- `stratum_by_component`
- `negative_cycle_components`

Helpers:

- `component_of(anchor)`
- `stratum_of(anchor)`
- `has_negative_cycle(anchor)`
- `negative_cycle_trace(anchor)`


## 4.3 Branches, variables canonicas y provenance

Esta parte existe para continuation, canonicalizacion e introspeccion avanzada.
No suele ser necesaria para usuarios normales del solver.

### `PendingBranch`

Campos:

- `blocked`
- `remaining_goals`
- `subst`
- `slot_info`
- `blocked_is_negated`
- `completion`
- `subjudgments`

### `EqClassInfo`

Campos:

- `origins: frozenset[pm.Var]`
- `source_names: frozenset[str]`

Metodo:

- `merge(other)`

### Contextos y variables canonicas

Contextos publicos:

- `QueryCtx`
- `RuleTemplateKey`
- `RuleCtx`
- `RuleAppCtx`
- `GoalCtx`
- `BranchCtx`

Variables publicas:

- `QueryVar`
- `RuleVar`
- `RuleAppVar`
- `GoalVar`
- `BranchVar`

Uso recomendado:

- debugging
- inspeccion de provenance
- tests avanzados
- herramientas alrededor del solver


## 4.4 Operadores logicos

### `LogicOpStep`

Superclase abstracta del protocolo de operadores.

Subtipos publicos:

- `OpExpand(goals)`
- `OpAnswer(answers)`
- `OpBind(subst, evidence=None)`
- `OpDeferred(blocked)`
- `OpFailed(reason)`

### `SolverOperator`

Base publica para operadores de razonamiento.

Metodo:

- `eval(*, goal, session, db) -> LogicOpStep`

Subtipos publicos:

- `KeyOfOperator`
- `ProjectionOperator`

Helper publico:

- `relation_operator_for(goal)` no se reexporta; es utilidad interna del modulo


## 5. Que es estable y que es avanzada

### Superficie estable recomendada

Para uso normal, la API recomendada es:

- `Database`
- `RuleSetDatabase`
- `Engine`
- `Session`
- `Query`
- `Result`
- `Rule`
- `Answer`
- `Judgment`
- `Unique | Ambiguous | NoSolution | Deferred | Floundered | MixedCycle | NegativeCycle`
- blockers/wakes principales

### Superficie avanzada pero publica

Para introspeccion o extension:

- `QueryTable`
- `SessionTables`
- `EngineTables`
- `PendingBranch`
- `CycleTrace`
- `CycleIssue`
- contextos/vars canonicas (`QueryVar`, `GoalVar`, `BranchVar`, etc.)
- operadores (`SolverOperator`, `Op*`)

### No recomendado como API comun

Aunque estos nombres sean publicos, no deberian ser la puerta de entrada para
clientes normales:

- `EqClassInfo`
- `RuleAppCtx` / `RuleAppVar`
- `StoredAnswer`

Son utiles, pero pertenecen a la zona de introspeccion/solver internals
persistidos.


## 6. Patrones de uso recomendados

### Consultar una base de reglas/hechos

```python
import pm
from pm.reasoning import Engine, Rule, RuleSetDatabase


x = pm.placeholder("X")
y = pm.placeholder("Y")

engine = Engine(
    RuleSetDatabase(
        rules=(Rule(pm.Spec.of("test.edge", x, y), ()),),
        facts=(pm.Spec.of("test.edge", pm.Spec.of("test.alice"), pm.Spec.of("test.bob")),),
    )
)

result = engine.session().query(pm.Spec.of("test.edge", pm.Spec.of("test.alice"), y)).result
```

### Reintentar obligaciones diferidas

```python
session = result.next_session
session = session.with_bindings(...)
session = session.retry_deferred()
```

### Inspeccionar tablas globales por componente

```python
component_id = engine.strata.component_of("test.path")
facts = engine.global_tables.facts_of_component(component_id)
```

### Inspeccionar trazas de ciclo

```python
outcome = engine.session().query(goal).result.outcome
if isinstance(outcome, (pm.reasoning.MixedCycle, pm.reasoning.NegativeCycle)):
    print(outcome.trace)
```


## 7. Export exacto del paquete

`pm.reasoning` reexporta actualmente estas familias de nombres:

- modelo declarativo y blockers
- algebra de resultados
- `Database` / `Engine` / `Session` / `Query`
- tablas de engine/sesion/query
- operadores logicos
- estratificacion
- variables y contextos canonicos

La fuente de verdad para el export exacto es
`packages/protomorph/src/pm/reasoning/__init__.py`.
