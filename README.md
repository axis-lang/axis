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
