# Outline markup / Outline fs specification

Out line es un sistema de reglas (podriamos hablar de micro dsl) que permite
parsear la estructura de archivos de texto extrayendo informacion sobre la anidacion 
de bloques de bloques de texto. podria pensarse en outline como un analogo a xml.

Outline no trabaja solo, extrae bloques de texto plano desde los archivos de texto
extrayendo la estructura anidada para inyectar esa informacion en un sistema de 
procesamiento de texto (P.Ej un parser).

outline se ha diseñado para cumplir con las siguietes caracteristicas:
 - Facilidad de uso y sencillez
    - Facilidad de implementacion
    - Facilidad en su lecto escritura
- Flexibilidad
    - Permite definir reglas que regulan comportamiento de outline tanto a nivel 
    de sistema de archivos como a nivel de bloque de texto

El trabajo no outline comienza desde la estructura del propio sistema de archivos,
por lo que, deembos comenzar la especificacion de outline ya no nivel de archivo / bloque 
de texto, sino de una especificacion de como debe comportarse outline en el sistema de archivos.



```outline
div 
    class container
    id main
h1


        Esto es un comentario vinculado al emento div
class container


    h1 hola mundo
            Comentario vinculado al elemento H1
    p
        lorem ipsum dolor sit amet

```




```outline

fn alpha[T](a: int, b: int) -> int
    funcion que describe el comportamiento de un modulo
    y sus parametros

param a: int
        Parametro a


fn alpha(a: int = 10, b: int) -> int:
    funcion que describe el comportamiento de un modulo
    y sus parametros
    param a


fn alpha
    funcion que describe el comportamiento de un modulo
    y sus parametros

param a: int = 10
        Parametro a

param b: int
        Parametro b
    default 10

constraints:
    a > 10
    b < 10
    a + b < 10
    a * b < 100

-> int
    if a > 10
        b
    else:
        c
```