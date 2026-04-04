# Solver Asimétrico Híbrido

## Planteamiento

Los sistemas de unificación clásicos (Prolog, Datalog, union-find) operan bajo **unificación simétrica**: ambos lados de una ecuación pueden contener variables libres, y el algoritmo busca el *most general unifier* que las satisfaga simultáneamente. Esto requiere occur check, trailing de bindings, y en el caso general no garantiza terminación.

El **pattern matching asimétrico** invierte la asimetría ontológica: el patrón es la ley, el sujeto es el dato. Solo el patrón tiene variables; el sujeto es ground. El resultado es un recorrido único, sin backtracking estructural, sin occur check, terminación garantizada.

Este documento describe un diseño intermedio: un **solver asimétrico híbrido** donde:

- El **patrón** puede contener variables de captura, wildcards, literales, y **nodos de control** (switch, alt, guard, seq).
- El **sujeto** puede contener **variables hoja** (*leaf vars* / slots) — posiciones sin valor conocido que el matcher captura como dato en lugar de fallar.
- Los patrones se **compilan a un IR** antes de ejecutarse, permitiendo reutilización y optimización.

La asimetría se mantiene: el patrón *dirige*, el sujeto *obedece*.

---

## Arquitectura en capas

```
┌─────────────────────────────────────────────────┐
│              Lenguaje de patrones                │
│  Var(?x) · Lit(v) · Ctor(tag,[sub]) · Wild(_)  │
│  Guard(pred) · Switch([arms]) · And · Or        │
└────────────────────┬────────────────────────────┘
                     │ compilación
┌────────────────────▼────────────────────────────┐
│              Pattern IR compilado                │
│  instrucciones lineales · tabla de dispatch     │
│  índices de salto · bloques de alternativas     │
└────────────────────┬────────────────────────────┘
                     │ ejecución
┌────────────────────▼────────────────────────────┐
│                 Matcher VM                       │
│  stack de cursores · env de ligados             │
│  variables hoja del sujeto → slots              │
└────────────────────┬────────────────────────────┘
                     │ inspección
┌────────────────────▼────────────────────────────┐
│          Sujeto con variables hoja              │
│  f(a, ?y, g(?z))                               │
│  ?y y ?z son slots sin valor → se propagan     │
└─────────────────────────────────────────────────┘
```

---

## Nodos del IR

### Captura y comparación

| Nodo | Semántica | Caso de uso |
|---|---|---|
| `Bind(?x)` | liga el cursor actual a `?x` en el env | captura de variables; siempre tiene éxito |
| `Lit(v)` | cursor == v, o falla | literales y átomos concretos |
| `Wild` | siempre tiene éxito, no liga | `_` en ML; placeholder |

### Navegación estructural

| Nodo | Semántica | Caso de uso |
|---|---|---|
| `Ctor(tag, arity)` | verifica tag y aridad del Term actual | despacha la forma del sujeto |
| `Enter(i)` | empuja el hijo i al stack de cursores | descenso sin recursión |
| `Exit` | vuelve al padre en el stack | ascenso tras procesar un hijo |

### Control de flujo

| Nodo | Semántica | Caso de uso |
|---|---|---|
| `Switch({tag: bloque})` | dispatch O(1) por tag del nodo actual | múltiples constructores; equivale a `case` compilado |
| `Guard(fn)` | evalúa `fn(env) → bool`; falla si False | predicados arbitrarios post-matching |

### Variables hoja del sujeto

| Nodo | Semántica | Caso de uso |
|---|---|---|
| `SlotBind(?x)` | el cursor es una `Var` hoja → `env[?x] = Var` | sujeto parcialmente desconocido; el slot se propaga |

### Combinadores lógicos

| Nodo | Semántica | Caso de uso |
|---|---|---|
| `Seq([instrs])` | falla si cualquier instrucción falla | and-pattern; vista compuesta |
| `Alt([bloques])` | devuelve el primer bloque que tiene éxito | or-pattern; múltiples formas alternativas |

---

## Términos y entorno

```python
# Nodo estructural con tag y children (ground o Var en hoja)
Term(tag: str, children: tuple)

# Variable — puede aparecer en el patrón (captura) o en el sujeto (slot)
Var(name: str)

# Entorno resultante del matching
Env = dict[str, Value]
# donde Value puede ser: Atom | Term | Var (slot sin resolver)
```

La distinción clave: cuando el resultado contiene una `Var` como valor en el env, el caller sabe que esa posición del sujeto está **aún sin determinar**. Puede pasarla a otro sistema (solver de restricciones, otra regla, una base de datos) sin romper la invariante de asimetría.

---

## El compilador de patrones

El compilador toma un patrón de alto nivel y produce una tupla de instrucciones IR. El patrón se compila **una sola vez** y se reutiliza en cada llamada al matcher.

Formas de alto nivel reconocidas:

```python
Var("x")                          # → IRBind("x")
'_'                               # → IRWild()
42  /  "hola"                     # → IRLit(v)
Term("f", (Var("x"), Var("y")))   # → IRCtor + IREnter/Exit por hijo

('switch', {'tag': sub_pat, ...}) # → IRSwitch con tabla de dispatch
('alt',    pat1, pat2, ...)       # → IRAlt con checkpoint/rollback
('guard',  sub_pat, pred_fn)      # → compila sub_pat + IRGuard
('and',    pat1, pat2)            # → concatena ambas compilaciones
('slot',   "nombre")              # → IRSlotBind — espera Var en sujeto
```

---

## La VM de matching

La VM mantiene un **stack de cursores** (posición actual en el árbol del sujeto) y un **env** mutable. Las instrucciones se ejecutan linealmente; cualquier fallo lanza una excepción que se captura en los puntos de elección (`Alt`).

```
estado VM:
  cursor_stack: [nodo_actual, padre, abuelo, ...]
  env: {nombre → valor_o_slot}

instrucción IREnter(i):  push(cursor.children[i])
instrucción IRExit:      pop()
instrucción IRBind(n):   env[n] = current()  (o verifica si ya está)
instrucción IRSwitch:    lookup(current().tag) → salta al bloque
instrucción IRAlt:       checkpoint(env) → prueba bloques → rollback si fallan
instrucción IRSlotBind:  assert isinstance(current(), Var); env[n] = current()
```

El resultado es `Env | None`. Sin excepciones visibles al caller.

---

## El solver (reglas con patrones compilados)

Las reglas declaran una cabeza (template con `Var`s) y un cuerpo (lista de `(relación, patrón)`). Los patrones del cuerpo se compilan en el constructor de la regla, no en cada evaluación.

```python
Rule(
    name="trans",
    head_template=Term("reach", (Var("x"), Var("z"))),
    body=[
        ("edge",  Term("edge",  (Var("x"), Var("y")))),
        ("reach", Term("reach", (Var("y"), Var("z")))),
    ]
)
```

El solver implementa un **fixpoint seminaïve**: itera hasta que no se derivan hechos nuevos. Garantías:

- Termina si las relaciones son finitas.
- No requiere occur check.
- Variables ya ligadas en el env actúan como literales en el siguiente patrón del cuerpo (matching no-lineal automático).

---

## Propiedades del diseño

### Lo que se preserva de pattern matching puro

- El sujeto nunca introduce bindings nuevos en el patrón — la asimetría se mantiene.
- Sin occur check.
- Un solo recorrido estructural por nodo del sujeto.
- Terminación garantizada en el solver si las relaciones son finitas.

### Lo que se añade respecto a pattern matching puro

- **Variables hoja en el sujeto**: posiciones sin valor se capturan como slots en el env, en lugar de causar fallo. Permite razonar sobre sujetos parcialmente conocidos.
- **IR compilado**: el patrón es un programa, no un árbol interpretado en cada uso. El `Switch` compila a dispatch O(1); los `Guard`s se ejecutan solo tras validar la estructura.
- **Nodos de control**: `Alt` y `Seq` son combinadores de primer orden en el IR, no azúcar sintáctico del lenguaje host.
- **Matching no-lineal**: una variable del patrón que aparece dos veces exige que ambas ocurrencias liguen al mismo valor. Se implementa verificando el env antes de escribir.

### Lo que no se hace (diferencia con unificación)

- El sujeto nunca unifica con el patrón — no hay `most general unifier` bilateral.
- No hay trailing lógico ni union-find.
- Las `Var` hoja del sujeto son datos opacos para el matcher; no se resuelven internamente.

---

## Extensiones naturales

**Modos al estilo Mercury**: anotar cada argumento de una relación como `in` (ground) u `out` (slot). El compilador puede entonces verificar estáticamente que los sujetos cumplen la invariante, y generar código más eficiente para los argumentos `in`.

**E-matching**: extender `IRSwitch` con una tabla de clases de equivalencia (e-graph). El dispatch ya no es por tag exacto sino por clase — permite matching módulo ecuaciones sin perder el O(1) en el caso común. Base de equality saturation (egg, egglog).

**Solver de restricciones para slots**: los slots capturados en el env pueden alimentarse a un CLP (constraint logic programming) externo. El matcher produce el env parcial; el solver de restricciones cierra los slots bajo las restricciones declaradas.

**Exhaustiveness checking estático**: dado el conjunto de patrones compilados para una relación, verificar en tiempo de compilación que todo posible sujeto es cubierto por al menos un patrón. Requiere un análisis de los `IRSwitch` y `IRAlt` en el IR.

**Índices sobre hechos**: para relaciones grandes, indexar los hechos por el tag del primer argumento. El `fixpoint` deja de iterar sobre todos los hechos y solo consulta el bucket relevante — equivalente a la first-argument indexing de Prolog, pero explícito en el solver.

---

## Referencias conceptuales

- **Maranget (2008)** — *Compiling Pattern Matching to Good Decision Trees*. Base del algoritmo de compilación de patrones a switches.
- **Ullman (1988)** — *Principles of Database and Knowledge-Base Systems*. Fundamentos de Datalog y fixpoint seminaïve.
- **Winterbottom / Frühwirth** — Constraint Handling Rules (CHR). Antecedente de solvers híbridos con matching asimétrico.
- **Willsey et al. (2021)** — *egg: Fast and Extensible Equality Saturation*. E-matching como extensión natural del matching asimétrico.
- **Henderson et al. (1996)** — *The Mercury Language*. Sistema de modos como solución al problema de asimetría en lenguajes lógicos.
