# Overview

## Estado actual

- Parser, AST y semantica base implementados.
- Resolucion de nombres y entidades por anchor.
- Evaluador parcial con literales y operadores aritmeticos basicos.
- TUI opcional para inspeccion (Textual).
- Pendiente: `Apply`, `Index`, `Member` en evaluacion.

## Componentes principales

- `src/axis/syn`: gramatica ANTLR y construccion de AST.
- `src/axis/items`: items y defs que emiten contribuciones.
- `src/axis/sem`: realm, entity y scope.
- `src/axis/dom`: valores, tipos y estructuras.
- `src/axis/val`: evaluador parcial.
- `src/axis/src`: fuentes, IO y watchers.
- `src/axis/tui`: interfaz textual.

## Ejemplos

El directorio `codebase` contiene ejemplos del lenguaje (por ejemplo,
`codebase/sandbox` y `codebase/std.core`).
