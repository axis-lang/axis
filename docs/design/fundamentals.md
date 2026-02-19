# Fundamentos

## Omision predecible
Gran parte de los fundamentos en el diseno de AXIS explotan el comportamiento implicito de las reglas que conforman el lenguaje. AXIS suele omitir las abstracciones para que la lectoescritura del codigo haga mas evidente el "que" que el "como". Es caracteristica general por ejemplo la omision de los tipos de referencia. Permitiendo la escritura de codigo de manera generalizada (codigo generico) que de forma automatica (predecible) sera adaptado al caso particular de cada uso.

AXIS, como lenguaje de programacion, oculta bajo el capo el andamiaje, dejando ver objeto que pretende implementar.

Que puede ocultar axis bajo el capo?

- generadores
- asincronia
- indirecciones: Referencias, Arrays
- paralelismo

Como oculta axis el andamiaje?

-
- ...

## Optimizacion automatica desde la generalizacion
En el diseno de AXIS se busca hacer que el codigo sea generalizable, asumiendo que un codigo generalizable es potencialmente codigo mas reusable. Por ejemplo, el alojamiento, liberacion y trackeo de objetos permite seleccionar el mecanismo de alojamiento adecuado (stack o heap) para un objeto en tiempo de compilacion. En el codigo, de forma general, no quedara explicitado si un objeto debe alojarse en la pila y en el heap, el programador puede tratar todos los objetos como objetos heap pero el compilador puede decidir apilar objetos como un metodo de optimizacion.

## Arrays y dimensiones nominales
Un array o escalar en realidad siempre tienen infinitas (por la izquierda y por la derecha, o con cualquier nombre) dimensiones a 1.

Dimensiones nominales:

```axis


# tiempo, espacio, energia ---------↓
val e: Array[;t, s:(x:0,y:1,z:2) v:(e:_) ;] Real = (..)

# tiempo, espacio, masa ------------↓
val m: Array[;t, s:(x:0,y:1,z:2) v:(m:_) ;] Real = (..)


```

Ninguna dimension puede ser inferior a 1, el resutlado de una operacion que arroje un array con alguna dimension del tamano 0 seria traducido a None.
