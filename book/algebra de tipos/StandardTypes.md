# Standard Types

## Building blocks

Los principales componentes del sistema de algebra de tipos:

Tipos básicos: Bit, Array, Tuple

Operadores: Conjunto, Mapa




def **Bit**: one binary digit

def **Byte: 8 Bit**

```
4 Byte == [4, 8] Bit
4 Byte != 32 Bit
```


## Unit

Los tipos unitarios, corresponden a los arreglos de orden 0, cadecen de las propiedades de los arreglos, cuando un arreglo tiene orden 0 se anula 

**Tuple**: Un tuple agrupa un conjunto de valores en un cocepto unitario. La uniformidad de los valores es un aspecto interesante

**Escalar**

**Shape** indica la forma de un array

**Range**

**Pair**

## Array

Los arreglos son un protocolo de abstraccion para conjuntos de datos.

**List** es un tipo de array de orden 1. Una lista de numeros es un **Vector**

Para definir un array se puede utilizar un cualificador numérico  `[3,3] Real.`

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

## Contenedores

**Array** todas las formas de arreglos son contenedores

**Set** los conjuntos son contenedores de datos unicos no repetidos e inmutables.

**Map** los mapeos son asociaciones de los elementos de un **Set** con una **List**a de valores. Un mapeo tiene caracteristicas comunes entre ambos contenedores, posee orden como la lista, inmutabilidad de la clave y mutabilidad del valor. `Map[Date] Number`

## Texto

Un **Text**o opera como un tipo unitario (que no atomico) que contiene una lista de elementos atomicos (carácteres, **Glyph** o tokens).

**Date**, **Time** y **DateTime**: el formato de texto de fecha y tiempo en diferentes especificaciones.

**Slug** texto que solo permite minusculas y guiones
