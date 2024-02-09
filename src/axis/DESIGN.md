# DESIGN

## Front

SRC --> AST (Parsing)

* Primary Sytax check

**AST --> CST** 

* Syntax Check
* Name resolution
* Macro Expansion

## IR

**CST --> RSVDG**

---

El motor de AXIS se establece en este punto, los datos estan procesados y la magia esta lista para ocurrir.

Plugins:

* Language server
* Interactive REPL
* JIT

---

## Back

**RSVDG --> CFG**
