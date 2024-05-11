# Pattern maching is dispatching.


## Optimization

Dado el conjunto de soluciones 'S' donde cada solucion es definida por un conjunto de condiciones 'C'. Se puede definir un algoritmo por el cual comprobar si T tiene solucion en S practicando una busqueda en un arbol binario del conjunto de condiciones.


```axis

match v:
	v: Iter[Item=Natural] -> "solution 1"
	v: Iter[Item=Real] -> "solution 2"
	v: Array[:,:] Real -> "solution 3"


```



Aproximacion 1: A cada condicion se le asigna un peso igualal numero de soluciones que la requieren para ser evaluada*

*: hay condiciones que pueden ser mas generales y confirmar otras condiciones por ejeplo si N < 10 y existen

Aproximacion 2: A cada solucion se le asigna un peso en funcion de la frecuencia en la aparicion como resultado de busqueda**

**: se puede tener en cuenta el resultado negativo a la hora de asignar un peso



*Manejo de ambiguedad*
