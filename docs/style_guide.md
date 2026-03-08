# Guia de estilo: Protobase, Flux y computacion incremental

Esta guia describe como se usan `Record`, `Inmutable`, `Consed`,
`@flux.property` y `@flux.method` en Axis, y como se organiza el flujo de datos
incremental.

## 1) Protobase en Axis (Record, Inmutable, Consed)

### Record

- `Record` es la base del sistema de clases de Protobase (atributos declarados,
  `__slots__`, defaults con deepcopy y metodos derivados).
- En Axis casi todos los nodos de dominio usan `Inmutable`/`Consed`, que heredan
  de `Record`. Usa `Record` directo solo si necesitas el modelo de record sin
  las restricciones de inmutabilidad.

### Inmutable

- Ideal para valores estables: hash estructural, prohibicion de mutacion y
  compatibilidad con cacheo.
- Uso en Axis: `src/axis/src/source.py` (`Source`, `Source.Span`,
  `Source.Position`), `src/axis/val/evaluator.py` (`Evaluator`).

### Consed

- Extiende `Inmutable` con hash-consing (canonicalizacion). Si dos instancias
  son iguales estructuralmente, comparten identidad.
- Uso en Axis: `src/axis/sem/realm.py` (`Realm`), `src/axis/sem/entity.py`
  (`Entity`), `src/axis/sem/context.py` (`Context.Contribution`),
  `src/axis/src/fs.py` (`SourceFile`, `SourceDir`).

Recomendacion rapida:

- Usa `Consed` para nodos del grafo semantico o AST donde la identidad debe
  seguir la estructura.
- Usa `Inmutable` para valores puros y evaluadores.
- Usa `Record` si no necesitas inmutabilidad pero quieres el modelo de records.

## 2) Flux: reglas y patrones de uso

### Reglas generales (Flux)

- `@flux.property`: valor derivado sin parametros.
- `@flux.method`: consulta derivada con parametros (cacheada por args/kwargs).
- `@flux.input`: unica fuente mutable; invalida dependencias de forma perezosa.
- Las consultas deben devolver valores concretos (no generators, no async).
- Args/kwargs deben ser hashables.
- No mutar inputs durante una consulta.
- Instancias deben ser weakrefables (Record/Inmutable/Consed ya lo garantizan).

Referencias: `packages/protobase/docs/flux.md`, `packages/protobase/docs/core.md`.

### Patrones en Axis

**Derivados con @flux.property**

- `Context.contributions` y `Context.scope`: `src/axis/sem/context.py`.
- `Realm.all_contributions`, `Realm.entities_by_anchor`: `src/axis/sem/realm.py`.
- `Entity.spec_by_shape`, `Entity.overload_by_shape`: `src/axis/sem/entity.py`.
- `Package.items`: `src/axis/items/package.py`.
- `Source.content`, `Source.lines`: `src/axis/src/source.py`.
- `SourceFile.content`: `src/axis/src/fs.py`.

**Consultas parametrizadas con @flux.method**

- `Package.file_items(file)`: `src/axis/items/package.py`.
- `SourceDir.glob(pattern)`: `src/axis/src/fs.py`.
- `Context.Contribution.check`: `src/axis/sem/context.py`.

**Inputs con @flux.input**

- `SourceBuffer.buffer`: `src/axis/src/source.py`.

## 3) Flujo de datos incremental (Package -> Items -> Contexts -> Realm -> Entity)

El flujo se organiza como un grafo inmutable con derivaciones cacheadas:

1) **Entrada**

   - `SourceDir.glob` lista archivos `.ax` y es invalidado por `FSWatcher`.
   - `SourceFile.content` lee el contenido y es invalidado por `FSWatcher`.
   Referencias: `src/axis/src/fs.py`.

2) **Package**

   - `Package.source_files` deriva los archivos desde el directorio.
   - `Package.file_items(file)` genera items por archivo.
   - `Package.items` agrega todos los items.
   Referencia: `src/axis/items/package.py`.

3) **Items/Contexts**

   - `Item` hereda de `Context` y define `anchor`.
   - `Context.contributions` devuelve contribuciones semanticas.
   - `Context.scope` construye el scope local.
   Referencias: `src/axis/items/item.py`, `src/axis/sem/context.py`.

4) **Realm**

   - Agrega contribuciones de todos los contexts.
   - Calcula `contributions_by_anchor` y `entities_by_anchor`.
   Referencia: `src/axis/sem/realm.py`.

5) **Entity**

   - Agrupa contribuciones por shape (spec/overload).
   - Buckets derivados se recomputan solo cuando cambia una contribucion.
   Referencia: `src/axis/sem/entity.py`.

Este flujo esta pensado para recomputacion incremental: una invalidacion en
fuentes o contribuciones solo recalcula lo que depende de ellas.

## 4) Contribuciones y definiciones

Las definiciones (`Item`) emiten contribuciones usando `@flux.property`:

- `FnDef` emite `ImplContribution`.
- `ClassDef` emite `OverloadContribution`.
- `Global` emite `GlobalContribution`.

Referencias: `src/axis/items/defs/fn.py`, `src/axis/items/defs/class_.py`,
`src/axis/items/global_.py`, `src/axis/sem/entity.py`.

## 5) Cacheo local vs Flux

- Usa `@flux.property` para valores que dependan de otras consultas o
  invalidacion.
- Usa `slot_cached_property` para calculos locales y estables que no dependen
  de flujo incremental (ej. `Item.anchor` o `Global.anchor`).

Referencias: `src/axis/items/item.py`, `src/axis/items/global_.py`.

## 6) Reglas de implementacion para nuevas piezas

- Mantener las consultas puras y deterministas.
- No mezclar IO directo dentro de propiedades que no esten claramente en la
  capa de entrada (`SourceFile.content`).
- Si agregas un `Item`, emite contribuciones desde `@flux.property` y deja que
  `Realm` sea el agregador unico por `anchor`.
- Si agregas un nuevo tipo de fuente, expone `content`/`lines` con
  `@flux.property` y una estrategia de invalidacion (watcher o `@flux.input`).
- Para cambios persistentes en records, usar `mutate(record, **attrs)`.

## 7) Convenciones de tipos y estructura

- El repo usa typing moderno (PEP 695) y el sentinel `_` para campos requeridos
  despues de defaults.
- Prefiere `type | None` sobre `Optional[type]` en runtime.
- Orden de imports: stdlib, terceros, locales (separados por linea en blanco).

Referencias: `packages/protobase/docs/core.md`, `pyproject.toml`.
