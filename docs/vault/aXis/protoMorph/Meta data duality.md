Excelente tema de diseño. Voy a reflexionar sobre tu esbozo, identificar qué está bien, qué queda vago, y proponer una formalización más precisa.

---

## Lo que capturo de tu intuición

La idea central es: **el par `(index, values)` de Struct y el par `(__type__, __data__)` de Val son instancias del mismo patrón `(meta, data)`**, y ese patrón debería ser recursivo -- el meta es él mismo un par (meta, data).

Esto colapsa la dualidad `Type`/`Val` en una sola estructura auto-similar: `Pure[M, D]`.

### Lo que ya funciona bien en tu esbozo

1. **MetaStruct como "meta = MetaIndex + field metas"** -- esto es exactamente la unificación de lo que hoy son dos cosas separadas:
   - `StructType.meta_attrs: Struct[str, Type]` (que tiene index + values)
   - Se convierte en: `MetaStruct.__meta__ = MetaIndex` (el index) + `MetaStruct.__data__ = tuple[Meta, ...]` (los field metas)

2. **StructMixin para ambos niveles** -- tanto MetaStruct (struct de metas) como Struct (struct de valores) comparten la interfaz `.index`, `.values`, `.get()`, `.map()`, etc. Esto es limpio.

3. **Spec como variante de la misma estructura** -- MetaSpec es esencialmente un MetaStruct para los argumentos de especialización.

---

## Problemas abiertos y propuestas

### 1. Grounding: el `??` en `MetaIndex[K](Meta[??, tuple[K, ...]])`

La cadena meta es recursiva: todo Meta tiene un meta. Tiene que terminar en algún punto. Hay tres opciones:

| Estrategia | Ejemplo | Pros | Contras |
|---|---|---|---|
| **Auto-referencial** | `Ground.__meta__ = Ground` | Simple, como `type(type) is type` en Python | Requiere romper el ciclo en construcción |
| **None terminal** | `MetaIndex.__meta__ = None` | Sin ciclos | Pierde uniformidad -- ya no todo es `Pure[M, D]` |
| **Universos** | Meta₀ : Meta₁ : Meta₂ ... | Formalmente limpio | Overengineering para runtime |

Mi propuesta: **auto-referencial con Ground singleton**.

```python
class Ground(Meta):
    """Terminal meta. Se clasifica a sí mismo."""
    # __meta__: Ground  (self-referential)
    # __data__: None
    pass

GROUND = Ground(GROUND, None)  # bootstrap singleton
```

Entonces:
```python
MetaIndex[K](Meta[Ground, tuple[K | None, ...]])
#  __meta__ = GROUND
#  __data__ = (None, "x", "y", None)  -- las keys
```

### 2. El invariante de alineación

Este es el corazón del modelo. Para que `Pure[M, D]` sea coherente, necesitamos una regla que diga **cómo M describe D**:

```
align(Ground, None)                     -- trivial
align(MetaAtom[T], x)                   -- x: T  (validación host)
align(MetaAnchor, s)                    -- s: str
align(MetaStruct[K, (M₁..Mₙ)], (D₁..Dₙ)) -- align(Mᵢ, Dᵢ) ∀i
```

Esto es exactamente `schema` del README, reificado como regla sobre Pure:

```
schema(Pure[M, D]) = M
schema preserva estructura: 
  schema(Struct[..., (d₁..dₙ)]) = MetaStruct[K, (schema(d₁)..schema(dₙ))]
```

La alineación también implica un invariante de longitud:
```
len(meta.__meta__.__data__) == len(meta.__data__) == len(self.__data__)
     ^^^^^^^^^^^^^^^^            ^^^^^^^^^^^^^^        ^^^^^^^^^^^^^
     keys                        field metas           field values
```

### 3. Datos compuestos: Spec y la cuestión de la heterogeneidad

Tu notación `Spec[K, *S](Pure[MetaSpec[K, *S], tuple[str, tuple[*S]]])` tiene un problema de niveles. En `MetaSpec`, `*S` son Metas (clasificadores). En `Spec.__data__`, `*S` deberían ser los datos clasificados por esos metas, no los metas mismos.

Propongo separar con claridad:

```python
# MetaSpec describe la forma de los args
MetaSpec[K](MetaStruct[K, Meta])
# Es un MetaStruct cuyos field-metas son Metas genéricos
# __meta__: MetaIndex[K]   -- las keys de los args
# __data__: tuple[Meta, ...] -- los metas de cada arg
```

Para Spec hay dos opciones de diseño:

**Opción A: Spec como Struct especial con anchor como primer campo**
```python
# Un Spec ES un Struct con semántica especial:
#   campo 0 (positional): anchor (clasificado por MetaAnchor)
#   campos 1..n: args (clasificados por sus metas)

Spec = Struct donde __meta__ = MetaStruct[
    keys=(None, k₁, k₂, ...),     # anchor es positional
    field_metas=(MetaAnchor, M₁, M₂, ...)
]
```

**Opción B: Spec como Pure dedicado con data compuesto**
```python
class Spec(Pure[MetaSpec, tuple[str, tuple[Data, ...]]]):
    # __meta__: MetaSpec  -- describe los args
    # __data__: (anchor_path, (arg₁_data, arg₂_data, ...))
```

La opción A es más fiel a "todo es structural", pero mezcla anchor con args. La opción B es más clara semánticamente pero introduce un data compuesto ad-hoc.

Yo me inclino por **una variante de A**: Spec no es un Struct sino un Pure cuyo meta es un *par* de (MetaAnchor, MetaStruct), lo que lleva a...

### 4. Producto de Metas (MetaPair / MetaTuple)

Para Spec necesitamos que el meta describa un data compuesto `(anchor, args)`. Esto sugiere un meta producto:

```python
MetaPair[A: Meta, B: Meta](Meta[Ground, tuple[A, B]])
# __meta__ = GROUND
# __data__ = (meta_a, meta_b)
# Clasifica: tuple[D_A, D_B] donde align(A, D_A) y align(B, D_B)
```

Entonces:
```python
# Spec
MetaSpec[K] = MetaPair[MetaAnchor, MetaStruct[K, Meta]]
# __data__ = (MetaAnchor_instance, MetaStruct_instance)

Spec(Pure[MetaSpec[K], tuple[str, tuple[Data, ...]]])
# __meta__.__data__[0] = MetaAnchor  -> clasifica __data__[0] = str
# __meta__.__data__[1] = MetaStruct  -> clasifica __data__[1] = tuple[...]
```

Pero esto es... esencialmente un MetaStruct con dos campos. Así que volvemos a: **MetaPair es un caso especial de MetaStruct con dos campos posicionales**. Todo es structural.

### 5. Mapa completo: Protomorph actual -> Pure

| Actual | Pure | Meta |
|---|---|---|
| `Val(__type__, __data__)` | `Pure[M, D]` | `M` reemplaza `__type__` |
| `Type` | `Meta` | Meta es un Pure que clasifica |
| `StructType(meta_attrs)` | `MetaStruct[K, V]` | `__meta__=MetaIndex`, `__data__=field_metas` |
| `Struct(index, values)` | `Struct[M, D]` (Pure) | `__meta__=MetaStruct`, `__data__=field_values` |
| `Struct.Index(keys)` | `MetaIndex[K]` | Contenido en `MetaStruct.__meta__` |
| `NominalType(spec_ref)` | `MetaNominal` | Meta[Ground, Spec] -- el spec ref ES el data |
| `NominalQualifier(spec, underlying)` | `MetaQual` | Meta[MetaPair[...], (spec, underlying_meta)] |
| `Anchor(segments)` | `Anchor` | Pure[MetaAnchor, str] |
| `Spec(anchor, args)` | `Spec` | Pure[MetaSpec, (str, args_data)] |
| `Const[T]` | desaparece | todo es `Pure` -- no hay distinción Const vs Val |
| `Literal` | `Pure[MetaAtom[T], T]` | int/str/bool son Pure con MetaAtom |

### 6. La torre completa para un ejemplo concreto

Valor: `struct(x=42, y="hello")`

```
Struct:
  __meta__: MetaStruct
    __meta__: MetaIndex
      __meta__: GROUND
      __data__: ("x", "y")          # las keys
    __data__: (MetaInt, MetaStr)     # los field metas
  __data__: (42, "hello")           # los field values

Alineación:
  keys[0]="x", meta[0]=MetaInt,  data[0]=42       ✓ align(MetaInt, 42)
  keys[1]="y", meta[1]=MetaStr,  data[1]="hello"  ✓ align(MetaStr, "hello")
```

Valor nominal: `NominalType("std.types.Integer")` (como clasificador de `42`)

```
Pure[MetaNominal, Spec[...]]
  __meta__: MetaNominal
    __meta__: GROUND
    __data__: None
  __data__: Spec
    __meta__: MetaSpec (con MetaStruct vacío para args)
    __data__: ("std.types.Integer", ())
```

---

## Preguntas abiertas para ti

1. **Ground auto-referencial** -- te convence, o preferirías `None` como terminador?

2. **MetaPair vs todo-es-MetaStruct** -- Spec y NominalQualifier tienen data compuesto. Creamos MetaPair como primitiva, o siempre modelamos data compuesto como "un struct posicional de 2 campos"?

3. **Nominales** -- en el modelo actual, `NominalType` es opaco (su layout viene del bridge/registry). En Pure, un MetaNominal tendría `__data__ = Spec` (su identidad) pero no describe la estructura del dato que clasifica. El layout sigue necesitando el bridge. Esto te parece aceptable, o quieres que Pure internalice más?

4. **StructMixin** -- asumo que expone `.index`, `.values`, `.entries`, `.get()`, `.map()`, `__getitem__`, etc. a partir de `__meta__.__meta__.__data__` (keys) y `__data__` (values). Lo compartiría MetaStruct (struct de metas) y Struct (struct de valores). Correcto?

5. **Scope** -- esto reemplazaría a `base.py` + `types.py` + `struct.py` + `refs.py`, o lo ves como una capa paralela experimental que convive?

---

**Especificación Formal**

- **Núcleo**
```text
Pure[M, D]
  __meta__: M
  __data__: D

Meta[K, P] <: Pure[K, P]
```

- **Observadores**
```text
meta_of(x: Pure[M, D]) = x.__meta__
data_of(x: Pure[M, D]) = x.__data__
```

- **Clasificación**
```text
well_formed(x) := classifies(meta_of(x), data_of(x))
```

`classifies` no tiene por qué ser una sola regla estructural; depende de la clase de meta.

**Metas Base**

- **Índice**
```text
MetaIndex[G, K] = Meta[G, tuple[K | None, ...]]
```

Lectura:
- `G` clasifica el propio índice como entidad nominal/meta
- `__data__` son las keys posicionales/nominales

- **Struct heterogéneo**
```text
MetaStruct[G, K, M] = Meta[MetaIndex[G, K], tuple[M, ...]]
Struct[G, K, M, D]  = Pure[MetaStruct[G, K, M], tuple[D, ...]]
```

Regla:
```text
classifies(MetaStruct(index, metas), ds)
iff
  len(index.keys) = len(metas) = len(ds)
  and forall i: classifies(metas[i], ds[i])
```

- **Struct homogéneo**
```text
MetaUniform[G, K, M] = Meta[MetaIndex[G, K], M]
Uniform[G, K, M, D]  = Pure[MetaUniform[G, K, M], tuple[D, ...]]
```

Regla:
```text
classifies(MetaUniform(index, m), ds)
iff
  len(index.keys) = len(ds)
  and forall i: classifies(m, ds[i])
```

- **Lista homogénea, aridad libre**
```text
MetaList[G, M] = Meta[G, M]
List[G, M, D]  = Pure[MetaList[G, M], tuple[D, ...]]
```

Regla:
```text
classifies(MetaList(g, m), xs)
iff
  xs es una secuencia finita
  and forall x in xs: classifies(m, x)
```

Yo fijaría ya que `List.__data__` sea secuencia, idealmente `tuple[D, ...]`, para mantener consistencia con el resto.

**Spec Como Meta Nominal Aplicado**

Tu redefinición más interesante es esta:

```text
MetaSpec[G, K, M, D] = Meta[MetaStruct[G, K, M], tuple[D, ...]]
```

o sea:
- `MetaSpec` ya no es “schema del spec”
- `MetaSpec` es el propio spec nominal como valor-meta
- por tanto sustituye a `NominalType` y a `NT`

Yo la reescribiría ligeramente para distinguir claridad semántica de notación:

```text
Spec[G, K, M, D] <: Meta[MetaStruct[G, K, M], tuple[D, ...]]
```

Es decir:
- `Spec` es una clase de `Meta`
- su `__meta__` es un `MetaStruct`
- su `__data__` son los argumentos concretos

Esto casa muy bien con tu frase:

- “MetaSpec pasa a ser el propio Spec”
- “Spec sustituye a NT”
- “el Spec del Spec es otro spec”

Entonces el punto fijo queda:

```text
meta_of(std.metas.Spec) = std.metas.Spec
```

Y los demás roots nominales serían instancias/especializaciones clasificadas por ese fixed point:

```text
meta_of(std.metas.Index) = std.metas.Spec
meta_of(std.metas.List) = std.metas.Spec
meta_of(std.Qualifier) = std.metas.Spec
...
```

Esto reemplaza `Ground` por un nominal self-hosted.

**Anchor**

Si `NT` desaparece y el root nominal se representa con `Spec`, entonces `Anchor` puede quedarse simple:

```text
Anchor = Pure[Spec(std.metas.Anchor), str]
```

o más esquemáticamente:

```text
MetaAnchor = Spec(std.metas.Anchor)
Anchor     = Pure[MetaAnchor, str]
```

**Qualifier**

Tu intuición aquí me parece muy buena:

- un `Qualifier` es un meta especial
- encadena varias metas
- puede representarse como un struct posicional de metas

La formalización que más me convence es:

```text
MetaQual[Q] = Spec(std.Qualifier, q1, q2, ..., qn)
```

y su carrier estructural interno es:

```text
MetaQual[Q] <: MetaStruct[std.Qualifier, None, Meta]
```

o más explícito:

```text
MetaQual[G, Q] = MetaStruct[G, None, Q]
```

con `Q` una tupla posicional de metas.

Semántica:
```text
classifies(MetaQual(q1, q2, ..., qn), d)
iff
  classifies(chain(q1, q2, ..., qn), d)
```

donde `chain` se interpreta como composición de metas sobre un mismo dato.

Yo fijaría la convención:

```text
MetaQual(q1, q2, ..., base)
= q1(q2(...(base)...))
```

Así tu ejemplo:

```text
Array[4,4] Natural
```

se representa como dos specs dentro de un qualifier chain:

```text
MetaQual(
  Spec(std.qualifiers.Array, 4, 4),
  Spec(std.types.Natural)
)
```

**Taxonomía Formal**

- `MetaStruct`: meta estructural heterogéneo
- `MetaUniform`: meta estructural homogéneo indexado
- `MetaList`: meta estructural homogéneo libre
- `Spec`: meta nominal aplicado, self-hosted
- `MetaQual`: meta compuesto por encadenamiento de metas

**Leyes Útiles**

- **Expandir uniform a struct**
```text
expand(MetaUniform(index, m)) = MetaStruct(index, repeat(m, len(index)))
```

- **Colapsar struct a uniform**
```text
collapse(MetaStruct(index, metas)) = MetaUniform(index, m)
iff all metas[i] = m
```

- **Spec como sustituto de Ground**
```text
meta_of(Spec(std.metas.Spec)) = Spec(std.metas.Spec)
```

- **Nominal roots**
```text
IndexRoot = Spec(std.metas.Index)
ListRoot  = Spec(std.metas.List)
QualRoot  = Spec(std.Qualifier)
```

**Traducción Desde El Modelo Actual**

- `packages/protomorph/src/protomorph/base.py`
  - `Val(__type__, __data__)` -> `Pure(__meta__, __data__)`
  - `Const` deja de ser primitivo
- `packages/protomorph/src/protomorph/types.py`
  - `Type` -> `Meta`
  - `NominalType(spec_ref)` -> `Spec(...)`
  - `StructType(meta_attrs)` -> `MetaStruct(...)`
- `packages/protomorph/src/protomorph/struct.py`
  - `Struct.Index` -> `MetaIndex`
  - `Struct[str, Type]` -> `MetaStruct`
  - `Struct[str, Val]` -> `Struct`
  - `Uniform` aparece como nueva variante comprimida
- `packages/protomorph/src/protomorph/refs.py`
  - `Anchor` se mantiene
  - `Spec` deja de ser `Ref` y pasa a ser `Meta`
- `packages/protomorph/src/protomorph/qualifiers.py`
  - `NominalQualifier(spec_ref, underlying)` -> `MetaQual(spec, underlying_meta)` o chain equivalente

**Plan De Implementación**

Lo haría por fases, no como big bang.

- **Fase 1: núcleo experimental paralelo**
  - crear `pure.py`
  - definir solo `Pure` y `Meta`
  - no exportarlo aún
  - sin bootstrap nominal todavía

- **Fase 2: metas estructurales mínimas**
  - añadir `MetaIndex`, `MetaStruct`, `MetaUniform`, `MetaList`
  - añadir mixins/propiedades derivadas:
    - `keys`
    - `arity`
    - `entries`
    - `field_metas`
    - `values`
  - implementar invariantes locales de longitud

- **Fase 3: spec self-hosted mínimo**
  - introducir `Spec` como `Meta`
  - bootstrap mínimo del fixed point `std.metas.Spec`
  - después roots nominales:
    - `std.metas.Index`
    - `std.metas.List`
    - `std.Qualifier`
    - `std.metas.Anchor`

- **Fase 4: qualifier chain**
  - introducir `MetaQual`
  - definir representación canónica posicional
  - helpers de composición:
    - `qual(base, *qualifiers)` o similar
    - normalización/aplanado

- **Fase 5: puentes con el modelo actual**
  - conversión desde `Struct.Index` / `StructType` / `NominalType` / `Spec`
  - adaptación progresiva de `format.py`, `bridge.py`, `algebra.py`

**Decisiones Que Conviene Cerrar Antes De Codificar**

- `Spec` como clase separada o simplemente una especialización nominal de `Meta` sin clase dedicada
  - recomiendo clase `Spec` dedicada
- `MetaQual` como alias semántico de `MetaStruct` o clase separada
  - recomiendo clase separada con semántica de chain
- `List.__data__`
  - recomiendo `tuple[D, ...]`
- key type de índices
  - recomiendo mantener `K | None`

**Mi Recomendación Concreta De Primer Corte**
1. fijar esta axiomatización mínima:
   - `Pure`
   - `Meta`
   - `MetaIndex`
   - `MetaStruct`
   - `MetaUniform`
   - `List`
   - `Spec`
2. dejar `MetaQual` para la segunda iteración del experimento
3. bootstrapear solo `std.metas.Spec` y `std.metas.Index` al principio

Si quieres, el siguiente paso lo preparo como un documento breve de especificación “v0” con secciones:
1. syntax
2. invariants
3. classification
4. bootstrap
5. mapping to current protomorph

y ya quedaría listo para pasar a código.

---

Bajo todo a una v0 axiomática: el sistema tiene 3 capas distintas pero acopladas: carrier (`Pure`), clasificadores (`Meta`) e interpretación semántica (`bridge`). La clave es que `Struct`, `Uniform`, `List`, `Spec` y `Qualifier` no son ideas aisladas; son 5 álgebras sobre el mismo patrón.

**Nucleo**
```text
Pure[M, D]
  __meta__: M
  __data__: D

Meta[K, P] <: Pure[K, P]
```

- `Pure` es el carrier universal: todo objeto es `meta + data`.
- `Meta` es un `Pure` que clasifica otros `Pure`.
- La relación fundamental no es "tener cierto tipo Python", sino `classifies(meta, data)`.

**Axiomas**
```text
meta_of(x) = x.__meta__
data_of(x) = x.__data__

well_formed(x) := classifies(meta_of(x), data_of(x))
```

Existe un meta distinguido:

```text
Omega := std.metas.Spec
meta_of(Omega) = Omega
```

- `Omega` sustituye a `Ground`.
- No es "vacío"; es el universo nominal mínimo.
- Los demás roots nominales viven clasificados por `Omega`.

Ejemplos:

```text
meta_of(std.metas.Index) = Omega
meta_of(std.metas.List) = Omega
meta_of(std.metas.Qualifier) = Omega
meta_of(std.metas.Anchor) = Omega
```

**Constructores Estructurales**
```text
MetaIndex[G, K]      = Meta[G, tuple[K | None, ...]]
MetaStruct[G, K, M]  = Meta[MetaIndex[G, K], tuple[M, ...]]
MetaUniform[G, K, M] = Meta[MetaIndex[G, K], M]
MetaList[G, M]       = Meta[G, M]

Struct[G, K, M, D]   = Pure[MetaStruct[G, K, M], tuple[D, ...]]
Uniform[G, K, M, D]  = Pure[MetaUniform[G, K, M], tuple[D, ...]]
List[G, M, D]        = Pure[MetaList[G, M], tuple[D, ...]]
```

Lectura:

- `MetaIndex`: define slots/keys.
- `MetaStruct`: define un meta por slot.
- `MetaUniform`: define un meta comun para todos los slots.
- `MetaList`: define un meta comun para una secuencia libre.
- `Struct`, `Uniform`, `List`: son carriers de datos bajo esas 3 familias.

**Clasificación**
```text
classifies(MetaIndex(g, keys), ks)
iff ks = keys
```

```text
classifies(MetaStruct(index, metas), ds)
iff
  len(index.keys) = len(metas) = len(ds)
  and forall i: classifies(metas[i], ds[i])
```

```text
classifies(MetaUniform(index, m), ds)
iff
  len(index.keys) = len(ds)
  and forall i: classifies(m, ds[i])
```

```text
classifies(MetaList(g, m), xs)
iff
  xs es una secuencia finita
  and forall x in xs: classifies(m, x)
```

Aqui aparece un patrón fuerte:

- `MetaStruct` = familia dependiente sobre un índice.
- `MetaUniform` = familia constante sobre un índice.
- `MetaList` = familia constante sobre longitud libre.

**Álgebra Oculta**
- `MetaStruct` es el análogo de un producto dependiente finito.
- `MetaUniform` es la diagonal `M -> (M, ..., M)` sobre un índice fijo.
- `MetaList` es el libre monoide del carrier clasificado por `M`.
- `Spec` es un código en un pequeño universo nominal.
- `Qualifier` es una acción monoidal sobre metas.

Ese último punto es el más profundo: `Qualifier` no es primariamente un producto, sino una composicion ordenada.

**Spec**
La forma correcta de pensarlo es doble:

- semánticamente, `Spec` es un `Meta`
- estructuralmente, `Spec` es isomorfo a un `Struct` de dos campos: `anchor` y `args`

```text
Spec[A, D] <: Meta[A, D]

Spec[A, D] ~= Struct[
  G = std.metas.Spec,
  K = "anchor" | "args",
  M = (std.metas.Anchor, A),
  D = (str, D)
]
```

Observables:

```text
anchor_of(spec) : str
args_of(spec)   : D
args_meta(spec) : A
```

Lectura:

- `anchor` da identidad nominal.
- `args` dan aplicación.
- `args_meta` describe esos argumentos.

Esto unifica muy bien lo actual:

- `NominalType` pasa a ser un `Spec`.
- `NT(...)` desaparece como primitivo.
- `Spec` ya no es un ref extraño; es un meta ordinario dentro del mismo universo.

**Anchor**
```text
Anchor = Pure[std.metas.Anchor, str]
```

- Por ahora basta `str`.
- Si luego quieres volver a `segments`, eso puede ser vista derivada.

**Qualifier**
Aquí conviene separar representación y semántica.

Representación canónica sugerida:

```text
MetaQual(ops, base)
  ops  : tuple[Spec, ...]
  base : Meta
```

con presentación superficial equivalente a:

```text
std.metas.Qualifier(op1, op2, ..., opn, base)
```

o si prefieres verlo como `Struct`, se puede almacenar posicionalmente. Pero algebraicamente no es un producto: es una cadena.

Semántica:

```text
denote(MetaQual((q1, q2, ..., qn), base))
= q1 ⊙ (q2 ⊙ (... (qn ⊙ base)...))
```

donde `⊙` es la acción de un qualifier sobre una meta base.

Tu ejemplo:

```text
Array[4,4] Natural
```

queda como:

```text
MetaQual(
  ops = (Spec(Array, (4,4)),),
  base = Spec(Natural, ())
)
```

y si hubiese varios:

```text
Readonly Array[4,4] Natural
```

```text
MetaQual(
  ops = (Spec(Readonly, ()), Spec(Array, (4,4))),
  base = Spec(Natural, ())
)
```

**Normal Forms**
Hay varias normalizaciones naturales.

- `Uniform` como compresión de `Struct`:
```text
expand(MetaUniform(index, m))
= MetaStruct(index, (m, m, ..., m))
```

```text
collapse(MetaStruct(index, metas))
= MetaUniform(index, m)
iff todos los metas son el mismo m
```

- `Qualifier` como cadena plana:
```text
flatten(MetaQual(ops1, MetaQual(ops2, base)))
= MetaQual(ops1 ++ ops2, base)
```

- `Spec` como anchor + args normalizados:
```text
normalize(spec(anchor, args))
= spec(anchor, normalize(args))
```

**Patrones Profundos**
- `Struct` expresa heterogeneidad.
- `Uniform` expresa constancia sobre forma fija.
- `List` expresa repetición libre.
- `Spec` expresa identidad nominal aplicada.
- `Qualifier` expresa transformación compuesta sobre una base.

O dicho de otra manera:

- `Struct` da geometría.
- `Spec` da identidad.
- `Qualifier` da acción.
- `bridge` da interpretación.

**Consecuencias Para El Diseño Del Código**
Esto simplifica mucho varias zonas del código actual:

- `packages/protomorph/src/protomorph/algebra.py:328`
  - `_occurs` hoy hace case analysis por clase; con `Pure` se puede convertir en un fold genérico.
- `packages/protomorph/src/protomorph/algebra.py:397`
  - `_normalize_type` también se puede reescribir como recorrido uniforme por carriers/meta-carriers.
- `packages/protomorph/src/protomorph/bridge.py:164`
  - `_lift_qualifier` ya es la semántica parcial de `⊙`; el nuevo `MetaQual` solo la haría explícita.
- `packages/protomorph/src/protomorph/struct.py:77`
  - `Index` ya contiene la forma.
- `packages/protomorph/src/protomorph/types.py:82`
  - `StructType(meta_attrs)` ya es básicamente `MetaStruct`.
- `packages/protomorph/src/protomorph/qualifiers.py:20`
  - `NominalQualifier(spec_ref, underlying)` ya es un proto-`MetaQual`.

**Plan De Código**
No lo ejecutamos aún, pero yo lo haría así:

- `Fase 1`
  - `pure.py` con `Pure` y `Meta`
  - sin exportarlo aún
- `Fase 2`
  - `MetaIndex`, `MetaStruct`, `MetaUniform`, `MetaList`
  - mixins de vistas derivadas: `keys`, `arity`, `entries`
- `Fase 3`
  - bootstrap mínimo:
    - `Omega = std.metas.Spec`
    - `std.metas.Index`
    - `std.metas.List`
    - `std.metas.Anchor`
    - `std.metas.Qualifier`
- `Fase 4`
  - `Spec` como meta nominal self-hosted
  - vista estructural `anchor/args`
- `Fase 5`
  - `MetaQual`
  - normalización plana de qualifiers
  - helpers de composición
- `Fase 6`
  - adaptadores desde el modelo actual:
    - `StructType -> MetaStruct`
    - `NominalType -> Spec`
    - `NominalQualifier -> MetaQual`

**Mi recomendación final**
- usar `Spec` como universo nominal mínimo (`Omega`)
- representar `Spec` como struct binario `anchor/args`
- representar `Qualifier` en forma normal como cadena plana `ops + base`
- dejar que `bridge` siga siendo el intérprete semántico; no meter toda la semántica dentro del core

Si quieres, el siguiente paso lo convierto en una especificación `v0` aún más seca, casi matemática, con solo:
1. firmas
2. axiomas
3. reglas de `classifies`
4. reglas de normalización
5. bootstrap mínimo de `Spec : Spec`

---


La pieza clave que aparece al formalizarlo es esta: `Uniform` demuestra que no conviene imponer una sola ley global del tipo `wf(x) = classifies(meta_of(x), data_of(x))` para todo `Meta`. La paridad estructural existe, pero es una propiedad de algunas construcciones, no del universo entero. Con eso, la v0 queda mucho más sólida.

**v0**

- **Carrier universal**
```text
Pure[M, D]
  __meta__: M
  __data__: D

Meta[K, P] <: Pure[K, P]
```

- **Observadores**
```text
meta_of(x) = x.__meta__
data_of(x) = x.__data__
```

- **Dos nociones distintas**
```text
wf(x)           # bien formado
m ⊨ d           # "m clasifica d"
```

- Para valores ordinarios:
```text
wf(Pure[m, d])  iff  wf(m) and m ⊨ d
```

- Para metas:
  - `Meta` reutiliza el carrier `(__meta__, __data__)`
  - pero su `wf(...)` es constructor-específico
  - no exigimos una ley global única para todos los metas

Eso permite que `MetaStruct` tenga paridad fuerte y `MetaUniform` la rompa sin inconsistencia.

**Metas estructurales**

```text
MetaIndex[G, K]      = Meta[G, tuple[K | None, ...]]
MetaStruct[G, K, M]  = Meta[MetaIndex[G, K], tuple[M, ...]]
MetaUniform[G, K, M] = Meta[MetaIndex[G, K], M]
MetaList[G, M]       = Meta[G, M]
```

Lectura:

- `MetaIndex` describe forma/slots
- `MetaStruct` describe una familia dependiente sobre esa forma
- `MetaUniform` describe una familia constante sobre esa forma
- `MetaList` describe una familia constante sobre aridad libre

**Reglas de bien formado**

- **Index**
```text
wf(MetaIndex[G, K](g, keys))
iff
  wf(g)
  and keys es tuple[K | None, ...]
  and las keys nominales no se repiten
```

- **Struct**
```text
wf(MetaStruct(index, metas))
iff
  wf(index)
  and metas es tuple
  and len(metas) = len(index.keys)
  and forall m in metas: wf(m)
```

- **Uniform**
```text
wf(MetaUniform(index, item_meta))
iff
  wf(index)
  and wf(item_meta)
```

- **List**
```text
wf(MetaList(g, item_meta))
iff
  wf(g)
  and wf(item_meta)
```

**Reglas de clasificación**

- **Index clasifica forma, no contenido**
```text
MetaIndex(g, keys) ⊨ xs
iff
  xs es tuple
  and len(xs) = len(keys)
```

Esto es importante: `MetaIndex` clasifica cualquier tupla con esa aridad/forma. Por eso puede clasificar tanto:
- la tupla de field metas de un `MetaStruct`
- la tupla de valores de un `Struct`

- **Struct heterogéneo**
```text
MetaStruct(index, metas) ⊨ xs
iff
  xs es tuple
  and len(xs) = len(metas)
  and forall i: metas[i] ⊨ xs[i]
```

- **Uniform homogéneo**
```text
MetaUniform(index, m) ⊨ xs
iff
  xs es tuple
  and len(xs) = len(index.keys)
  and forall i: m ⊨ xs[i]
```

- **List homogénea libre**
```text
MetaList(g, m) ⊨ xs
iff
  xs es una secuencia finita
  and forall x in xs: m ⊨ x
```

**Valores inducidos**

```text
Struct[G, K, M, D]   = Pure[MetaStruct[G, K, M], tuple[D, ...]]
Uniform[G, K, M, D]  = Pure[MetaUniform[G, K, M], tuple[D, ...]]
List[G, M, D]        = Pure[MetaList[G, M], tuple[D, ...]]
```

**Vistas derivadas**

- **Shape**
```text
shape(index) = (arity(index), named_keys(index))
```

- **Project**
```text
project(MetaStruct(index, metas), key)  = metas[offset(index, key)]
project(MetaUniform(index, m), key)     = m
```

**Álgebras ocultas**

- `MetaStruct` = producto dependiente finito
- `MetaUniform` = familia constante sobre índice fijo
- `MetaList` = monoide libre homogéneo
- `Qualifier` = acción monoidal sobre metas
- `Spec` = código nominal dentro del mismo universo

**Spec : Spec**

Aquí conviene distinguir la semántica abstracta de la representación concreta.

- **Abstractamente**
```text
Spec[A, D] <: Meta[A, D]
```

Todo `Spec` tiene:
```text
head(spec)   # identidad nominal
args(spec)   # argumentos
```

y su meta es el schema de sus argumentos:
```text
meta_of(spec) = A
data_of(spec) = args(spec)
```

- **Bootstrap mínimo**
Existe un spec distinguido:
```text
Ω = std.metas.Spec
```

con el axioma:
```text
wf(Ω)
meta_of(Ω) = Ω
```

Ese es el fixed point mínimo.

- **Roots nominales**
Cada root nominal `r` satisface:
```text
wf(r)
meta_of(r) = Ω
```

Ejemplos:
```text
std.metas.Index
std.metas.List
std.metas.Anchor
std.metas.Qualifier
std.types.Natural
std.qualifiers.Array
```

- **Aplicación nominal**
Si `r` es un root y `params(r)` es su schema de argumentos, entonces:
```text
wf(r[a])
iff
  wf(r)
  and wf(params(r))
  and params(r) ⊨ a

meta_of(r[a]) = params(r)
```

- **Semántica externa**
El hecho de que un `Spec` clasifique datos no es puramente estructural:
```text
r[a] ⊨ d
iff
  interpret(r, a, d)
```

donde `interpret` lo resuelve el bridge/registry semántico.

Esto preserva algo importante:
- el core expresa sintaxis/meta-estructura
- el bridge expresa interpretación nominal/opaca

**Representación concreta opcional de `Spec`**

Si quieres mantener la intuición que ya apareció, una codificación fiel es:

```text
Spec[A, D] ~= Struct[
  G = std.metas.Spec,
  K = ("anchor", "args"),
  M = (MetaAnchor, A),
  D = (str, D)
]
```

Pero esto es una representación concreta; la semántica abstracta no depende de fijarla ya.

**Qualifier**

Aquí la estructura profunda es de acción, no de simple producto.

- **Forma abstracta**
```text
Qual(qs; base)
  where qs = (q1, q2, ..., qn)
  and each qi is a qualifier-spec
  and base is a meta
```

- **Semántica**
```text
⟦Qual((); base)⟧ = base
⟦Qual((q, *qs); base)⟧ = apply(q, ⟦Qual(qs; base)⟧)

Qual(qs; base) ⊨ d
iff
  ⟦Qual(qs; base)⟧ ⊨ d
```

- **Leyes de acción**
```text
apply(q, MetaStruct(index, metas))
= MetaStruct(index, tuple(apply(q, m) for m in metas))

apply(q, MetaUniform(index, m))
= MetaUniform(index, apply(q, m))

apply(q, MetaList(g, m))
= MetaList(g, apply(q, m))
```

Y para nominales:
```text
apply(q, s) = Qual((q,); s)
```
salvo que el bridge tenga una reducción canónica más específica.

Esto encaja exactamente con la intuición actual del `bridge`: los qualifiers actúan punto a punto sobre layouts estructurales.

- **Forma normal**
```text
Qual(qs; Qual(rs; base))  =>  Qual(qs ++ rs; base)
```

La normal form de qualifier es una cadena plana:
```text
Qual((q1, q2, ..., qn); base)
```

**Ejemplo**

```text
Array[4,4] Natural
```

se modela como:

```text
Qual(
  ( std.qualifiers.Array[(4,4)] ; ),
  std.types.Natural
)
```

o, si prefieres notación totalmente explícita:

```text
Qual(
  qs   = (Spec(Array, (4,4)),),
  base = Spec(Natural, ())
)
```

Son, efectivamente, dos `Spec`s encadenados.

**Normalización**

- **Recursiva**
```text
norm(Index(keys))            = Index(keys)
norm(Struct(index, metas))   = Struct(norm(index), tuple(norm(m) for m in metas))
norm(Uniform(index, m))      = Uniform(norm(index), norm(m))
norm(List(g, m))             = List(norm(g), norm(m))
norm(r[a])                   = r[norm(a)]
norm(Qual(qs; base))         = flatten(tuple(norm(q) for q in qs), norm(base))
```

- **Flatten**
```text
flatten(qs, Qual(rs; base)) = Qual(qs ++ rs; base)
flatten(qs, base)           = Qual(qs; base)
```

- **Uniform no colapsa por definición**
Hay una vista:
```text
expand(MetaUniform(index, m))
= MetaStruct(index, repeat(m, len(index.keys)))
```

y una vista inversa parcial:
```text
collapse(MetaStruct(index, metas))
= MetaUniform(index, m)
iff all metas[i] = m
```

Pero esto es vista/coerción, no igualdad definicional. `Uniform` conserva significado propio.

**Consecuencia de diseño más importante**

La teoría queda con 5 familias bien separadas:

- `Struct`: heterogeneidad indexada
- `Uniform`: homogeneidad indexada
- `List`: homogeneidad libre
- `Spec`: identidad nominal aplicada
- `Qualifier`: acción compuesta sobre metas

O en una línea:

- `Struct` da geometría
- `Spec` da identidad
- `Qualifier` da acción

**Paso siguiente hacia código**

Si esto te cuadra, yo bajaría a un núcleo mínimo en este orden:

1. `Pure`, `Meta`
2. `MetaIndex`, `MetaStruct`, `MetaUniform`, `MetaList`
3. bootstrap de `Ω = std.metas.Spec`
4. `Spec` abstracto con `head/args`
5. `Qual` y `apply`
6. adaptadores desde el modelo actual

La única decisión que aún conviene fijar antes de escribir código es esta:
- si `Spec` se implementa desde el principio como abstracción pura con `head/args`, o directamente como representación concreta tipo `Struct("anchor","args")`

Mi recomendación: primero abstracción pura; luego, si encaja, demostrar que la representación concreta como `Struct` es fiel.