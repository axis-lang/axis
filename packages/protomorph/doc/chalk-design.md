# Chalk Solver Design - Contrapunto operativo a `solver-design.md`

Este documento describe el solver experimental implementado en
`packages/protomorph/src/pm/chalk.py` como una linea separada del diseno
general presentado en `packages/protomorph/doc/solver-design.md`.

La idea central es deliberadamente mas estrecha: no construir todavia un core
unificado para TypeScript, Datalog y Rust-style reasoning, sino una primera
arquitectura inspirada en Chalk que sea compatible con la filosofia de
inmutabilidad de protobase/protomorph y que valide varias decisiones de base.


## 1. Objetivo de esta variante

La variante Chalk busca responder una pregunta mas concreta que el documento
general:

> Como se ve un solver query-oriented, con fachada inmutable y core mutable
> interno, cuando `Spec` es la unidad fundamental de hecho, regla y query.

No intenta cubrir todavia todo el espacio del solver unificado. Su foco actual
es:

- reglas Horn positivas expresadas como `Rule(head: Spec, body: tuple[Spec, ...])`
- goals expresados como `Spec`
- matching estructural sobre carriers
- recursion inductiva con fixed-point local
- resultados resumidos como `Unique`, `Ambiguous` o `NoSolution`


## 2. Decisiones de diseno tomadas

## 2.1 `Spec` sigue siendo la unidad fundamental

La decision principal del documento general se mantiene intacta:

- las relaciones se representan como `Spec`
- los hechos son `Rule(head, ())`
- los sub-goals del body son `Spec`
- la query publica es `solve(goal: Spec)`

La diferencia no esta en la representacion de las relaciones, sino en la forma
de ejecutar la resolucion.


## 2.2 Fachada inmutable, core mutable interno

El solver publico sigue la forma de query derivada propia de `flux`:

```python
class ChalkDatabase(Consed, abstract=True):
    @flux.method
    def rules_for_goal(self, goal: pm.Spec) -> tuple[pm.Rule, ...]: ...


class RuleSet(ChalkDatabase):
    rules: tuple[pm.Rule, ...] = ()


class ChalkSolver(Consed):
    db: ChalkDatabase

    @flux.method
    def solve(self, goal: pm.Spec) -> ChalkResult: ...
```

Consecuencias:

- el objeto publico del solver no expone `pending`, `known`, `subst` ni frames
- el estado mutable vive solamente dentro de `_Core`
- la cache publica queda alineada con `flux.method`
- el "universo" de reglas permanece como dato inmutable (`RuleSet` o un
  backend equivalente)

Esto contrasta con `solver-design.md`, donde el primer borrador del solver se
presenta como un objeto con estado operativo explicito (`pending`, `deferred`,
`known`, `subst`).


## 2.3 Sin `freshen_rule`

Esta es una de las decisiones mas importantes de la variante Chalk.

El solver actual de `packages/protomorph/src/pm/solver.py` usa `freshen_rule()`
para clonar placeholders por aplicacion de regla. La variante Chalk no hace eso.

En su lugar:

1. cada regla se compila una sola vez a una plantilla con `_TemplateVar(slot)`
2. cada aplicacion de la regla materializa vars runtime como
   `_RuntimeVar(kind="rule", owner, slot)`
3. las vars visibles del query se representan como
   `_RuntimeVar(kind="goal", owner=0, slot)`

En otras palabras, la frescura deja de ser "copiar la regla" y pasa a ser
"instanciar un scope runtime".

Beneficios:

- no hay reescritura eager de reglas
- la identidad de vars de regla depende del frame de aplicacion, no de un
  contador global de freshening
- la regla fuente permanece como dato estable y consed


## 2.4 Query canonicalization como frontera interna

Antes de resolver un sub-goal, el core lo canonicaliza:

- reifica bindings actuales
- renumera vars libres a `_GoalSlot(slot)`
- usa el `Spec` canonico como clave del search graph

Esto cumple el papel de "canonical query" de Chalk:

- permite detectar ciclos semanticamente equivalentes
- hace estable la clave de cache interna
- desacopla la semantica de la identidad nominal accidental de las vars


## 2.5 Search graph local y fixed-point para ciclos inductivos

La variante Chalk no usa un obligation loop con `pending/deferred`, sino un
solver recursivo con search graph local:

- `_nodes: dict[pm.Spec, _SearchNode]`
- cada nodo guarda una solucion parcial actual
- si un goal reaparece mientras el nodo esta activo, se detecta ciclo
- el core vuelve a iterar hasta alcanzar fixed-point o ambiguedad

Esto esta mas cerca del recursive solver de Chalk que del bosque de obligaciones
del diseno general.


## 2.6 Unificador local, no `pm.unify`

Aunque `pm.unification.py` sigue siendo el kernel general de unificacion, la
variante Chalk usa unificador propio dentro de `pm/chalk.py`.

La razon es de modelo de variables:

- `pm.unify` opera sobre placeholders/carriers reales
- el solver Chalk opera sobre `_RuntimeVar`, `_TemplateVar` y `_GoalSlot`
- por lo tanto, necesita unificacion aware de scopes runtime

Propiedades del unificador actual:

- stack-based
- occurs check activo
- vars enlazadas por `_Bindings`
- leaves comparados por descriptor + igualdad de valor
- nodos no-leaf comparados por aridad y estructura de hijos


## 2.7 Resultado resumido, no enumeracion completa

La salida publica actual es:

- `Unique(goal, subst)`
- `Ambiguous(goal, subst, reason)`
- `NoSolution(goal, reason)`

La semantica actual es intencionalmente limitada:

- si hay exactamente una solucion estable, se devuelve `Unique`
- si hay varias pruebas o el fixed-point deja la respuesta subdetermina, se
  devuelve `Ambiguous`
- si no hay prueba, se devuelve `NoSolution`

No se enumeran respuestas una por una.


## 3. Estado actual de desarrollo

## 3.1 Componentes implementados

En `packages/protomorph/src/pm/chalk.py` ya existen:

- `ChalkDatabase`
- `RuleSet`
- `ChalkSolver`
- `ChalkResult`, `Unique`, `Ambiguous`, `NoSolution`
- `_Core` como loop mutable interno
- `_Bindings` como entorno mutable de bindings runtime
- compilacion de reglas a templates
- instanciacion runtime por `owner/slot`
- canonicalizacion de goals
- search graph local con fixed-point para recursion inductiva


## 3.2 Cobertura funcional actual

La suite en `packages/protomorph/tests/pm2/test_chalk.py` valida hoy:

- facts simples
- chaining de reglas
- variables compartidas a traves de sub-goals
- reflexividad (`Eq(T, T)`) como regla general
- recursion con base case que degenera en `Ambiguous`
- recursion sin base case que termina en `NoSolution`
- no aliasing de vars entre aplicaciones repetidas de una misma regla

Ademas, la suite `pm2` completa sigue pasando con esta implementacion presente.


## 3.3 Forma actual de indexacion

`RuleSet` implementa un primer nivel de indexacion por anchor:

- `rules_by_anchor`
- `rules_for_goal(goal)`

Esto ya separa el backend de reglas del core del solver, pero todavia es una
forma minima de indexing.


## 4. Diferencias explicitas contra `solver-design.md`

## 4.1 No hay solver unificado por dominios

`solver-design.md` plantea una unica arquitectura que eventualmente soporte:

- algebra de tipos estilo TypeScript
- Datalog
- Rust-style resolution

La variante Chalk no intenta eso todavia. Es un solver top-down para reglas
positivas sobre `Spec`, sin estrategias por dominio.


## 4.2 No hay `Deferred`

El documento general reserva un lugar central para goals bloqueados y reintento.

La variante Chalk actual no implementa esa capa. En particular:

- no existe `Deferred` como resultado publico
- no hay floundering explicito
- no hay retry de goals bloqueados
- la ambiguedad actual resume tanto multiples pruebas como falta de precision


## 4.3 No hay rollback por rama ni impl selection

El documento general piensa en backtracking con snapshots y rollback sobre un
estado compartido.

La variante Chalk evita ese problema por otro camino:

- cada aplicacion de regla trabaja con un `_Bindings` local
- los bindings de una rama no se comprometen globalmente
- la combinacion entre ramas ocurre a nivel de resultados, no via rollback de un
  `UnionFind` compartido


## 4.4 No hay `Judgment` ni `Evidence`

El documento general reserva una capa para `Judgment` y trazas de derivacion.

La variante Chalk no implementa eso. Solo devuelve:

- el `goal`
- una substitucion visible
- una clasificacion (`Unique`, `Ambiguous`, `NoSolution`)


## 4.5 No hay multi-answer enumeration

El diseno general deja abierta la puerta a un solver que eventualmente enumere
derivaciones o respuestas.

La variante Chalk toma una posicion mas estricta por ahora:

- si hay mas de una respuesta observable, devolver `Ambiguous`
- no exponer iteradores de soluciones
- no modelar aun `solve_multiple()` ni answers sucesivas


## 5. Restricciones actuales deliberadas

Estas restricciones no son bugs accidentales; son recortes de alcance
intencionales para la primera iteracion:

- Sin negacion.
- Sin evidence.
- Sin coinduction real; `is_coinductive()` queda como hook futuro.
- Sin multiple-answer enumeration; cuando haya mas de una respuesta, devolver
  `Ambiguous`.

Tambien quedan fuera por ahora:

- estrategias por dominio
- clause synthesis dinamico estilo Chalk/Rust
- normalizacion diferida
- goals negativos
- strata para Datalog
- projections y alias resolution estilo Rust


## 6. Mapa de arquitectura actual

```text
ChalkDatabase / RuleSet        # mundo inmutable de reglas
        |
        v
ChalkSolver.solve(goal)        # query publica con flux
        |
        v
_Core                          # estado mutable local a una invocacion
  - _compiled_rules
  - _nodes
  - _next_owner
        |
        +-- _compile_rule()    # placeholders -> _TemplateVar(slot)
        +-- _canonicalize()    # vars libres -> _GoalSlot(slot)
        +-- _apply_rule()      # _TemplateVar -> _RuntimeVar(rule, owner, slot)
        +-- _unify()           # unificacion local sobre carriers
        +-- _combine_solutions()
```

Puntos importantes:

- las reglas siguen siendo datos estaticos
- los scopes runtime son internos al core
- la base de conocimiento derivada no sale del core
- el resultado publico vuelve a ser un dato inmutable


## 7. Objetivos pendientes

## 7.1 Objetivos inmediatos

- Exportar o integrar el solver Chalk en la superficie publica de `pm` cuando la
  API se estabilice.
- Mejorar la precision de `Ambiguous.subst` para conservar guidance parcial util.
- Introducir una capa de backend mas rica que `RuleSet`, manteniendo la forma
  `rules_for_goal(goal)`.
- Documentar con mas detalle la semantica de ciclos e invariantes del core.


## 7.2 Objetivos de semantica

- Incorporar floundering/deferral explicito en vez de colapsar todo a
  `Ambiguous`.
- Introducir evidence/judgments cuando el modelo de derivacion este mas claro.
- Explorar coinduction real usando `is_coinductive()` como punto de extension.
- Definir como conviviran subtyping, projections y clause synthesis en esta
  arquitectura.


## 7.3 Objetivos de interoperacion con el diseno general

- Decidir si esta linea Chalk reemplaza o complementa al futuro solver unificado.
- Decidir si el search graph local debe convivir con un obligation loop mas
  general.
- Evaluar si `pm.unify` y el unificador local deben converger sobre una
  abstraccion comun de variables scoped.
- Determinar si `Rule` debe permanecer como builtin separado o si debe acercarse
  mas al modelo "Rule como Spec" planteado en el documento general.


## 7.4 Hoja de ruta para completar la implementacion actual

La recomendacion actual es no reescribir `pm/chalk.py`, sino abrir tres seams
internas y luego completar las features pendientes en este orden:

1. literals en bodies
2. respuestas/evidence internas
3. politica explicita de ciclos

Sobre esa base, la secuencia recomendada es:

### Fase 0 - Refactor preparatorio

Antes de agregar nueva semantica conviene generalizar tres puntos internos:

- `_CompiledRule.body` debe pasar de `tuple[pm.Carrier, ...]` a una secuencia de
  literales compilados
- `_InternalSolution` debe separarse de la representacion concreta de answers
- `_SearchNode` debe poder distinguir mejor entre resultado actual y politica de
  ciclo

El objetivo de esta fase es mantener intacta la API publica actual:

- `ChalkSolver.solve(goal)` sigue existiendo
- `_Core` sigue siendo el loop mutable local
- la canonicalizacion de goals sigue siendo la frontera semantica interna


### Fase 1 - Negacion

La primera extension recomendada es introducir negacion de manera acotada.

Direccion propuesta:

- representar negacion publicamente como un `Spec`, por ejemplo
  `Spec.of("std.logic.Not", goal)`
- compilar el body de una regla a literales positivos/negativos
- evaluar un literal negativo con semantica estratificada minima:
  - `NoSolution(subgoal)` => exito del literal negativo
  - respuesta positiva del subgoal => fallo del literal negativo
  - subgoal no ground o ambiguo => `Ambiguous`/floundering

Alcance deliberado de la primera iteracion:

- sin negacion general
- sin recursion negativa
- sin mezclar aun negacion con coinduction

Tests objetivo:

- negacion de un hecho
- regla con literales positivos + negativos
- negacion no ground => ambiguedad explicita
- ciclo negativo => rechazado o ambiguo


### Fase 2 - Evidence

La segunda extension recomendada es incorporar evidencia estructurada.

Direccion propuesta:

- modelar evidencia tambien como datos navegables, idealmente usando `Spec`
- cada respuesta interna debe cargar una prueba estructurada, no solo una
  sustitucion visible
- `Unique` debe poder devolver evidencia; `Ambiguous` puede devolver evidencia
  parcial o multiples pruebas resumidas

Una taxonomia minima de evidencia podria ser:

- `std.logic.ByFact`
- `std.logic.ByRule`
- `std.logic.ByNegation`
- `std.logic.ByCoinduction`

Razon para este orden:

- la evidencia es util para depurar negacion
- la coinduction necesitara representar supuestos/proofs provisionales
- la enumeracion multiple necesitara adjuntar evidencia por answer

Tests objetivo:

- evidencia de hecho simple
- evidencia anidada para chaining
- evidencia de negacion cuando el subgoal falla


### Fase 3 - Coinduction

La tercera extension recomendada es activar `is_coinductive()` y distinguir
ciclos inductivos de coinductivos.

Direccion propuesta, alineada con Chalk:

- ciclos inductivos: seed negativo y busqueda de least fixed-point
- ciclos coinductivos: seed positivo identidad y busqueda de greatest fixed-point
- ciclos mixtos inductivo/coinductivo: rechazarlos o tratarlos como ambiguos en
  la primera iteracion

Cambios internos necesarios:

- `_SearchNode` debe saber si el goal es coinductivo
- el stack activo debe poder distinguir revisitas coinductivas de revisitas
  inductivas
- no se deben cachear como definitivos resultados provisionales de un ciclo
  coinductivo antes de refinar/cerrar el ciclo

Tests objetivo:

- `C :- C` coinductivo => exito
- `C :- C` inductivo => `NoSolution`
- ciclo mixto => `Ambiguous` o no soportado
- caso coinductivo con constraints incompatibles => no debe producir un exito
  espurio


### Fase 4 - Enumeracion de multiples respuestas

La ultima extension recomendada es generalizar el motor de un resumen de una
sola respuesta a una coleccion de answers.

Direccion propuesta:

- introducir una representacion interna `_Answer(subst, evidence, ...)`
- agregar una API publica nueva (`answers(goal)` o `solve_all(goal)`)
- mantener `solve(goal)` como wrapper resumido:
  - cero respuestas => `NoSolution`
  - una respuesta => `Unique`
  - mas de una respuesta => `Ambiguous`

La primera version no necesita llegar a un SLG solver on-demand completo.
Alcanza con una enumeracion eager, finita y deduplicada por sustitucion visible
canonizada.

Tests objetivo:

- dos hechos compatibles => dos answers
- dos pruebas de la misma sustitucion visible => dedupe o merge controlado
- ejemplo recursivo finito con varias respuestas
- `solve(goal)` preserva la semantica resumida actual


### Orden recomendado y dependencias

El orden propuesto no es arbitrario:

1. negacion fuerza la introduccion de la capa de literals
2. evidence conviene antes de coinduction para poder representar supuestos y
   derivaciones parciales
3. coinduction conviene antes de enumeracion para no tener que redisenar dos
   veces la politica de ciclos
4. enumeracion multiple es la generalizacion mas amplia y debe hacerse al final

En particular, hay un principio de conservacion de arquitectura:

- preservar `ChalkSolver.solve(goal)` como entrada principal
- preservar `_Core` como motor mutable por query
- preservar goals canonicos como clave de search graph
- evolucionar incrementalmente la implementacion actual en vez de reemplazarla
  por un forest/SLG solver nuevo


## 8. Conclusion

El solver de `pm/chalk.py` no es la implementacion del documento general, sino
una contraprueba arquitectonica.

Lo que ya valida es lo siguiente:

- `Spec` funciona como pieza central de asercion y consulta
- se puede evitar `freshen_rule` si la identidad variable se modela por scopes
  runtime
- se puede alinear el solver con `flux` usando fachada inmutable y core mutable
  privado
- recursion inductiva y ambiguedad ya pueden modelarse sin obligation loop

Lo que todavia no valida es igual de importante:

- no cubre negacion, evidence, coinduction ni enumeracion multiple
- no cubre aun la coexistencia completa de TypeScript, Datalog y Rust-style
  reasoning
- no reemplaza todavia al diseno general; solo reduce el riesgo tecnico de sus
  decisiones fundamentales
