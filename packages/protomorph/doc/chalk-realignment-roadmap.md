# Chalk Solver Realignment Roadmap

Este documento define la hoja de ruta de implementacion para realinear
`packages/protomorph/src/pm/chalk.py` con las expectativas originales de
`packages/protomorph/doc/solver-design.md` sin abandonar la arquitectura tipo
Chalk ya explorada.

El principio rector es conservar:

- `Spec` como unidad fundamental de hecho, regla y query
- goals canonicos como clave de cache/search graph
- un core mutable efimero para la resolucion
- una fachada publica compatible con el estilo query-oriented de protobase/flux

Y corregir estas desviaciones:

- no mezclar answers con estados bloqueados
- no colapsar floundering/deferred/ciclos mixtos en `Ambiguous`
- introducir una session compartida que permita retry de obligaciones
- modelar negacion con estratificacion explicita
- abrir puntos de extension basados en `Placeholder` para operaciones de tipo
  (`keyof`, projections, etc.)


## 1. Objetivos de realineacion

La implementacion debe crecer hacia este modelo:

- `Answer` representa solo una respuesta concreta con evidencia
- `Deferred` representa obligaciones bloqueadas pero reintentables
- `Floundered` representa goals bloqueados por falta de instanciacion suficiente
- `MixedCycle` y `NegativeCycle` representan problemas estructurales del solver,
  no respuestas ambiguas
- `Ambiguous` queda reservado a multiplicidad real de respuestas

El solver debe ofrecer una `Session` compartida para:

- acumular informacion entre varias consultas
- reintentar obligaciones diferidas
- modelar el estilo Rust de inferencia local dentro de cuerpos de funcion


## 2. Arquitectura objetivo

```text
ChalkSolver                     # fachada inmutable
    |
    +-- solve(goal)             # convenience sobre fresh session
    +-- session()               # crea session compartida

ChalkSession                    # motor mutable compartido por episodio
    - cache de goals cerrados
    - bindings compartidos de session
    - deferred queue
    - stratification plan
    - operator hooks
    |
    +-- solve(goal)
    +-- answers(goal)
    +-- retry_deferred()

GoalOutcome                     # resultado interno ortogonal
    - answers
    - deferred
    - cycle_issue
    - failed

DeferredGoal / Blocker          # contexto suficiente para reintentar
CycleIssue                      # mixed / negative
SolverOperator                  # Placeholder como punto de extension
```


## 3. Fases de implementacion

## Fase A - Session compartida y algebra de resultados

### Objetivo

Separar answers de estados bloqueados y de problemas de ciclo.

### Cambios

- Introducir `ChalkSession` como superficie mutable compartida.
- Hacer que `ChalkSolver.solve(goal)` sea sugar sobre una session fresh.
- Introducir un outcome interno con ejes separados:
  - `answers`
  - `deferred`
  - `cycle_issue`
  - `failed`
- Mantener `Answer` limpio: solo sustitucion + evidencia.

### Resultado esperado

- `Unique`, `Ambiguous`, `NoSolution`, `Deferred`, `Floundered`,
  `MixedCycle`, `NegativeCycle` quedan separados en la API publica.


## Fase B - Deferred y floundering con contexto reintetable

### Objetivo

Dejar de usar strings de razon para representar bloqueo.

### Cambios

- Introducir `BlockedGoal(goal, blocker)`.
- Introducir familia de `Blocker`:
  - `StratumPending`
  - `NonGroundNegation`
  - `OperatorPending`
  - `UnresolvedDependency` (reservado)
- Hacer que la session pueda reintentar deferreds cuyo blocker sea resoluble.

### Resultado esperado

- El solver puede responder `Deferred`/`Floundered` con suficiente contexto para
  operar despues.
- Esto sienta la base para obligaciones estilo Rust durante el analisis de
  bloques de funcion.


## Fase C - Estratificacion completa para negacion

### Objetivo

Sacar la negacion del modo top-down inmediato y alinearla con el modelo
estratificado del diseno original.

### Cambios

- Introducir `StratificationPlan` derivado de las reglas.
- Analizar dependencias positivas y negativas por anchor.
- Detectar ciclos negativos e invalidar el programa/goal con `NegativeCycle`.
- Evaluar `not G` solo si el estrato objetivo esta sellado/cerrado.
- Si no esta cerrado, devolver `Deferred(StratumPending(...))`.

### Resultado esperado

- Datalog con negacion ya no se comporta como simple negation-as-failure.
- La negacion se vuelve compatible con retry y cierre por estratos.


## Fase D - Placeholder como operadores logicos

### Objetivo

Usar `Placeholder` como punto de extension para operaciones de tipo y goals no
resolubles solo por pattern matching de reglas.

### Cambios

- Introducir `SolverOperator(pm.Placeholder)`.
- Hacer que el solver detecte operadores presentes en los terms de un goal.
- Si el backend no sabe resolverlos todavia, producir `Deferred(OperatorPending)`.
- Abrir el hook para futuros operadores como:
  - `KeyOfOp`
  - `ProjectionOp`
  - `IndexedAccessOp`

### Resultado esperado

- La arquitectura queda lista para TypeScript (`keyof`, conditionals, mapped
  types) y Rust (`T::Item`, impl selection, projections) sin redisenar el core.


## Fase E - Shared session para inferencia estilo Rust

### Objetivo

Permitir que varias consultas compartan contexto y bindings, en vez de resolver
cada query de forma aislada.

### Cambios

- La session mantiene bindings compartidos para placeholders visibles.
- Soluciones unicas pueden comprometerse en la session.
- Los goals diferidos quedan registrados y pueden reintentarse tras nueva
  informacion.

### Resultado esperado

- El solver se puede usar como motor de obligaciones locales en cuerpos de
  funcion.
- Casos como proyecciones o traits dependientes de tipos aun no inferidos dejan
  de aparecer como ambiguedad espuria.


## 4. Estrategia de tests

Los tests deben representar la expectativa deseada, no congelar el estado
accidental del experimento actual.

Reglas:

- corregir los tests que institucionalizan comportamiento desalineado
- agregar tests nuevos para resultados separados (`Deferred`, `Floundered`,
  `MixedCycle`, `NegativeCycle`)
- agregar tests de session compartida
- agregar tests expectation-first para operadores aun no implementados por
  completo, usando `expectedFailure` si hace falta

Ejemplos de tests objetivo:

- `test_non_ground_negation_flounders`
- `test_negative_cycle_reported_separately`
- `test_mixed_cycle_reported_separately`
- `test_session_shares_bindings_across_goals`
- `test_unhandled_operator_is_deferred`
- `test_keyof_deferred_until_structural_input_known` (`expectedFailure`)
- `test_projection_deferred_until_receiver_known` (`expectedFailure`)


## 5. Criterio de exito

La realineacion se considera encaminada cuando se cumpla lo siguiente:

- `Ambiguous` deja de usarse como catch-all
- existe `ChalkSession` compartida y operativa
- negacion usa estratificacion y deferreds reales
- mixed cycles y negative cycles son resultados distintos
- hay hook de operadores basado en `Placeholder`
- la suite de tests expresa la expectativa futura, aunque parte quede marcada
  como pendiente deliberadamente
