# Fundamentos de diseño

## Omision predecible

Gran parte de los fundamentos en el diseño de AXIS explotan el comportamiento implicito de las reglas que conforman el lenguaje. AXIS suele omitir las abstracciones para que la lectoescritura del codigo haga mas evidente el 'qué' que el 'como'. Es caracteristica general por ejemplo la omision de los tipos de referencia. Permitiendo la escritura de codigo de manera generalizada (codigo generico) que de forma automatica (predecible) será adaptado al caso particular de cada uso.

AXIS, como lenguaje de programacion, oculta bajo el capó el andamiaje, dejando ver objeto que pretende implementar.

¿Que puede ocultar axis bajo el capó?

- generadores
- asincronia
- indirecciones: Referencias, Arrays
- paralelismo

¿Como oculta axis el andamiaje?

- 
- ...

## Optimizacion automatica desde la generalizacion

En el diseño de AXIS se busca hacer que el codigo sea generalizable, asumiendo que un codigo generalizable es potencialmente codigo más reusable. Por ejemplo, el alojamiento, liberacion y trackeo de objetos permite seleccionar el mecanismo de alojamiento adecuado (stack o heap) para un objeto en tiempo de compilacion. En el codigo, de forma general, no quedará explicitado si un objeto debe alojarse en la pila y en el heap, el programador puede tratar todos los objetos como objetos heap pero el compilador puede decidir apilar objetos como un metodo de optimizacion.
