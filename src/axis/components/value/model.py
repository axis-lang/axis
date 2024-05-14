"""
Filosofia:


VALUE = List Natural(0..10) = (1,2,3,4)

Compmosicion de tipos:
 Array[:,:] Shared Natural -> A B C -> A(B(C)):
    A: Array[:,:]
    B: Shared
    C: Natural



Dominio del objeto de un valor:
    v: 0..9

    type_of(v) -> Natural
    object_of(v) -> Range(0, 9)
    domain_of(v) -> ({Natural}: Range[Natural](0, 9)) # dado que un rango es un dominio

    shape_of(V) -> [] ->  Scalar





un objeto es un named tuple que puede tener un cualificador T? (a:1,b,c, ..)
un cualificador de objeto es un tipo T(a,b,c)
el objeto de un valor puede tener un dominio: 0..100 o ("manzana", "lima", "pera")

generalmente un valor es definido por un objeto



el objeto es la cualidad esencial ultima del valor,
un valor no es un objeto, un objeto (es una cualidad del



FORMA:



#

# Valor

propiedades:
    - domain
        - morphology (shape and access)
        - layout (type and content)
    - lifetime (grafo?)
    - view of other values (alias)


Constante (access qualifier)


Variable (access qualifier)



def Range[T]:
    T: Ordered
    start: T
    end: T



"""

from protobase import Object, traits


# Value, Variable y Constant son siempre traits?


class Value(Object, traits.Basic):
    ...
    # shape
    # tuple
    # type
    # domain for constant = self


class Constant(Value): ...


class Variable(Value): ...


class Type(Constant): ...


class Domain(Constant): ...
