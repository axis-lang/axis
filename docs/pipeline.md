# Pipeline incremental

## Resumen

Axis usa un flujo incremental basado en Protobase/Flux. La idea central es
construir un grafo inmutable de items y derivar entidades a partir de
contribuciones, evitando recomputo completo ante cambios de entrada.

`Package -> Items -> Contexts -> Realm -> Entity`

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

### Items / Contexts

- `Item` hereda de `Context` y define `anchor`.
- `Context.contributions` expone contribuciones semanticas.
- `Context.scope` construye el scope local.

Referencias: `src/axis/items/item.py`, `src/axis/sem/context.py`.

### Realm

- Agrega contribuciones de todos los contexts.
- Deriva `contributions_by_anchor` y `entities_by_anchor`.

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
