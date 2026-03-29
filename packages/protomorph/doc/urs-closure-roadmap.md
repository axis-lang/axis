# URS Closure Roadmap

Este documento complementa `packages/protomorph/doc/urs-design.md` y fija la
hoja de ruta de cierre para la implementacion actual de URS en
`packages/protomorph/src/pm/reasoning/*`.

No redefine la arquitectura general. Su objetivo es traducir el diseno a una
secuencia concreta de iteraciones tecnicas, tomando en cuenta el estado actual
de la implementacion.


## 1. Estado actual resumido

La base de URS ya existe y es funcional:

- `Database` ya actua como fuente semantica de verdad.
- `Engine` ya construye indices, SCCs, estratos y un fixed-point global reusable.
- `Session` ya mantiene bindings, deferreds, overlays y retry selectivo, y ya no es meramente replay-driven.
- `Query` ya usa claves semanticas canonicas.
- `QueryTable` ya tiene `status`, `frontier`, `continuation_state`, answers, failures y branches reanudables.
- `SolverOperator` ya unifica `KeyOf` y `Proj` con el pipeline de operadores.
- `Judgment` y la evidence publica ya cubren answers, deferreds, ciclos y `NoSolution`.
- La continuation ya persiste sustitucion/provenance canonicas de branch y puede sintetizar `Unique`, `Ambiguous` y `NoSolution` sin root requery como camino normal.
- La coinduccion ya usa `CycleTrace` explicita y `MixedCycle` / `NegativeCycle` ya exponen trace + judgment.
- `EngineTables` ya expone facts cerradas por anchor y por componente de SCC, todavia de forma conservadora.

Sin embargo, todavia no se considera cerrado el diseno de
`packages/protomorph/doc/urs-design.md`.


## 2. Meta de cierre

Consideraremos URS suficientemente cerrado cuando se cumplan las siguientes
condiciones:

- `QueryTable` pueda reanudar trabajo real, no solo reconsultar el goal raiz.
- `Session` opere como fixed-point contextual fuerte y no como replay manager.
- la coinduccion deje de ser una heuristica minima y tenga una semantica mas
  robusta y explicable.
- `Judgment` y la evidence formen una traza de derivacion uniforme y util.
- `EngineTables` almacene exactamente el conocimiento global reusable y nada que
  dependa de contexto local.


## 3. Invariantes a preservar

Durante el cierre de URS se deben preservar estas reglas:

- `Spec` sigue siendo la unidad universal de hecho, regla y query.
- `Database` sigue siendo la fuente semantica de verdad.
- `Engine` solo guarda conocimiento global reusable.
- `Session` solo guarda conocimiento contextual/local.
- `Query` sigue siendo la unidad del solve raiz.
- `Result` sigue siendo un snapshot inmutable del solve.
- `UnionFind` sigue siendo infraestructura, no API publica del solver.
- `Ambiguous` no vuelve a convertirse en catch-all.
- `Deferred`, `Floundered`, `MixedCycle` y `NegativeCycle` permanecen separados.


## 4. Fase 1 - Continuation operativa real

### Objetivo

Pasar de una continuation descriptiva a una continuation realmente utilizable,
de forma que `_SessionSolveCore` pueda reanudar branches pendientes sin tener
que rehacer el solve raiz como camino principal.

### Estado actual

La mayor parte de esta fase ya esta completada. Hoy `QueryTable` ya guarda:

- `status`
- `frontier`
- `continuation_state`
- `PendingBranch` con `subst`, `slot_info`, `completion` y `subjudgments`

Y `_SessionSolveCore` ya reanuda branches con un `UF` fresh reconstruido desde:

- `SessionState.bindings`
- `PendingBranch.subst`
- `PendingBranch.slot_info`

El root requery ya no es el camino principal de progreso ni de cierre terminal.
Lo pendiente aqui es sobre todo cleanup de superficie y seguir endureciendo la
composicion interna de continuations anidadas cuando haga falta.

### Brainstorm: persistencia de la sustitucion

Antes de cerrar la continuation real conviene fijar explicitamente que significa
persistir el estado de sustitucion de una branch. No queremos persistir el
`UnionFind` crudo; queremos persistir una proyeccion inmutable y reanudable.

Alternativas consideradas:

1. **Solo bindings visibles de sesion**
   - Persistir unicamente `SessionState.bindings`.
   - Ventaja: muy simple.
   - Problema: insuficiente para reanudar branches complejas sin root requery.

2. **Bindings visibles + delta de branch**
   - Persistir `SessionState.bindings` y un delta adicional por branch.
   - Ventaja: equilibrio razonable entre simplicidad y poder.
   - Problema: hay que definir una identidad estable para las variables de
     branch.

3. **Persistir constraints, no sustituciones**
   - Guardar una bolsa de constraints y reconstruir el solve desde ellas.
   - Ventaja: muy declarativo.
   - Problema: reconstruccion mas costosa y riesgo de repetir demasiado trabajo.

4. **Persistent Union-Find**
   - Implementar una variante persistente/inmutable de UF.
   - Ventaja: continuation muy fiel.
   - Problema: demasiada complejidad para el estado actual de URS.

5. **Solo goals reificados**
   - Guardar solo `remaining_goals` ya reificados.
   - Ventaja: simple.
   - Problema: empuja nuevamente hacia replay fuerte y pierde precision.

6. **Canonical branch environment**
   - Persistir cada branch como:
     - `remaining_goals` canonicos
     - placeholders/slots de branch
     - delta de sustitucion sobre ese espacio canonico
     - `subjudgments`
   - Ventaja: aprovecha la canonicalizacion ya existente, evita persistir UF
     crudo y permite reanudar branches de forma precisa.
   - Problema: exige definir con cuidado la identidad de los placeholders de
     branch.

Decision recomendada:

- avanzar con la **opcion 6**
- mantener `SessionState.bindings` como snapshot visible/contextual
- hacer que `PendingBranch` persista un entorno canonico propio de branch

### Analisis pendiente: identidad de placeholders

El cierre de esta fase depende de resolver bien la identidad de las variables
persistidas.

Debemos distinguir al menos tres espacios:

- **Placeholders publicos de query**
  - Son los placeholders que aparecen en el goal original.
  - Deben seguir siendo los unicos visibles en resultados publicos.

- **Placeholders contextuales de sesion**
  - Representan bindings compartidos por el contexto local.
  - Deben persistirse en `SessionState.bindings`.

- **Placeholders canonicos de branch**
  - Son placeholders/slots internos al environment persistido de una branch.
  - Deben ser estables dentro de la branch, pero no forman parte de la API
    publica.

La identidad recomendada para branch placeholders es:

- no basarse en owner ids efimeros
- no basarse en `repr(...)`
- si basarse en la canonicalizacion del estado de branch
- usar slots canonicos de branch como identidad primaria

En terminos practicos:

- `PendingBranch.subst` deberia persistirse como una tupla ordenada de
  bindings sobre slots canonicos de branch
- al reanudar, el kernel reconstruye un UF fresh usando:
  - `SessionState.bindings`
  - el delta de branch sobre esos slots canonicos

Esto deja a `UnionFind` como infraestructura efimera y a la branch como snapshot
semantico reanudable.

### Cambios de modelo

Archivos principales:

- `packages/protomorph/src/pm/reasoning/model.py`
- `packages/protomorph/src/pm/reasoning/tabling.py`

Acciones:

- Ampliar `PendingBranch` para que lleve suficiente contexto semantico para
  reanudar:
  - `blocked`
  - `remaining_goals`
  - `subst`
  - `subjudgments`
- Introducir un tipo ligero para items de frontier si hace falta
  (`FrontierItem`, `PendingGoal`, etc.).
- Hacer que `QueryTable` distinga claramente entre:
  - answers cerradas
  - deferreds presentes
  - branches pendientes reanudables
  - continuation_state operativo

### Cambios de solve

Archivos principales:

- `packages/protomorph/src/pm/reasoning/core.py`
- `packages/protomorph/src/pm/reasoning/query.py`

Acciones:

- Introducir `_resume_branch(...)` en `core.py`.
- `_rule_outcome(...)` y `_expanded_outcome(...)` deben persistir la sustitucion
  visible de branch, no solo los goals restantes.
- `_SessionSolveCore.run()` debe intentar primero la reanudacion directa de
  branches y usar root requery solo como fallback transitorio.
- `Result.resume()` debe reutilizar esa continuation semantica en vez de ser un
  simple alias de `continuation.result` sobre una query rehecha.

### Tests

Agregar o reforzar:

- `test_blocked_query_stores_pending_branch_with_remaining_goals`
- `test_branch_resume_uses_remaining_goals_without_root_requery`
- `test_branch_resume_accumulates_subjudgments`
- `test_blocked_query_with_multiple_branches_retries_only_unblocked_branch`

### Criterio de salida

- La continuation ya no es mayormente descriptiva.
- El solve ya reanuda branches usando su propio estado semantico.
- Root requery ya no es el camino principal; queda solo como red de seguridad residual.


## 5. Fase 2 - Coinduccion robusta

### Objetivo

Pasar de la heuristica actual de ciclos a una semantica mas robusta para ciclos
inductivos, coinductivos y mixtos.

### Estado actual

Esta fase ya tiene una primera implementacion solida:

- `CycleTrace` ya existe y captura miembros/tipo de ciclo
- la stack activa ya usa frames estructurados en vez de una heuristica minima
- ciclo coinductivo puro -> exito con `ByCoinduction` y `trace`
- mezcla inductivo/coinductiva -> `MixedCycle`
- borde negativo en el ciclo activo -> `NegativeCycle`

Lo pendiente aqui es refinar todavia mas la semantica para blockers o
contradicciones incompatibles dentro de ciclos mas complejos, pero la fase ya no
esta en modo heuristica minima.

### Cambios de modelo

Archivos principales:

- `packages/protomorph/src/pm/reasoning/model.py`
- `packages/protomorph/src/pm/reasoning/result.py`

Acciones:

- Introducir una representacion mas explicita de la traza de ciclo (`CycleTrace`
  o equivalente):
  - miembros del ciclo
  - tipo de ciclo
  - informacion coinductiva/inductiva
- Evaluar si `MixedCycle` y `NegativeCycle` publicos deben cargar esa traza.

### Cambios de solve

Archivo principal:

- `packages/protomorph/src/pm/reasoning/core.py`

Acciones:

- Reemplazar la heuristica actual por una evaluacion de ciclo mas explicita.
- Integrar la traza de ciclo al `Judgment` y al `QueryTable` cuando el ciclo
  quede abierto o provisional.
- Asegurar que un ciclo coinductivo no provoque exito espurio si aparecen
  blockers o contradicciones incompatibles.

### Tests

Agregar:

- `test_two_node_coinductive_cycle_succeeds`
- `test_coinductive_cycle_preserves_trace`
- `test_mixed_cycle_reports_members`
- `test_coinductive_cycle_with_negative_edge_is_rejected`

### Criterio de salida

- La coinduccion ya dejo de ser una heuristica minima.
- `MixedCycle` y `NegativeCycle` ya estan mejor delimitados.
- Los ciclos ya son inspeccionables y explicables via `CycleTrace`.


## 6. Fase 3 - Judgment y evidence uniformes

### Objetivo

Cerrar la capa de derivacion de forma consistente para answers, blockers y
resultados publicos.

### Estado actual

La mayor parte de esta fase tambien esta bastante avanzada:

- `Judgment` ya puede cargar `trace`
- `Unique`, `Ambiguous`, `Deferred`, `Floundered`, `MixedCycle`, `NegativeCycle`
  y `NoSolution` ya exponen juicios/evidence de forma mucho mas uniforme
- `retry_deferred()` ya preserva y compone `subjudgments` durante la
  continuation

Lo pendiente es mas de pulido que de arquitectura: decidir si conviene separar
un tipo `Evidence` explicito y seguir afinando algunos casos limite de fallo.

### Cambios de modelo

Archivos principales:

- `packages/protomorph/src/pm/reasoning/model.py`
- `packages/protomorph/src/pm/reasoning/result.py`

Acciones:

- Consolidar la estructura publica de `Judgment`.
- Evaluar si hace falta un tipo `Evidence` separado o si alcanza con `Spec` como
  valor navegable.
- Homogeneizar la exposicion publica:
  - `Unique.judgment`
  - `Ambiguous.judgments`
  - `Deferred.judgments`
  - `Floundered.judgments`
- Decidir si `NoSolution`, `MixedCycle` y `NegativeCycle` deben llevar una traza
  o juicio asociado.

### Cambios de solve

Archivo principal:

- `packages/protomorph/src/pm/reasoning/core.py`

Acciones:

- Asegurar que toda transicion importante produzca evidence consistente:
  - facts
  - rules
  - builtin/operators
  - negacion
  - deferred
  - coinduccion
- Mantener y extender subjudgments durante resume de branches.

### Tests

Agregar:

- `test_unique_exposes_judgment`
- `test_ambiguous_exposes_judgments`
- `test_deferred_preserves_branch_judgment`
- `test_rule_judgment_contains_subjudgments`
- `test_coinductive_judgment_contains_bycoinduction`

### Criterio de salida

- Answers, deferreds, ciclos y `NoSolution` ya tienen una historia de
  derivacion bastante coherente.
- La capa de evidence ya es util; lo pendiente es consolidacion y cleanup.


## 7. Fase 4 - EngineTables mas rica

### Objetivo

Decidir y materializar que conocimiento global reusable merece vivir en
`EngineTables`, sin invadir el dominio contextual de `Session`.

### Estado actual

Esta fase ya empezo con una ampliacion conservadora:

- `EngineTables` ya expone facts cerradas por anchor
- `EngineTables` ya expone facts cerradas por componente (`facts_by_component`)
- `EngineTables` ya expone derivadas por componente (`derived_facts_by_component`)

Sigue siendo una fase deliberadamente conservadora: aun no hay respuestas
globales no-ground ni tablas solver-heavy por SCC.

### Cambios de modelo

Archivos principales:

- `packages/protomorph/src/pm/reasoning/tabling.py`
- `packages/protomorph/src/pm/reasoning/engine.py`

Acciones:

- Evaluar si conviene introducir:
  - tablas globales por SCC
  - respuestas globales reusables mas ricas
  - metadata de cierre mas fina
- Mantener la regla de validez:
  - solo conocimiento global
  - canonizado
  - cerrado
  - independiente del contexto local

### Cambios de solve

Archivo principal:

- `packages/protomorph/src/pm/reasoning/core.py`

Acciones:

- Ampliar `_EngineSolveCore` solo despues de estabilizar continuation,
  coinduccion y judgments.
- No subir a `EngineTables` nada que dependa de bindings de sesion,
  continuation de query o blockers contextuales.

### Tests

Agregar:

- `test_engine_tables_expose_closed_component_results`
- `test_session_overlay_uses_engine_tables_without_recomputing_global`
- `test_global_tables_do_not_capture_contextual_answers`

### Criterio de salida

- `Engine` ya reduce trabajo real de las capas inferiores sin mezclar semantica
  local.
- Lo pendiente es decidir si conviene subir resultados globales mas ricos sin
  contaminar el dominio contextual.


## 8. Secuencia recomendada de ejecucion

Orden estricto recomendado:

1. Continuation operativa real
2. Coinduccion robusta
3. Judgment/evidence uniformes
4. `EngineTables` mas rica

Motivacion:

- la coinduccion necesita una continuation y branch state mas estables
- la evidence se beneficia de una continuation ya madura
- enriquecer `EngineTables` demasiado pronto puede contaminar el diseno local


## 9. Riesgos principales

- Persistir demasiada informacion de branch puede acercarse a persistir el
  `UnionFind` crudo.
- Hacer coinduccion robusta antes de estabilizar continuation puede introducir
  semantica fragil.
- Enriquecer `EngineTables` antes de estabilizar `Session` puede ocultar errores
  contextuales.


## 10. Criterio de cierre de URS

Consideraremos que URS esta practicamente cerrada cuando:

- `Session` ya no sea replay-driven.
- `QueryTable` y `Result.continuation` sean realmente reanudables.
- la coinduccion no dependa de heuristicas triviales.
- `Judgment` y la evidence sean coherentes en answers, deferreds y ciclos.
- `Engine` almacene solo conocimiento globalmente reusable, pero realmente util.
