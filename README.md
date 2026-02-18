# AXIS (POC of a new programming language)

* [IM]([https://docs.rs/im/latest/im/]())
* [internment](https://docs.rs/internment/latest/internment/index.html)
* [oxide rsvdg](https://github.com/feroldi/oxide/blob/master/src/rvsdg.rs)

**Initial targets**

- [ ] basic functionality:
  - [ ] def functions
  - [ ] calling functions with args
  - [ ] basic statements
  - [ ] basic types
- [ ] arithmetic operators: implement a function dispatch for arithmetic operators
  - [ ] n dim tensor data type as generic (impls can be diverse)
  - [ ] einops expressions
- [ ] imports
- [ ] deref: a generic function implementation can return a value

**Traits**

- negative logic: Tensor extends(Numeric, !Scalar) un tensor es numerico y no es un escalar

# Estructura de archivos

* Packages: Librerias transversales a los modulos de axis
* Submodule: modulos que componen el sistema

# Notas de build

- El grammar y los generados viven en `src/axis/syn/grammar/`; para regenerar: `just gen-parser`.
- `protobase` es parte interna del ecosistema y vive en `src/protobase` (no es paquete independiente por ahora).

# Resumen de archivos (src/axis)

**Funcionales (núcleo activo)**

- `src/axis/dom/`: modelos base (Meta/Val, Tuple/Index/Shape, Map)
- `src/axis/expr/`: nodos de expresión + matcher/reifier
- `src/axis/syn/`: AST, parser/builder, outline, grammar ANTLR
- `src/axis/sem/`: scope, binding, package/index
- `src/axis/items/`: parseo de items, bloques y paquetes
- `src/axis/val/`: evaluador y tipos/valores base
- `src/axis/src/`: utilidades de archivo/span
- `src/axis/log/`: diagnósticos
- `src/axis/core/`: contexto e índices clave

**Borradores / POC (candidatos a limpieza)**

- `src/axis/__main__.py`: script demo ad-hoc
- `src/axis/core/db.py`: stubs vacíos
- `src/axis/core/index.py`: placeholder de índice
- `src/axis/dom/array.py`: nota/docstring
- `src/axis/sem/__init__.py`: imports comentados
- `src/axis/sem/abstract.py`: diseño en borrador
- `src/axis/val/matching.py`: API sin implementar
- `src/axis/val/unification.py`: API sin implementar
- `src/axis/val/type.py`: notas de álgebra de tipos
- `src/axis/val/ref.py`: stub con implementación comentada
