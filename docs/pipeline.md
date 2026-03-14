# Pipeline incremental

## Resumen

Axis usa un flujo incremental basado en Protobase/Flux. La idea central es
construir un grafo inmutable de items y derivar entidades a partir de
contribuciones, evitando recomputo completo ante cambios de entrada.

`Source -> Package -> Item -> Context -> Contribution -> Realm -> Entity`

Lectura operacional:

- `Package` descubre fuentes y construye `Item`.
- Cada `Item` es un `Context`.
- Cada `Context` emite una o mas `Contribution` ya adaptadas al contrato de
  `sem`.
- `Realm` agrega contribuciones por `anchor`.
- `Entity` agrupa contribuciones por shape y resuelve semantica.

## Politica de lowering

- `syn` define contratos abstractos de lowering consumibles por framework:
  - `syn.SymLike`
  - `syn.ScopeLike`
  - `syn.Expr.to_bound(scope)`
  - `syn.Expr.to_anchor(scope_ref)`
- `sem` posee el runtime semantico concreto:
  - `sem.Scope`
  - `sem.Binding`
  - `sem.BindingStruct`
  - `sem.build_bound(...)`
- `expr` implementa el lowering Axis-especifico sobre nodos concretos.
- `items` usa ese lowering para construir anchors, bindings y contribuciones.

Regla de diseño:

- `sem` consume contratos de `syn` y tipos canonicos propios.
- `sem` no debe depender de nodos concretos o lowers concretos de `expr`.
- `expr/ir` puede exponer shims de compatibilidad, pero no es el dueño del
  modelo semantico canonico.

## Capas del flujo

### Entrada

- `SourceDir.glob` lista archivos `.ax` y es invalidado por `FSWatcher`.
- `SourceFile.content` lee el contenido y se invalida en cambios de archivo.

Referencia: `src/axis/src/fs.py`.

### Package

- `Package.source_files` agrega los archivos detectados.
- `Package.file_items(file)` construye items por archivo (`@flux.method`).
- `Package.items` agrega todos los items (`@flux.property`).

Referencia: `src/axis/items/package.py`.

### Items / Contexts / Contributions

- `Item` hereda de `Context` y define `anchor`.
- `Context.contributions` expone contribuciones semanticas.
- `Context.scope` construye el scope local.
- `expr` loweriza bindings, bounds y anchors mediante contratos de `syn`.
- `items` emite `Contribution` listas para ser agregadas por `Realm`.

Referencias: `src/axis/items/item.py`, `src/axis/sem/context.py`.

### Realm

- Agrega contribuciones de todos los contexts.
- Deriva `contributions_by_anchor` y `entities_by_anchor`.
- No interpreta sintaxis Axis; trabaja sobre contribuciones ya adaptadas.

Referencia: `src/axis/sem/realm.py`.

### Entity

- Agrupa contribuciones por shape (spec/overload) en buckets.
- Buckets se recomputan solo cuando cambia una contribucion.

Referencia: `src/axis/sem/entity.py`.

## Invalidacion

El sistema es pull-based:

- Mutaciones sobre `@flux.input` o invalidaciones manuales avanzan la revision.
- El recomputo ocurre solo cuando se vuelve a acceder a la consulta.
- `FSWatcher` invalida `SourceFile.content` y `SourceDir.glob`.

Referencias: `packages/protobase/docs/flux.md`, `src/axis/src/fs.py`.
