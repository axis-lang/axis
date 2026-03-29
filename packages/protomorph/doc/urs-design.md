# URS Design - Unified Reasoning

Este documento define la arquitectura objetivo del sistema de razonamiento
unificado de Protomorph. Su foco no es describir el experimento actual de
`pm/chalk.py`, sino fijar el modelo hacia el que debe converger la futura
implementacion en `packages/protomorph/src/pm/reasoning/*`.

La implementacion de URS en `pm/reasoning/*` debe escribirse desde cero. Los
modulos `pm/chalk.py` y `pm/solver.py` pueden servir como antecedentes
historicos o experimentales, pero no son la base de migracion. La unica pieza
operativa del solver actual que se asume reutilizable como primitiva tecnica es
`pm/unification.py`.

`solver-design.md` sigue siendo el antecedente conceptual principal y
`chalk-design.md` conserva valor como experimento de arquitectura. Este
documento los sintetiza y corrige para aterrizar una arquitectura consistente
con:

- `Spec` como unidad fundamental de hechos, reglas y queries
- la filosofia de inmutabilidad y cacheo incremental de protobase/flux
- inferencia diferida estilo Rust
- negacion estratificada estilo Datalog
- computacion de tipos bloqueada estilo TypeScript

Nota de estado:

- la implementacion base en `packages/protomorph/src/pm/reasoning/*` ya existe
- este documento sigue siendo la referencia arquitectonica principal
- el estado de cierre y las iteraciones pendientes se siguen en
  `packages/protomorph/doc/urs-closure-roadmap.md`
- la referencia practica de la superficie publica actual vive en
  `packages/protomorph/doc/reasoning-api.md`


## 1. Objetivo

URS (Unified Reasoning System) debe permitir que los tres dominios principales
de razonamiento de Protomorph convivan sobre una sola infraestructura:

1. algebra de tipos estilo TypeScript
2. motor logico estilo Datalog
3. resolucion de tipos y obligations estilo Rust

La idea central no cambia:

- las relaciones son `Spec`
- las reglas son datos
- la evaluacion es incremental
- la mutabilidad operativa queda encapsulada dentro de evaluaciones derivadas

Lo que si cambia respecto a iteraciones previas es la forma de estructurar el
solver:

- no un unico objeto mutable publico
- no un solver top-down aislado por query
- no `Ambiguous` como catch-all

En su lugar, URS se organiza como una cascada de snapshots inmutables:

```text
Database -> Engine -> Session -> Query -> Result
```

Cada salto produce nuevos fixed-points y tablas derivadas, usando mutabilidad
interna encapsulada durante su computacion.


## 2. Principios de diseno

## 2.1 `Spec` es la unidad universal de razonamiento

Las relaciones siguen representandose como `Spec`:

- `std.rels.Eq[T, U]`
- `std.rels.Sub[T, U]`
- `std.rels.Bound[T, Trait]`
- `std.rels.Proj[T, Trait, Name, R]`
- `std.rels.KeyOf[T, R]`
- hechos Datalog como `mydb.parent[A, B]`

Consecuencia:

- no hay una jerarquia `Rel` separada
- reglas, hechos y goals viven en el mismo espacio de valores
- traversal, substitution y canonicalizacion operan sobre un solo lenguaje


## 2.2 Inmutabilidad hacia afuera, mutabilidad hacia adentro

Los objetos publicos son snapshots `Consed` e inmutables.

La mutabilidad solo aparece dentro de los kernels operativos usados para
calcular propiedades o metodos derivados. El resultado de cada computacion es un
nuevo valor inmutable, apto para ser cacheado por `flux`.

Esto implica:

- `Engine(db)` es un valor inmutable
- `Engine` expone propiedades derivadas como `rules_by_anchor`, `strata`,
  `global_tables`, etc.
- la mutabilidad real vive en kernels efimeros internos como worklists,
  tabling mutable, rollback y `UnionFind`
- esos kernels nunca se exponen como API publica

La consecuencia practica es que URS no persiste procesos mutables; persiste
snapshots. Cada salto de capa produce un nuevo valor inmutable que resume el
fixed-point alcanzado hasta ese nivel.


## 2.3 Tabling por capas

URS no usa un unico memo global. Usa tabling por nivel de validez:

- `Engine` memoiza informacion reusable globalmente
- `Session` memoiza informacion reusable dentro de un contexto local
- `Query` memoiza informacion reusable dentro de una consulta concreta

Esto evita mezclar:

- conocimiento global derivado solo de la base de datos
- conocimiento dependiente del contexto local
- conocimiento dependiente del goal raiz


## 2.4 `Ambiguous` no es catch-all

URS debe distinguir explicitamente entre:

- respuestas concretas
- obligaciones diferidas
- floundering por falta de instanciacion suficiente
- ciclos mixtos o negativos
- multiplicidad real de respuestas

En particular:

- `Ambiguous` queda reservado a multiplicidad real de respuestas observables
- `Deferred` significa retriable cuando aparezca mas informacion
- `Floundered` significa falta de informacion suficiente para proceder ahora
- `MixedCycle` y `NegativeCycle` son problemas estructurales separados


## 2.5 Los operadores no deciden la capa de memoizacion

Los operadores logicos se modelan como placeholders especializados, pero no
deciden por si mismos donde se cachea su resultado.

El operador solo describe su semantica local y devuelve un paso de evaluacion.
La capa de solver decide donde ese resultado es reusable segun sus
dependencias reales.


## 3. Arquitectura publica

La forma canonical del sistema es:

```python
class Database(Consed):
    ...  # query api base


class Engine(Consed):
    db: Database


class Session(Consed):
    engine: Engine
    context: SolveContext
    state: SessionState


class Query(Consed):
    session: Session
    goal: pm.Spec


class Result(Consed):
    query: Query
    outcome: SolverResult
    next_session: Session | None = None
    continuation: Query | None = None
```


## 3.1 `Database`

`Database` es la verdad de base del sistema.

Responsabilidades:

- exponer `rules_for_anchor(...)`
- exponer `facts_by_anchor(...)`
- exponer consultas del host necesarias para operadores o resolucion semantica
- no almacenar estado derivado mutable


## 3.2 `Engine`

`Engine` es una fachada inmutable y derivada sobre `Database`.

Importante: el llamado "compiled program" no tiene por que ser un objeto
nominal separado. Puede ser simplemente el conjunto de propiedades derivadas de
`Engine(db)`.

En otras palabras, esto es valido y deseable:

```python
class Engine(Consed):
    db: Database

    @flux.property
    def rules_by_anchor(self) -> ...: ...

    @flux.property
    def facts_by_anchor(self) -> ...: ...

    @flux.property
    def dependency_graph(self) -> ...: ...

    @flux.property
    def sccs(self) -> ...: ...

    @flux.property
    def strata(self) -> ...: ...

    @flux.property
    def global_tables(self) -> ...: ...
```

Responsabilidades:

- compilar/indexar reglas y hechos por anchor
- construir el grafo de dependencias
- calcular SCCs y estratificacion
- calcular fixed-points globales reusables
- ofrecer una vista solver-shaped de `Database`


## 3.3 `Session`

`Session` representa un contexto local de inferencia o razonamiento.

No esta caracterizada por un goal. Esta caracterizada por:

- `engine`
- `context`
- `state`

Donde `context` puede incluir:

- item o funcion actual
- assumptions activas
- expected types
- facts locales
- modo de solve o estrategia local

Y `state` representa un snapshot persistente del progreso local:

- bindings locales ya comprometidos
- obligations diferidas locales
- facts locales derivados
- overlays de tablas sobre las globales

La sesion es la unidad correcta para modelar inferencia compartida estilo Rust.


## 3.4 `Query`

`Query` representa una consulta raiz dentro de una sesion.

Responsabilidades:

- contener el goal raiz
- construir o exponer la tabla propia de esa consulta
- producir answers, deferreds, ciclo o continuation

`Query` es la unidad natural para resumir o reanudar una consulta concreta.


## 3.5 `Result`

`Result` es el snapshot publico de una query evaluada.

Debe poder contener:

- answers concretas
- bloqueos diferibles
- problemas de ciclo
- una `next_session` para continuar saturando el contexto
- una `continuation` si la propia query necesita reanudarse


## 4. Arquitectura interna paralela

Ademas de la jerarquia publica, URS necesita una jerarquia interna paralela para
organizar el tabling y los fixed-points.

```text
Database
  -> Engine properties
     - rules_by_anchor
     - facts_by_anchor
     - dependency_graph
     - sccs
     - strata
     - global_tables

Session
  -> SessionState
     - local assumptions
     - local bindings snapshot
     - deferred queue snapshot
     - local table overlays

Query
  -> QueryTable
     - open frontier
     - partial answers
     - blockers
     - cycle info
     - continuation state
```

La regla de validez es simple:

- si algo depende solo de `db`, vive en `Engine`
- si depende de `db + contexto local`, vive en `Session`
- si depende de `db + contexto local + goal`, vive en `Query`


## 5. Solver result algebra

La algebra de resultados publica debe ser:

```python
SolverResult = (
    Unique
    | Ambiguous
    | NoSolution
    | Deferred
    | Floundered
    | MixedCycle
    | NegativeCycle
)
```

Semantica:

- `Unique`: una sola respuesta concreta y cerrada
- `Ambiguous`: multiples respuestas concretas observables
- `NoSolution`: no existe prueba en el espacio actual; cuando sea posible debe
  cargar juicio estructurado del fracaso
- `Deferred`: hay obligaciones bloqueadas pero reintentables
- `Floundered`: no hay suficiente instanciacion para proceder correctamente
- `MixedCycle`: ciclo inductivo/coinductivo mixto o inconsistente, idealmente con
  traza inspeccionable
- `NegativeCycle`: ciclo negativo no estratificable, idealmente con traza
  inspeccionable


## 5.1 Blockers

Los bloqueos deben tener forma estructurada.

Taxonomia inicial:

- `StratumPending`
- `NonGroundNegation`
- `OperatorPending`
- `ProjectionBlocked`
- `TypeFunctionBlocked`
- `ImplSelectionBlocked`

La lista puede crecer, pero el principio se mantiene:

- un blocker describe por que no se puede continuar
- un blocker contiene suficiente contexto para reintento posterior


## 5.2 Answers

`Answer` contiene solo:

- el goal
- la sustitucion visible
- la evidencia

No debe contener:

- razones de bloqueo
- razones de ciclo
- banderas provisionales de ejecucion


## 6. Layered tabling y fixed-points

URS adopta un modelo de tabling por capas.

## 6.1 Fixed-points globales de `Engine`

`Engine` calcula fixed-points globales reusables a partir de `Database`.

Esto incluye:

- cierres de hechos por anchor o por SCC
- tablas cerradas de strata inferiores
- indices solver-friendly

Estos resultados deben ser aptos para cacheo incremental por `flux`.


## 6.2 Fixed-points contextuales de `Session`

`Session` calcula fixed-points locales sobre las tablas globales de `Engine`.

Esto incluye:

- assumptions activas
- facts locales
- refinamientos introducidos por bindings locales
- retry de deferreds del contexto

La sesion no debe recomputar las tablas globales; debe trabajar como overlay.


## 6.3 Fixed-points de `Query`

`Query` calcula el fixed-point especifico de un goal raiz sobre la sesion.

Esto incluye:

- answers visibles para el goal
- expansion de subgoals
- blockers de la consulta
- continuation state si la query no esta cerrada


## 6.4 Incrementalidad con `flux`

Este reparto permite invalidacion incremental razonable:

- un cambio en `Database` invalida solo propiedades dependientes de `Engine`
- un cambio en `Session.context` o `Session.state` invalida solo esa sesion y sus
  queries
- un cambio en `Query.goal` invalida solo esa query

El objetivo es evitar recomputar todo el sistema si cambia un solo anchor,
estrato o contexto local.


## 7. Dependencias, SCC y estratificacion

## 7.1 Grafo de dependencias

`Engine` debe construir un grafo de dependencias entre anchors.

Cada regla induce:

- dependencias positivas del head hacia los subgoals positivos
- dependencias negativas del head hacia los subgoals negados


## 7.2 SCC

SCC significa Strongly Connected Component.

Una SCC es un conjunto de anchors mutuamente recursivos. Es la unidad natural
para:

- calcular fixed-points
- organizar tabling
- detectar ciclos negativos internos


## 7.3 Estratos

La estratificacion ordena SCCs o anchors segun sus dependencias negativas.

Regla central:

- un literal negativo `not G` solo puede resolverse cuando el estrato de `G`
  esta cerrado

Consecuencias:

- si el estrato de `G` no esta cerrado -> `Deferred(StratumPending(...))`
- si `G` no es suficientemente ground -> `Floundered(NonGroundNegation(...))`
- si existe una dependencia negativa ciclica no estratificable ->
  `NegativeCycle`

Cuando sea posible, `NegativeCycle` debe exponer una traza estructurada del
componente o ciclo implicado, no solo un mensaje plano.


## 8. Operadores logicos

Las operaciones que no se resuelven solo por pattern matching de reglas deben
modelarse como placeholders especializados.

Direccion propuesta:

```python
class SolverOperator(pm.Placeholder, abstract=True):
    def eval(self, *, goal: pm.Spec, session: SessionView, host: pm.Host) -> LogicOpStep:
        return host.eval_logic_op(self, goal=goal, session=session)
```

Esto permite representar:

- `keyof T`
- proyecciones tipo `T::Item`
- indexed access
- mapped type combinators
- cualquier otro punto de extension semantico


## 8.1 Resultado de evaluacion de operadores

El operador no decide la capa de memoizacion. Solo devuelve un paso de
evaluacion:

```python
LogicOpStep = OpExpand | OpAnswer | OpDeferred | OpFailed
```

Semantica:

- `OpExpand(goals)`: el operador reduce a nuevos goals
- `OpAnswer(answers)`: el operador produce respuestas concretas
- `OpDeferred(blocked)`: el operador queda bloqueado
- `OpFailed(reason)`: el operador no puede satisfacerse

La capa de solver decide luego donde ese resultado es reusable segun sus
dependencias efectivas.


## 8.2 Host y operadores

El host sigue siendo el backend semantico de los operadores, pero el protocolo
de entrada debe ser el del operador.

Direccion recomendada:

- `Operator.eval(...)` es la interfaz primaria
- por defecto delega en `host.eval_logic_op(...)`
- el host decide como evaluar el operador usando el contexto de sesion y el goal
- el solver interpreta el resultado estructurado


## 9. Especificacion tecnica del solver operativo

Aunque la arquitectura publica es inmutable, cada capa puede requerir un kernel
operativo mutable interno para construir su snapshot.

Ejemplos:

- `_EngineSolveCore`
- `_SessionSolveCore`
- `_QuerySolveCore`

Estos kernels pueden usar:

- worklists
- tablas mutables temporales
- `UnionFind`
- snapshots/rollback
- estructuras auxiliares para fixed-point

Pero deben cumplir dos reglas:

1. no formar parte de la API publica
2. producir siempre un resultado inmutable al terminar

El plan de implementacion asume que estos kernels se escriben especificamente
para `pm/reasoning/*` y no como adaptacion incremental de `pm/chalk.py`.


## 9.1 Solve loop conceptual

Cada kernel opera sobre una worklist de obligaciones:

```text
pending -> step(goal) ->
    answers
    new goals
    deferred blockers
    cycle issues
    failure
```

El kernel:

- drena `pending`
- incorpora nuevos subgoals
- registra deferreds
- cierra tablas cuando se alcanza fixed-point
- emite un snapshot persistente al final


## 9.2 Retry de deferreds

Un goal diferido no es un error. Es una obligacion pendiente.

Debe poder reintentarse cuando:

- se cierra un estrato
- se aprende nueva informacion de bindings en la sesion
- un operador pasa de bloqueado a resoluble

La direccion recomendada es que este retry reanude branches desde un entorno
canonico persistido, reconstruyendo un `UnionFind` fresh en vez de rehacer la
query raiz como camino normal.


## 10. Especificacion tecnica de `UnionFind`

`UnionFind` sigue siendo el nucleo de sustitucion compartida de URS. La
implementacion actual en `pm/unification.py` ya ofrece la interfaz base
necesaria.


## 10.1 Rol de `UnionFind`

`UnionFind` no es el solver. Es la infraestructura de sustitucion del solver.

Responsabilidades:

- mantener representantes canonicos de variables
- unificar variables y terminos
- soportar rollback por snapshots
- reificar estructuras con bindings aplicados

No conoce:

- estrategias de solve
- negacion
- tabling
- estratificacion
- operadores


## 10.2 API tecnica

La interfaz tecnica base es:

- `find(x) -> Carrier`
- `bind(var, term, occurs_check=True) -> bool`
- `snapshot() -> int`
- `rollback(mark) -> None`
- `reify(carrier) -> Carrier`

Y la API de unificacion estructural:

- `unify(a, b, subst=uf, occurs_check=True) -> Carrier | None`


## 10.3 Invariantes

- `find(x)` devuelve un representante canonico
- las compresiones de camino deben ser reversibles bajo `rollback`
- `bind(var, term)` debe respetar occurs check si esta activo
- `rollback(mark)` debe restaurar el estado exacto previo al snapshot
- `reify(carrier)` no debe perder estructura semantica


## 10.4 Uso en URS

La sesion es la unidad natural para compartir un `UnionFind`.

Razones:

- varias obligaciones del mismo contexto local deben compartir bindings
- nuevos bindings pueden desbloquear obligations diferidas
- la inferencia bidireccional estilo Rust requiere una sola sustitucion comun

Por lo tanto:

- `Engine` no debe almacenar bindings de sesion
- `Session` si debe representar snapshots derivados de una sustitucion local
- los kernels operativos pueden usar snapshots y rollback para explorar ramas

Mas precisamente:

- `UnionFind` vive dentro de `_SessionSolveCore` y `_QuerySolveCore`
- `SessionState` no debe persistir la estructura interna cruda de `UnionFind`
- la sesion persiste solo una proyeccion estable de bindings visibles
- al comenzar un solve, el kernel reconstruye un `UnionFind` nuevo a partir de
  ese snapshot y lo usa para saturar o reintentar obligaciones


## 11. Alineacion por dominio

## 11.1 TypeScript

URS debe soportar terminos bloqueados de computacion de tipos:

- `keyof T`
- indexed access
- mapped types
- conditional types

Estos deben modelarse como operadores o relaciones normalizables, y si el input
no esta listo deben producir `Deferred` o `Floundered`, nunca `Ambiguous`
espurio.


## 11.2 Rust

URS debe soportar obligations diferidas e inferencia local compartida:

- trait bounds
- projections
- impl selection
- retry de obligaciones tras nueva informacion local

La unidad correcta para esto es `Session`, no `Query`.


## 11.3 Datalog

URS debe soportar:

- hechos y reglas por anchor
- saturacion por fixed-point
- negacion estratificada
- cierre por strata/SCC

La negacion no debe resolverse como simple negation-as-failure top-down.


## 12. Layout de implementacion propuesto

La implementacion objetivo debe vivir en `packages/protomorph/src/pm/reasoning/*`.

Layout sugerido:

```text
pm/reasoning/
  __init__.py
  model.py
  database.py
  engine.py
  session.py
  query.py
  result.py
  operators.py
  stratify.py
  subst.py
  tabling.py
  core.py
```

Notas:

- `Engine` concentra las propiedades derivadas globales
- `Session` concentra contexto y overlays locales
- `Query` concentra la tabla de una consulta concreta
- `subst.py` concentra la integracion de URS con `pm.unification.UnionFind`
- `tabling.py` concentra tablas y fixed-point por capa
- `core.py` concentra kernels operativos mutables
- `model.py` concentra algebra de resultados, blockers y tipos publicos


## 13. Relacion con documentos previos

`solver-design.md` sigue siendo el documento conceptual de origen.

`chalk-design.md` sigue siendo valioso como experimento que demostro:

- viabilidad de `Spec` como unidad central
- canonicalizacion de goals
- valor de separar fachada inmutable y nucleo operativo

Pero URS corrige dos puntos importantes:

- el solver no se organiza ya como una sola query top-down aislada
- `Ambiguous` deja de ser el receptaculo de todo lo no resuelto

Y ademas fija una decision de implementacion explicita:

- URS no se construye como refactor directo de `pm/chalk.py`
- URS se implementa desde cero en `pm/reasoning/*`
- `pm/unification.py` si se reutiliza como infraestructura base de sustitucion


## 14. Roadmap de implementacion

El roadmap de escritura de URS debe seguir este orden, de menor a mayor riesgo
semantico.

Nota de estado:

- este orden ya fue ejecutado en gran medida por la implementacion actual
- varias fases ya estan materializadas de forma parcial o sustancial en
  `packages/protomorph/src/pm/reasoning/*`
- el roadmap vigente de cierre ya no es este bootstrap inicial sino
  `packages/protomorph/doc/urs-closure-roadmap.md`

### Fase 1 - Modelos publicos y superficie base

- escribir `model.py`
- escribir `result.py`
- escribir `database.py`
- fijar `Rule`, `Answer`, `SolverResult`, blockers y algebra de resultados
- agregar tests de shape de resultados y tipos publicos

Objetivo:

- tener una superficie estable sin depender de `pm/chalk.py`


### Fase 2 - Engine global

- escribir `engine.py`
- escribir `stratify.py`
- implementar `rules_by_anchor`, `facts_by_anchor`, `dependency_graph`, `sccs`,
  `strata`
- empezar `global_tables` como fixed-point global minimo

Objetivo:

- consolidar el nivel global reusable y su invalidacion incremental por `flux`


### Fase 3 - Sustitucion y canonicalizacion

- escribir `subst.py`
- integrar `pm.unification.UnionFind`
- definir runtime vars y snapshots visibles de bindings
- definir canonicalizacion de goals y reconstruccion de UF desde snapshots

Objetivo:

- reutilizar `UnionFind` sin persistir su estado interno bruto


### Fase 4 - Query positiva

- escribir `_QuerySolveCore` en `core.py`
- soportar hechos y reglas Horn positivas
- soportar multiples answers
- soportar `NoSolution`

Objetivo:

- tener la primera query evaluable sobre `Engine` sin negacion ni operadores


### Fase 5 - Session contextual

- escribir `SessionState`
- escribir `session.py`
- escribir `_SessionSolveCore`
- agregar overlay de facts/asunciones locales
- agregar bindings compartidos de sesion

Objetivo:

- preparar la unidad correcta de inferencia compartida estilo Rust


### Fase 6 - Deferred y floundering reales

- implementar blockers estructurados
- agregar retry de deferreds en kernels de sesion/query
- distinguir `Deferred` de `Floundered`

Objetivo:

- eliminar `Ambiguous` como sustituto de bloqueo semantico


### Fase 7 - Negacion estratificada

- conectar `Query` y `Session` con `StratificationPlan`
- hacer que `not G` espere el cierre del estrato de `G`
- reportar `NegativeCycle` cuando corresponda

Objetivo:

- alinear Datalog y los terminos bloqueados por negacion con el diseno original


### Fase 8 - Operadores y host

- escribir `operators.py`
- introducir `SolverOperator.eval(...)`
- delegar al host segun convenga
- implementar `OpExpand`, `OpAnswer`, `OpDeferred`, `OpFailed`

Objetivo:

- abrir el camino para `keyof`, projections y otras operaciones no expresables
  solo como matching de reglas


### Fase 9 - Resultados continuables

- terminar `Query.table`
- terminar `Result.next_session`
- terminar `Result.continuation`

Objetivo:

- permitir reanudar queries y reutilizar progreso contextual


### Fase 10 - Evidence y coinduction

- introducir evidence estructurada
- introducir judgments si ya hay forma estable de derivacion
- reintroducir coinduction sobre la nueva algebra de resultados

Objetivo:

- cerrar el modelo semantico sin contaminar answers con estados internos


## 15. Estrategia de tests

La suite de `pm/reasoning/*` debe escribirse desde cero y expresar la
expectativa futura, no congelar accidentalmente el comportamiento experimental
previo.

Layout sugerido:

```text
packages/protomorph/tests/pm2/reasoning/
  test_model.py
  test_engine.py
  test_stratify.py
  test_subst.py
  test_session.py
  test_query.py
  test_operators.py
```

Reglas:

- no reutilizar `test_chalk.py` como oraculo semantico
- mover o reescribir los tests necesarios para que apunten a `pm.reasoning`
- usar `expectedFailure` para expectativas de operadores aun no implementados
  por completo
- asegurar que los tests distingan `Deferred`, `Floundered`, `MixedCycle` y
  `NegativeCycle`


## 16. Criterio de revision

Este documento estara bien encaminado si permite responder afirmativamente a las
siguientes preguntas:

- puede `Engine` recalcular incrementalmente solo las partes globales afectadas
  por cambios en `Database`?
- puede `Session` compartir inferencia entre varias queries del mismo contexto?
- puede `Query` producir continuations o reanudar una consulta?
- estan separados `Answer`, `Deferred`, `Floundered`, `MixedCycle` y
  `NegativeCycle`?
- queda claro el rol de `UnionFind` como infraestructura y no como solver?
- esta claramente delimitado el rol de los operadores y del host?
- queda claro que la implementacion parte desde `pm/reasoning/*` y no como
  migracion incremental de `pm/chalk.py`?


## 17. Proximo paso tecnico

La implementacion base ya existe; el siguiente paso tecnico ya no es arrancar
`pm/reasoning/*` desde cero.

La prioridad actual debe seguir el cierre documentado en
`packages/protomorph/doc/urs-closure-roadmap.md`:

1. consolidacion/cleanup de continuation, ciclos y judgments
2. enriquecimiento conservador de `EngineTables` solo con conocimiento global
3. refinamientos semanticos posteriores sin volver a mezclar el dominio global,
   contextual y de query
