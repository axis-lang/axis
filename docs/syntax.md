# Syntax

Callable e indexable

indexable [Key]:> Value
callable (Arg1, Arg2, Arg3):> Value


## deestructuring Patterns

### Object destructuring

```ts
let obj = Object(alpha=1, beta=2, theta=3);

let Object(alpha=a, beta=b, theta=z) = obj;

if let Object(alpha=a, beta=b, ..) = obj {
    // ...
}

let a = Nat 10 // a es una variable de tipo Any inicializada a Nat 10
a = 1.4 // bien, ahora a es de tipo Any y su valor es 1.4

let a: Nat = 10 // a es una variable de tipo Nat inicializada a 10
a = 1.4 // error, a es de tipo Nat y no puede ser asignado un valor de tipo Float

let array1d: [:] Nat; // array es una variable de tipo Array unidimensional de Nat 
let array2d: [:, :] Nat; // array es una variable de tipo Array bidimensional de Nat
let arraynd: [..] Nat; // array es una variable de tipo Array de N dimensiones de Nat
let refrence: [] Nat; // refrence es una variable de tipo Reference a Nat

reference = [] 10 // bien, ahora reference es un Reference a Nat con valor 10
array1d = (1, 2, 3) // bien, ahora array1d es un Array unidimensional de Nat con valores 1, 2 y 3
array2d = ((1, 2), (3, 4)) // bien, ahora array2d es un Array bidimensional de Nat con valores [1, 2], [3 y 4]
arraynd = [..] 0 // bien, ahora arraynd es un Array de N dimensiones de Nat con valor 0

let a: .. = Map(String) Natural {
    "a": 1,
    "b": 2,
    "c": 3
}



if Nat(name=value < 10) = a {

}
if [a, .., z] Nat = Nat [1,2,3] {
    // a = 1, z = 3
}



```

```ts

```