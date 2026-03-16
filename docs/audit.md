# Auditoria del proyecto Axis

Fecha del informe: 2026-03-08

## Resumen ejecutivo

- Pipeline completo para parsing/AST/semantica con integracion Protobase/Flux.
- Evaluador parcial: literales y operadores aritmeticos basicos.
- TUI opcional con Textual y CLI con modos `--repl`, `--watch` y `--tui`.
- Suite de tests activa pero cobertura limitada; no hay CI/CD.
- Documentacion alineada en lo esencial, con brechas en `expr/` y `log/`.
- Hallazgos criticos en errores silenciados y diagnosticos incompletos.

## Estado del repositorio (snapshot)

- Rama principal: `main`.
- Remoto: `origin/main` (al momento de la auditoria).
- Cambios staged al momento del informe:
  - Nuevos: `codebase/sandbox/alpha.ax`, `codebase/sandbox/beta.ax`.
  - Borrados: `codebase/sandbox/decimal.ax`, `codebase/sandbox/demo.ax`,
    `codebase/sandbox/test.ax`.
  - Modificados: `codebase/sandbox/std.ax`, `justfile`,
    `packages/protobase/src/protobase/flux.py`,
    `src/axis/log/report.py`, `src/axis/sem/entity.py`,
    `src/axis/syn/__init__.py`, `src/axis/syn/node.py`.
  - Renombrado: `src/axis/syn/building.py` -> `src/axis/syn/parsing.py`.
- No habia cambios unstaged en el momento del informe.
- Estilo de commits observado: mensajes largos y multi-tema, sin convencion.

## Estructura del repositorio

- `src/axis/`: paquete principal (parser, AST, semantica, evaluacion, TUI).
- `packages/protobase/`: runtime de records inmutables, consing y Flux.
- `tests/`: tests unittest.
- `docs/`: documentacion Sphinx (MyST).
- `codebase/`: ejemplos de lenguaje (`sandbox`, `std-core`).
- `data/`: PDFs y referencias tecnicas.
- `scripts/`: scripts experimentales.

## Dependencias y tooling

- Python `^3.13` y Poetry.
- Runtime: `protobase` (local), `antlr4-tools`, `antlr4-python3-runtime`,
  `interegular`, `cyclopts`, `pyyaml`, `semver`, `ipython`.
- Dev: `ipykernel`, `myst-parser`, `pydata-sphinx-theme`, `rich`,
  `watchdog`, `pyright`, `sphinx`, `textual`.
- No hay configuracion de lint/formatter ni CI/CD.

## Documentacion: alineacion y cobertura

### Inventario

- `README.md`, `AGENTS.md`.
- `docs/index.md`, `docs/overview.md`, `docs/pipeline.md`,
  `docs/style_guide.md`, `docs/development.md`, `docs/conf.py`.
- `src/axis/val/README.md` (notas informales).

### Brechas principales

- `src/axis/expr/` (12 archivos) no aparece en `README.md` ni en docs Sphinx.
- `src/axis/log/` no aparece en docs Sphinx.
- `src/axis/syn/matching.py` es un subsistema grande sin doc externa.
- Sphinx tiene `autodoc`/`autosummary` configurados pero no se usan.

### Desalineaciones puntuales

- `docs/style_guide.md` referencia `fn.py`/`class_.py` como lugar de
  `ImplContribution`/`OverloadContribution`, pero las clases viven en
  `src/axis/sem/entity.py`.
- `docs/style_guide.md` no distingue entre `Entity.overload_by_shape` y el
  metodo homonimo en `SpecBucket`.
- `docs/pipeline.md` sugiere que `Package.source_files` es derivado, pero es
  un `@property` simple (la derivacion real vive en `SourceDir.glob`).
- `src/axis/val/README.md` no esta enlazado y tiene el titulo con un typo.

### Docstrings

- Buen ejemplo: `src/axis/syn/matching.py` (docstring extenso y claro).
- Faltan docstrings en clases clave: `Node`, `Builder`, `Context`, `Entity`,
  `Realm`, `Scope`, `Package`, `Evaluator`, `Report`, `MainView`, y la mayoria
  de los nodos en `src/axis/expr/`.

## Estilo y calidad del codigo

### Hallazgos criticos

- `src/axis/dom/err.py:7` tiene el campo `diagnostic` comentado, pero
  `src/axis/tui/dom_render.py:34` y `src/axis/tui/dom_render.py:40` acceden a
  `value.diagnostic` -> riesgo de `AttributeError` en runtime.
- `src/axis/expr/tuple_.py:276` usa `except Exception: return None` y oculta
  errores reales.
- `src/axis/log/report.py:150` pierde el encadenamiento de excepciones
  (`raise ... from exc` comentado).

### Warnings

- Imports no usados en `src/axis/syn/parsing.py:7` (`warn`) y
  `src/axis/syn/parsing.py:17` (`token`).
- Debug leftover: `from rich import print` en `src/axis/sem/entity.py:8` con
  llamadas a `print()` en `src/axis/sem/entity.py:55` y
  `src/axis/sem/entity.py:58`.
- Codigo muerto comentado en:
  - `src/axis/syn/node.py` (rendering antiguo)
  - `src/axis/expr/__init__.py` (dispatch viejo)
  - `src/axis/items/mod.py`
  - `src/axis/items/defs/base.py`
  - `src/axis/syn/outline.py` (bloque final)
- Typo persistente `identation` en `src/axis/syn/outline.py`,
  `src/axis/syn/node.py` y `src/axis/src/source.py`.
- Clase `SyntaxError` en `src/axis/syn/node.py:341` shadowing el builtin.
- Inconsistencia de typing: `Optional[X]` mezclado con `X | None`.
- Estilos de logging mezclados (`from axis import log` vs
  `from axis.log import report as log`).

### Informativos

- Funciones largas con nesting profundo:
  - `_reify_group()` en `src/axis/syn/matching.py` (~100 lineas).
  - `match_tuple()` en `src/axis/expr/tuple_.py` (~77 lineas).
- Comentarios con mezcla de espanol/ingles en varios modulos.

## Tests y cobertura

- Total: 5 archivos, ~31 tests activos.
- `tests/test_syn.py`: parsing, matching, reificacion, proyecciones, smoke.
- `tests/test_eval.py`: literales, aritmetica, tuplas, simbolos.
- `tests/test_defs.py`: merge de tuplas inline/bloque.
- `tests/test_dom_struct.py`: Struct/Shape/Index.
- `tests/test_tuple.py`: commented out (0 tests activos).

### Gaps de cobertura

- `src/axis/src/` (SourceFile, SourceDir, FSWatcher).
- `src/axis/log/` (Report y renderers).
- `src/axis/tui/`.
- `src/axis/sem/` (Context, Entity, Realm, Scope).
- `src/axis/items/` (Mod, Use, Doc, contribuciones).
- `src/axis/syn/outline.py`.

## Funcionalidades implementadas

- Gramatica ANTLR4 completa y parsing de expresiones.
- Outline parser basado en indentacion.
- AST completo de expresiones (`src/axis/expr/`).
- Pattern matching estructural y reificacion de templates.
- Modelo de dominio (valores, tipos, refs, structs).
- Sistema de items y contribuciones basicas.
- Modelo semantico con `Context`, `Entity`, `Realm`, `Scope`.
- Evaluador parcial (literales, aritmetica, tuplas, simbolos).
- Sistema de fuentes e invalidacion incremental con watcher.
- Diagnosticos con `Report` y renderizado con Rich.
- TUI con Textual.
- CLI con modos `--repl`, `--watch`, `--tui`.

## Funcionalidades parciales

- Evaluador: `Apply`, `Index`, `Member` registradas pero no implementadas.
- Evaluador: faltan `Comparison`, `Logic`, `Range`, `Cast`, `Trail`, `Suite`.
- `Mod.contributions` devuelve `frozenset()` (codigo comentado).
- `QualDef.contributions` devuelve `frozenset()`.
- `ImplBucket` comentado en `src/axis/sem/entity.py`.
- `CastDef` comentado en `src/axis/items/defs/base.py`.
- AST Transformer y Visitor existen pero no se exportan.

## Funcionalidades pendientes o planificadas

- `ifExpr` en la gramatica (comentado en `Axis.g4`).
- Operador de scope `::` sin manejo en AST/evaluador.
- Spread de tuplas (regla comentada en la gramatica).
- Motor de inferencia de tipos (solo notas en `src/axis/val/README.md`).
- Biblioteca estandar con implementaciones reales (no solo stubs).
- Runtime o codegen mas alla del evaluador parcial.

## TODOs y FIXMEs destacados

- `src/axis/syn/parsing.py:226`: warnings de parsing en vez de errores.
- `src/axis/syn/outline.py:76`: verificar unicidad de keywords.
- `src/axis/expr/tuple_.py:201`: cached_property re-lanzar error.
- `packages/protobase/src/protobase/record.py:57`: attrs que participan en hash.
- `packages/protobase/src/protobase/object.py:318` y `:391`.

## Proximos pasos sugeridos

### Corto plazo

- Reparar el crash en `Err.diagnostic`.
- Eliminar el `except Exception` silencioso.
- Restaurar el encadenamiento de excepciones en `Report`.
- Remover debug prints e imports no usados.
- Limpiar el codigo comentado (vive en git history).

### Mediano plazo

- Implementar evaluacion de `Apply` y `Member`.
- Activar contribuciones de `Mod` y `QualDef`.
- Agregar tests a `Scope`, `Entity`, `Realm`, `Outline` y `Report`.
- Implementar `Comparison`/`Logic`/`Range`/`Cast`.
- Rehabilitar `ImplBucket` y `CastDef`.

### Largo plazo

- Motor de inferencia de tipos y resolucion de sobrecargas.
- Implementacion real de la biblioteca estandar.
- If-expressions y soporte completo de scope.
- CI/CD, linting y formateo automatico.
