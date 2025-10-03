un array o escalar en realidad siempre tienen infinitas (por la izquierda y por la derecha, o con cualquier nombre) dimensiones a 1

dimensiones nominales:
```axis


# tiempo, espacio, energia ---------↓
val e: Array[;t, s:(x:0,y:1,z:2) v:(e:_) ;] Real = (..)

# tiempo, espacio, masa ------------↓
val m: Array[;t, s:(x:0,y:1,z:2) v:(m:_) ;] Real = (..)


```




ninguna dimension puede ser inferior a 1, el resutlado de una 
operacion que arroje un array con alguna dimension del tamaño 
0 seria traducido a None

