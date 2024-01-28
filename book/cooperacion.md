# Cooperacion

La cooperacion cimienta las funcionalidades de corutinas, programacion asincrona y los paradigmas de inversion del flujo de control.

Definicion de una corutina

```rust
fn my_generator(param: Natural) -> Natural :
	for n in 0..10:
		let x <- (param + n) swap_point2; // coop swap point
	return 10
```

Contianucion en multiples ramas

```rust
fn multibranch(x: Natural):
	match <- x + 1 {
		(x: Natural) => {
		}
		(x: Natural, y: Natural) => {
		}
	}

m = maultibranch(68)
m()


```

## Inversion del flujo de control

La adopcion de la cooperacion como una caracteristica fundamental en AXIS conlleva tres efectos directos importantes en su diseño:

1. Interfaces mutantes: Al adaptar el algebra de tipos para poder cubrir todos los casos de cooperatividad, encontramos que una corutina varia el tipado en funcion del tipado de entrada y salida del punto de intercambio. Analisis del flujo de ejecucion.
2. Polimorfismo: El algebra de datos debe soportar el modelado de los estados de las corutinas. Y este debe ser compatible con la recurrencia (subrutinas que se llaman a sí mismas), el flujo dinamico (llamadas por indireccion) y la cooperacion en funciones anidadas.
3. La fragmentacion de funciones: El lowering del codigo cooperativo a codigo no cooperativo implica romper las funciones en pedazos.

Del tercer efecto directo se deriva un cuarto y un quinto efecto colateral:

4. Estado fuera de la pila: El estado de la corutina se debe almacenar de forma independiente de la pila, pudiendo generar una pila de estados paralela cuando se trata de cooperacion anidada. esta característica mueve al heap gran parte del volumen de datos. Una vez mas, el uso de la pila es una optimizacion desde la generalizacion.
5. Nuevos mecanismos de debuging: La existencia de una pila paralela de estados anidados para las corutinas, hace que el proceso de debuging.
