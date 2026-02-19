# Sistema de tipos y cualificadores

## Tipos y cualificadores

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

- `..$Q Natural` capturara los cualificadores de Natural de forma analoga a como lo haria `Vector $T` con los tipos interiores.

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

## Standard Types

### Building blocks
Los principales componentes del sistema de algebra de tipos:

Tipos basicos: Bit, Array, Tuple

Operadores: Conjunto, Mapa



def **Bit**: one binary digit

def **Byte: 8 Bit**

```
4 Byte == [4, 8] Bit
4 Byte != 32 Bit
```

### Unit
Los tipos unitarios, corresponden a los arreglos de orden 0, cadecen de las propiedades de los arreglos, cuando un arreglo tiene orden 0 se anula 

**Tuple**: Un tuple agrupa un conjunto de valores en un cocepto unitario. La uniformidad de los valores es un aspecto interesante

**Escalar**

**Shape** indica la forma de un array

**Range**

**Pair**

### Array
Los arreglos son un protocolo de abstraccion para conjuntos de datos.

**List** es un tipo de array de orden 1. Una lista de numeros es un **Vector**

Para definir un array se puede utilizar un cualificador numerico  `[3,3] Real.`

**Atencion** a los arrays de referencias: `[..] Iterator` siendo iterator un protocolo (un fat pointer) podriamos llamar a varios iteradores a la vez (y en paralelo) utilizando arrays, siendo los arrays perfectos paralelizadores uniformes.

**Shapes:** 

`[:]` Lista o Vector de n elementos

`[:,:]` Matriz

`[..]` array (posible orden 0 implicado, indireccion/referencia)

`[:,..]` array

`[]` indireccion: un array de orden  0 representa una referencia o


Number permite la aplicacion de operaciones aritmeticas.

**Scalar** abstrae los tipos de numeros de orden 0. Son escalares los valores del tipo **Boolean(bit)**, **Natural(n8, n16, n32, n64, n128)**, **Integer(i8, i16, i32, i64, i128)**, **Real(f16, f32)** y **Complex**. Scalar no es un array sino un tipo unitario.

**Vector** es un array numerico de orden 1

**Matrix** es un array numerico de orden 2

**Tensor** es un array numerico de orden superior a 2 o desconocido

### Contenedores
**Array** todas las formas de arreglos son contenedores

**Set** los conjuntos son contenedores de datos unicos no repetidos e inmutables.

**Map** los mapeos son asociaciones de los elementos de un **Set** con una **List**a de valores. Un mapeo tiene caracteristicas comunes entre ambos contenedores, posee orden como la lista, inmutabilidad de la clave y mutabilidad del valor. `Map[Date] Number`

### Texto
Un **Text**o opera como un tipo unitario (que no atomico) que contiene una lista de elementos atomicos (caracteres, **Glyph** o tokens).

**Date**, **Time** y **DateTime**: el formato de texto de fecha y tiempo en diferentes especificaciones.

**Slug** texto que solo permite minusculas y guiones

## Captura con enmascaramiento
El tipo `Mut Bijection Matrix[4, 4] Complex` puede ser capturado por:

* `Complex`
* `Matrix Complex`
* `Var .. Complex`
* `Bijection .. Complex`
* `Matrix[4, $N] Number`

```
DEF 

FUNCTION
::name fft_inplace
::doc
	Funcion foo
::param
	value: Bijection[Nat] N
::where
	W: Nat
	H: Nat
	N: Number
::body

```
