# Tipos y cualificadores

```

def None = 
def Optional $T = $T | None
```

### Propagation throught qualifiers

La propagacion a traves de los tipos cualificantes invierte el control del flujo del programa de forma omitida pero predecible.

La sintaxis especial de los qualificadores facilita logica y mentalmente la propagacion a traves de los mismos. De esta forma podemos generalizar las operaciones de mapeo.

```rust
// definimos una operacion binaria en el dominio real
fn add(l: Real, r: Real) -> Real {...}

// creamos contenedores de datos a traves de cualificadores como Array o Map
let array: Array[] Real = (1, 2, 3)
let map: Map[Text] Real = (a: 1, b: 2, c: 3)

// Propagamos la operacion suma a traves de los cualificadores Array y Map
let array_sum: Array Real = add(array, array)
let map_sum: Map[Text] Real = add(map, map)

```


```rust
// la funcion print recibe un valor de texto
fn print(txt: Text) { ... }

// definimos un valor opcional con un texto
let optional_text: Option Text = "brother";
let no_text: Option Text = None;

// Print solo sera ejecutado si optional_text tiene valor
print(optional_text) // imprime "Hey brother"
print(no_text) // no invoca la funcion

// con valores de retorno:
fn append_hey(txt: Text) { ... }
append_hey(optional_text) // "Hey brother"
append_hey(no_text) // None
```


La sintaxis de cualificadores permite al motor logico de axis adentrarse en las construcciones algebraicas de tipos interiores omitiendo los tipos exteriores:

- `Ref Natural` es propagable a `.. Natural`
- `Array Real` es propagable a `.. Real`

Tambien permite la captura de tipos exteriores a traves de variables logicas.

- `..$Q Natural` capturará los cualificadores de Natural de forma analoga a como lo haria `Vector $T` con los tipos interiores.

## Mecanismos de propagacion

***Propagar aplicacion***

En el ejemplo anterior propagamos la aplicacion de la funcion add sobre un cojunto de tipos cualificados.

Algoritmo:

1. se hacen coincidir los cualificadores entre los parametros y el argumento de la funcion, de interior a exterior.
2. desde el primer cualificador hasta el punto de no coincidencia se establece un mecanismo de propagacion que consiste en:
3. 

Pseudo codigo de como implementar la propagacion de aplicaciones

```python
def apply_propagation[T](...params: ..T, fn: Callable[[T]]):
	for 

```

```rust
let a: Array Optional Real
let b: Array Real

let c: Array Optional Real = sum(a, b)
```
